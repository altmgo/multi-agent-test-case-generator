import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

import evaluation_cli
import main
from datasets import e2edev
from evaluation.embeddings import EmbeddingBatch
from schemas import UsageRecord


FIREFOX = "firefox_bookmarks"
E2EDEV = "e2edev_bench_01"
CALIBRATION = "e2edev_bench_02"
SOLUTIONS = ("one-shot", "GHL", "Multiagent")
MODEL = "gemini-3.5-flash-lite"
LOCAL_DATA = Path(__file__).resolve().parents[1] / "data" / "normalized"


def load_json(path):
    return json.loads(path.read_bytes())


def prepare_fixtures(root, normalized, monkeypatch):
    requirements, tests = root / "R-set.csv", root / "T-set.csv"
    requirements.write_text(
        "RequirementID;RequirementContent\n" + "".join(f"R-{i:03d};Requirement {i}\n" for i in range(1, 185)),
        encoding="utf-8",
    )
    tests.write_text(
        "TestCaseID;TestCaseContent\n" + "".join(f"TC-{i:03d};Firefox case {i}\n" for i in range(1, 185)),
        encoding="utf-8",
    )
    assert main.main(["prepare", "firefox", "--requirements", str(requirements), "--tests", str(tests),
                      "--output", str(normalized)]) == 0
    inventory = {}
    for index in ("01", "02"):
        file = root / "E2EDev_data" / f"E2ESD_Bench_{index}" / e2edev.ANNOTATION
        file.parent.mkdir(parents=True)
        file.write_text(json.dumps({"finegrained_rewith_test": {"1": {
            "requirement": {"description": "Open a document"},
            "test_cases": [{"test_case": ["Scenario: Open a document", "When I click Open",
                                          "Then a document opens"]}],
        }}}), encoding="utf-8")
        inventory[index] = hashlib.sha256(file.read_bytes()).hexdigest()
    monkeypatch.setattr(e2edev, "ANNOTATION_SHA256", inventory)
    assert main.main(["prepare", "e2edev", "--source", str(root), "--output", str(normalized)]) == 0


class FakeRuntime:
    def __init__(self, units):
        self.units = units
        self.usage_records = []
        self.calls = []

    async def run(self, stage, instructions, input, output_type, *, extra=None):
        original = self.units[input.unit_id]
        assert input.model_dump() == {"unit_id": original["id"], "requirements": original["requirements"]}
        self.calls.append((stage, input.unit_id, extra))
        self.usage_records.append(UsageRecord(input_tokens=7, output_tokens=2))
        if stage == "ghl_select_techniques":
            value = {"selections": [{"technique_id": "use_case", "rationale": "Test the main workflow."}]}
        elif stage == "multiagent_coverage":
            value = {"feedback": "One generated case."}
        else:
            value = {"cases": [{
                "id": "provider-id",
                "title": "Fixture title",
                "description": "Fixture description",
                "requirement_ids": [input.requirements[0].id],
            }]}
        return output_type.model_validate(value)


class FakeEmbedder:
    def embed(self, texts):
        # The single generated case matches the first reference. Other
        # references are orthogonal, so they stay outside the review.
        assert len(texts) >= 2 and "Fixture description" in texts[0]
        return EmbeddingBatch(
            [[1.0, 0.0], [1.0, 0.0]] + [[0.0, 1.0] for _ in texts[2:]],
            UsageRecord(input_tokens=len(texts)), request_count=1,
        )


