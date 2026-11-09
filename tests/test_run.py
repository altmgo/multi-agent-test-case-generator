import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from datasets.e2edev import SOURCE_COMMIT
from evaluation.embeddings import EmbeddingBatch, EmbeddingError
from schemas import GeneratedCase, GenerationResult, ReferenceCase, Requirement, Unit, UsageRecord


MODEL = "gemini-3.5-flash-lite"
SECRET = "synthetic-provider-key-that-must-not-leak"
E2EDEV = "e2edev_bench_01"
CALIBRATION = "e2edev_bench_02"
FIREFOX = "firefox_bookmarks"


def make_unit(unit_id, *, reference=True):
    return Unit(
        id=unit_id,
        requirements=[
            Requirement(id="R1", text="Open a document", language="en", source="fixture"),
            Requirement(id="R2", text="Close the document", language="en", source="fixture"),
            Requirement(id="R3", text="Confirm deletion", language="en", source="fixture"),
        ],
        reference_cases=[
            ReferenceCase(
                id="TC1", title="Open document", description="The document opens.",
                requirement_ids=["R1"], source="fixture", link_method="annotated", link_status="confirmed",
            )
        ] if reference else [],
    )


def put(data, unit):
    path = data / f"{unit.id}.json"
    path.write_text(unit.model_dump_json(), encoding="utf-8")
    return path


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def config(run):
    return json.loads((run / "configs.md").read_text(encoding="utf-8").split("```json\n")[1].split("\n```")[0])


def csv_row(unit_dir):
    with (unit_dir / "results.csv").open(newline="", encoding="utf-8") as stream:
        row, = csv.DictReader(stream)
    return row


class FakeRuntime:
    def __init__(self, respond):
        self.respond = respond
        self.calls = []
        self.usage_records = []

    async def run(self, stage, instructions, input, output_type, *, extra=None):
        assert len(input.requirements) == 3
        assert "reference_cases" not in input.model_dump()
        self.calls.append((stage, input.unit_id, extra))
        self.usage_records.append(UsageRecord(input_tokens=2, output_tokens=3))
        return output_type.model_validate(self.respond(stage, input.unit_id, extra))


class FakeEmbedder:
    def __init__(self):
        self.fail_next = False

    def embed(self, texts):
        if self.fail_next:
            self.fail_next = False
            raise EmbeddingError(SECRET, usage=UsageRecord(input_tokens=9), request_count=1)
        return EmbeddingBatch(
            [[1.0, 0.0] for _ in texts], UsageRecord(input_tokens=7), request_count=1
        )


def response(stage, unit_id, extra):
    if stage == "ghl_select_techniques":
        return {"selections": [{"technique_id": "use_case", "rationale": "A workflow"}]}
    if stage == "multiagent_analyst":
        return {"analysis": "All requirements reviewed"}
    if stage in {"multiagent_critic", "multiagent_validator"}:
        return {"feedback": "Clear", "request_revision": False, "confirmed_blockers": []}
    if stage == "multiagent_coverage":
        return {"feedback": "Add more negative cases"}
    links = [extra["target"]] if extra["output_mode"] != "batch" else ["R1", "R2", "R1"]
    return {"cases": [
        {"id": "provider-id", "title": "../Open document", "description": "The document opens.", "requirement_ids": links}
    ]}


@pytest.fixture
def cli(tmp_path, monkeypatch):
    import main as cli_module

    data, runs = tmp_path / "data", tmp_path / "results"
    data.mkdir()
    runtime = FakeRuntime(response)
    embedder = FakeEmbedder()
    monkeypatch.setattr(cli_module, "make_runtime", lambda _: runtime)
    monkeypatch.setattr(cli_module, "make_embedder", lambda: embedder)

    def run(*options):
        return cli_module.main([
            "run", "--model", MODEL, "--data-dir", str(data), "--results-dir", str(runs),
            *options,
        ])

    return cli_module, data, runs, runtime, embedder, run


def test_timestamp_collision_waits_before_factory_and_leaves_existing_run_intact(cli, monkeypatch):
    module, data, runs, runtime, _, run = cli
    put(data, make_unit(FIREFOX))
    occupied = runs / "2026-11-08_23-59-59"
    occupied.mkdir(parents=True)
    sentinel = occupied / "configs.md"
    sentinel.write_text("earlier run", encoding="utf-8")
    ticks = iter([
        datetime(2026, 11, 9, 2, 59, 59, 950000, tzinfo=timezone.utc),
        datetime(2026, 11, 9, 3, 0, 0, tzinfo=timezone.utc),
    ])
    monkeypatch.setattr(module, "now", lambda: next(ticks))

    def start(_):
        assert (runs / "2026-11-09_00-00-00" / "configs.md").is_file()
        return runtime

    monkeypatch.setattr(module, "make_runtime", start)
    assert run("--solutions", "one-shot", "--units", FIREFOX) == 0
    assert sentinel.read_text(encoding="utf-8") == "earlier run"
    created = config(runs / "2026-11-09_00-00-00")
    assert created["reserved_at"] == "2026-11-09T00:00:00-03:00"
    assert created["timezone"] == "America/Recife"
    assert len(runtime.calls) == 1


def test_persisted_snapshots_and_index_count_a_multi_linked_case_once(cli, monkeypatch):
    _, data, runs, _, _, run = cli
    unit = make_unit(FIREFOX)
    source = put(data, unit)
    expected_sha = hashlib.sha256(source.read_bytes()).hexdigest()
    monkeypatch.setenv("GOOGLE_API_KEY", SECRET)
    assert run("--solutions", "one-shot", "--datasets", "firefox") == 0
    execution, = runs.iterdir()
    solution = execution / "one-shot"
    unit_dir = solution / FIREFOX
    assert sorted(p.name for p in execution.iterdir() if p.is_dir()) == ["one-shot"]
    assert (unit_dir / "R3" / "requirement.md").is_file()
    assert list((unit_dir / "R3" / "test cases").iterdir()) == []
    assert (unit_dir / "R1" / "test cases" / "1_Open_document.md").is_file()
    assert (unit_dir / "R2" / "test cases" / "1_Open_document.md").is_file()
    assert (solution / "requirements_to_tests.md").read_text().count("G-001") == 1
    source.unlink()
    result = read_json(unit_dir / "results.json")
    assert result["schema_version"] == 1
    assert result["requirements"] == [item.model_dump() for item in unit.requirements]
    assert result["reference_cases"] == [item.model_dump() for item in unit.reference_cases]
    assert result["generated_cases"][0]["title"] == "../Open document"
    assert result["evaluation"]["matches"] == [{"generated_id": "G-001", "reference_id": "TC1", "similarity": 1.0}]
    assert read_json(unit_dir / "semantic_matches.json")["matches"] == result["evaluation"]["matches"]
    assert set(result["links"]["cases"]["G-001"]) == {"R1", "R2"}
    row = csv_row(unit_dir)
    assert row["generated_count"] == row["match_count"] == "1"
    assert row["tokens_used"] == "5"
    assert row["precision"] == row["recall"] == row["f1"] == "1.0"
    assert config(execution)["units"][FIREFOX]["sha256"] == expected_sha
    assert config(execution)["credential"]["present"] is True
    assert SECRET not in (execution / "configs.md").read_text()


def test_units_continue_after_generation_and_embedding_failures(cli):
    _, data, runs, runtime, embedder, run = cli
    for unit_id in (E2EDEV, CALIBRATION, FIREFOX):
        put(data, make_unit(unit_id))
    embedder.fail_next = True

    def scripted(stage, unit_id, extra):
        if unit_id == FIREFOX and stage == "multiagent_critic":
            raise ValueError(SECRET)
        return response(stage, unit_id, extra)

    runtime.respond = scripted
    assert run("--solutions", "multiagent", "one-shot", "--units", FIREFOX, E2EDEV, CALIBRATION,
               "--agents", "critic") == 1
    execution, = runs.iterdir()
    multi = execution / "Multiagent"
    generation_failure = multi / FIREFOX
    partial = read_json(generation_failure / "results.json")
    assert partial["failure"] == {"stage": "critic", "error_type": "ValueError"}
    assert partial["status"] == "failed"
    assert partial["evaluation"] is None
    assert len(partial["generated_cases"]) == 1
    assert partial["usage"]["generation"]["input_tokens"] == 4
    assert csv_row(generation_failure)["tokens_used"] == "10"
    assert read_json(generation_failure / "intermediate" / "trace.json")["status"] == "failed"
    assert read_json(generation_failure / "intermediate" / "initial.json")["assessment"]["cases"][0]["id"] == "G-001"

    embedding_failure = multi / E2EDEV
    failed = read_json(embedding_failure / "results.json")
    assert failed["failure"] == {"stage": "evaluation", "error_type": "EmbeddingError"}
    assert failed["usage"]["embedding"]["input_tokens"] == 9
    assert failed["usage"]["embedding_requests"] == 1
    assert csv_row(embedding_failure)["precision"] == ""
    assert read_json(multi / CALIBRATION / "results.json")["status"] == "evaluated"
    assert read_json(execution / "one-shot" / FIREFOX / "results.json")["status"] == "evaluated"
    comparison = read_json(execution / "comparison.json")
    assert comparison["unit_ids"] == [CALIBRATION]
    assert comparison["coverage"] == 1 / 3
    assert comparison["metrics"]["one-shot"]["generated_count"] == 1
    assert config(execution)["status"] == "partial"
    assert all(SECRET not in file.read_text() for file in execution.rglob("*") if file.is_file())