@pytest.mark.parametrize("use_local_data", [False, True], ids=["prepared-fixtures", "prepared-real-units"])
def test_prepare_run_evaluate_review_and_rereview_all_solutions(tmp_path, monkeypatch, use_local_data):
    from human_review import main as review_main

    if use_local_data:
        data = LOCAL_DATA
        if not all((data / f"{name}.json").is_file() for name in (FIREFOX, E2EDEV, CALIBRATION)):
            pytest.skip("Local prepared Firefox and E2EDev datasets are unavailable")
    else:
        data = tmp_path / "data"
        prepare_fixtures(tmp_path, data, monkeypatch)
    units = {name: load_json(data / f"{name}.json") for name in (FIREFOX, E2EDEV, CALIBRATION)}
    results = tmp_path / "results"
    runtime = FakeRuntime(units)

    def fake_factory(model):
        assert model == MODEL
        return runtime

    monkeypatch.setattr(main, "make_runtime", fake_factory)
    monkeypatch.setattr(evaluation_cli, "make_embedder", FakeEmbedder)
    monkeypatch.setattr(main, "now", lambda: datetime(2026, 11, 9, 3, tzinfo=timezone.utc))
    assert main.main([
        "run", "--model", MODEL, "--solutions", *SOLUTIONS, "--units", FIREFOX, E2EDEV,
        "--agents", "coverage", "--calibration-units", CALIBRATION,
        "--data-dir", str(data), "--results-dir", str(results),
    ]) == 0
    run, = results.iterdir()
    config = json.loads((run / "configs.md").read_text(encoding="utf-8").split("```json\n")[1].split("\n```")[0])
    assert config["model"] == MODEL
    assert config["embedding_model"] == "gemini-embedding-2"
    assert config["similarity_threshold"] == 0.70
    assert config["output_modes"] == {solution: "batch" for solution in SOLUTIONS}
    assert config["calibration"]["unit_ids"] == [CALIBRATION]
    assert CALIBRATION not in {unit_id for _, unit_id, _ in runtime.calls}
    coverage = {unit_id: extra for stage, unit_id, extra in runtime.calls if stage == "multiagent_coverage"}
    assert "calibration_profile" not in coverage[FIREFOX]
    assert coverage[E2EDEV]["calibration_profile"] == config["calibration"]["aggregate"]
    assert set(coverage[E2EDEV]["calibration_profile"]) == {"requirement_count", "histogram", "quartiles"}

    comparison_path = run / "comparison.json"
    assert not comparison_path.exists()
    generated = {}
    for solution in SOLUTIONS:
        for name in (FIREFOX, E2EDEV):
            artifact = run / solution / name / "results.json"
            snapshot = load_json(artifact)
            assert snapshot["status"] == "generated"
            assert snapshot["evaluation"] is None
            assert snapshot["usage"]["embedding_requests"] == 0
            generated[artifact] = snapshot
    generation_files = {
        path: path.read_bytes() for path in run.rglob("*")
        if path.is_file() and path.name not in {"configs.md", "results.json", "results.csv", "semantic_matches.json"}
    }
    generation_calls = list(runtime.calls)
    assert evaluation_cli.main(["--results-dir", str(results), "--run", run.name]) == 0
    assert runtime.calls == generation_calls
    assert all(path.read_bytes() == content for path, content in generation_files.items())
    for artifact, snapshot in generated.items():
        evaluated = load_json(artifact)
        for key in ("requirements", "generated_cases", "reference_cases", "generation", "links", "artifacts"):
            assert evaluated[key] == snapshot[key]
        for key in ("generation", "generation_attempts", "generation_calls"):
            assert evaluated["usage"][key] == snapshot["usage"][key]
    original_comparison = comparison_path.read_bytes()
    comparison = json.loads(original_comparison)
    assert comparison["unit_ids"] == [E2EDEV, FIREFOX]
    for solution in SOLUTIONS:
        assert comparison["metrics"][solution]["match_count"] == 2
        for name in (FIREFOX, E2EDEV):
            directory = run / solution / name
            artifact = directory / "results.json"
            automatic = load_json(artifact)["evaluation"]
            pair, = automatic["matches"]
            csv_path = directory / "results.csv"
            csv_before = csv_path.read_bytes()
            with csv_path.open(newline="", encoding="utf-8") as stream:
                row, = csv.DictReader(stream)
            assert row["status"] == "evaluated"
            assert (row["match_count"], row["precision"]) == ("1", "1.0")
            references = len(units[name]["reference_cases"])
            assert float(row["recall"]) == 1 / references

            args = ["--results-dir", str(results), "--run", run.name, "--solution", solution, "--unit", name]
            replies = iter(["equivalent", "", "y"])
            monkeypatch.setattr("builtins.input", lambda _: next(replies))
            assert review_main(args) == 0
            first = load_json(artifact)["human_evaluation"]
            assert first["precision"] == 1
            assert first["recall"] == 1 / references
            assert first["decisions"] == [{
                "generated_id": pair["generated_id"], "reference_id": pair["reference_id"],
                "verdict": "equivalent", "justification": "",
            }]

            replies = iter(["y", "different", "Different workflow", "y"])
            assert review_main(args) == 0
            revised = load_json(artifact)
            assert revised["human_evaluation"]["precision"] == 0
            assert revised["human_evaluation_history"] == [first]
            assert revised["evaluation"] == automatic
            assert csv_path.read_bytes() == csv_before
    assert comparison_path.read_bytes() == original_comparison