def test_three_attempts_and_round_decision_are_saved(cli):
    _, data, runs, runtime, _, run = cli
    put(data, make_unit(FIREFOX))

    def scripted(stage, unit_id, extra):
        if stage == "multiagent_critic":
            return {"feedback": "Retry", "request_revision": True, "confirmed_blockers": ["Same blocker"]}
        return response(stage, unit_id, extra)

    runtime.respond = scripted
    assert run("--solutions", "Multiagent", "--units", FIREFOX, "--agents", "analyst", "critic") == 0
    execution, = runs.iterdir()
    intermediate = execution / "Multiagent" / FIREFOX / "intermediate"
    revision = intermediate / "round_001"
    assert [read_json(revision / f"attempt_{i}.json")["assessment"]["candidate_id"] for i in (1, 2, 3)] == [
        "round-1-candidate-1", "round-1-candidate-2", "round-1-candidate-3"
    ]
    assert read_json(revision / "decision.json")["selected_id"] == "initial"
    assert read_json(intermediate / "trace.json")["rounds"][0]["decision"] == "preserved"


def test_calibration_is_disjoint_and_only_reaches_e2edev_coverage(cli):
    _, data, runs, runtime, _, run = cli
    for unit_id in (E2EDEV, CALIBRATION, FIREFOX):
        put(data, make_unit(unit_id))
    options = ("--solutions", "Multiagent", "--units", E2EDEV, FIREFOX, "--agents", "coverage")
    with pytest.raises(SystemExit) as error:
        run(*options, "--calibration-units", E2EDEV)
    assert error.value.code == 2
    assert not runs.exists()
    assert not runtime.calls

    assert run(*options, "--calibration-units", CALIBRATION) == 0
    coverage = {unit_id: extra for stage, unit_id, extra in runtime.calls if stage == "multiagent_coverage"}
    assert "calibration_profile" not in coverage[FIREFOX]
    assert coverage[E2EDEV]["calibration_profile"] == {
        "requirement_count": 3, "histogram": {"0": 2, "1": 1},
        "quartiles": {"q1": 0.0, "median": 0.0, "q3": 0.5},
    }
    assert CALIBRATION not in json.dumps(runtime.calls)
    execution, = runs.iterdir()
    assert config(execution)["calibration"]["unit_ids"] == [CALIBRATION]


@pytest.mark.parametrize("mode", ["per_requirement", "per_case"])
def test_scoped_modes_leave_one_shot_as_one_batch(cli, mode):
    _, data, runs, runtime, _, run = cli
    put(data, make_unit(FIREFOX))
    assert run("--solutions", "One-shot", "ghl", "multiagent", "--units", FIREFOX,
               "--agents", "--output-mode", mode) == 0
    assert [extra["output_mode"] for stage, _, extra in runtime.calls if stage == "one_shot"] == ["batch"]
    assert [(extra["output_mode"], extra["target"]) for stage, _, extra in runtime.calls if stage.startswith("ghl_generate")] == [
        (mode, "R1"), (mode, "R2"), (mode, "R3")
    ]
    assert [(extra["output_mode"], extra["target"]) for stage, _, extra in runtime.calls if stage == "multiagent_generator"] == [
        (mode, "R1"), (mode, "R2"), (mode, "R3")
    ]
    assert {stage for stage, _, _ in runtime.calls} == {
        "one_shot", "ghl_select_techniques", "ghl_generate_use_case", "multiagent_generator"
    }


def test_non_evaluable_unit_preserves_counts_without_joining_comparison(cli):
    _, data, runs, _, _, run = cli
    put(data, make_unit(E2EDEV, reference=False))
    assert run("--solutions", "one-shot", "--units", E2EDEV) == 0
    execution, = runs.iterdir()
    unit_dir = execution / "one-shot" / E2EDEV
    assert csv_row(unit_dir)["status"] == "not_evaluable"
    assert csv_row(unit_dir)["precision"] == ""
    assert csv_row(unit_dir)["embedding_requests"] == "0"
    assert read_json(execution / "comparison.json")["unit_ids"] == []


@pytest.mark.parametrize("unit_id", ["firefox_legacy", "firefox_../../other", "unknown"])
def test_legacy_unknown_and_traversal_unit_ids_are_rejected(cli, unit_id):
    _, data, runs, runtime, _, run = cli
    put(data, make_unit("firefox_legacy"))
    with pytest.raises(SystemExit) as error:
        run("--solutions", "one-shot", "--units", unit_id)
    assert error.value.code == 2
    assert not runtime.calls
    assert not runs.exists()


def test_public_persistence_maps_unsafe_ids_to_safe_paths(tmp_path):
    from evaluation.metrics import evaluate
    from persistence import save_unit

    unit = make_unit("../outside", reference=False)
    unit.requirements[0].id = "../../R1"
    unit.requirements[1].id = "intermediate"
    result = GenerationResult(cases=[GeneratedCase(
        id="case-1", title="..\\..//", description="Case", requirement_ids=["../../R1"]
    )])
    evaluation = evaluate(unit, result.cases, FakeEmbedder())
    run = tmp_path / "run"
    run.mkdir()
    save_unit(run, "one-shot", unit, result, evaluation)
    artifact, = run.glob("one-shot/*/results.json")
    snapshots = read_json(artifact)
    assert snapshots["unit_id"] == "../outside"
    requirement_path = Path(snapshots["links"]["requirements"]["../../R1"])
    assert requirement_path.parts[0] not in {"..", "intermediate"}
    assert (artifact.parent / requirement_path).is_file()
    assert not (tmp_path / "outside").exists()


def test_prepare_firefox_normalizes_local_csv_files(tmp_path):
    from main import main

    requirements, tests = tmp_path / "requirements.csv", tmp_path / "tests.csv"
    requirements.write_text(
        "RequirementID;RequirementContent\n" + "".join(f"R-{i:03d};Requirement {i}\n" for i in range(1, 185))
    )
    tests.write_text(
        "TestCaseID;TestCaseContent\n" + "".join(f"TC-{i:03d};Case {i}\n" for i in range(1, 185))
    )
    output = tmp_path / "normalized"
    assert main(["prepare", "firefox", "--requirements", str(requirements), "--tests", str(tests),
                 "--output", str(output)]) == 0
    assert len(read_json(output / f"{FIREFOX}.json")["requirements"]) == 18
    assert read_json(output / "firefox_legacy.json")["generatable"] is False


def test_prepare_e2edev_verifies_local_pin_and_writes_descriptive_profile(tmp_path, monkeypatch):
    from datasets import e2edev
    from main import main

    raw = tmp_path / "raw"
    source = raw / "E2EDev_data" / "E2ESD_Bench_01" / "requirment_with_tests.json"
    source.parent.mkdir(parents=True)
    source.write_text(json.dumps({"finegrained_rewith_test": {
        "1": {"requirement": {"description": "Open a document"}, "test_cases": []}
    }}))
    monkeypatch.setattr(e2edev, "ANNOTATION_SHA256", {"01": hashlib.sha256(source.read_bytes()).hexdigest()})
    output, profile = tmp_path / "normalized", tmp_path / "profile.json"
    command = ["prepare", "e2edev", "--source", str(raw), "--output", str(output),
               "--profile", str(profile)]
    assert main([*command, "--commit", SOURCE_COMMIT]) == 0
    assert read_json(profile)["aggregate"]["histogram"] == {"0": 1}
    assert read_json(output / f"{E2EDEV}.json")["id"] == E2EDEV
    with pytest.raises(SystemExit) as error:
        main([*command, "--commit", "wrong"])
    assert error.value.code == 2


def test_existing_unit_artifacts_are_immutable(tmp_path):
    from evaluation.metrics import evaluate
    from persistence import save_unit

    unit = make_unit(FIREFOX, reference=False)
    result = GenerationResult(cases=[
        GeneratedCase(id="G-001", title="Open document", description="Case", requirement_ids=["R1"])
    ])
    run = tmp_path / "run"
    run.mkdir()
    save_unit(run, "one-shot", unit, result, evaluate(unit, result.cases, FakeEmbedder()))
    old_artifact = run / "one-shot" / FIREFOX / "results.json"
    original = old_artifact.read_bytes()

    replacement = GenerationResult(cases=[])
    with pytest.raises(FileExistsError):
        save_unit(run, "one-shot", unit, replacement, evaluate(unit, replacement.cases, FakeEmbedder()))
    assert old_artifact.read_bytes() == original


def test_malformed_manifest_is_rejected_before_model_calls(cli, capsys):
    _, data, runs, runtime, _, run = cli
    put(data, make_unit(E2EDEV))
    manifests = data / "manifests"
    manifests.mkdir()
    (manifests / "e2edev.json").write_text("{}", encoding="utf-8")
    with pytest.raises(SystemExit) as error:
        run("--solutions", "one-shot", "--units", E2EDEV)
    assert error.value.code == 2
    assert "e2edev.json" in capsys.readouterr().err
    assert not runs.exists()
    assert not runtime.calls
