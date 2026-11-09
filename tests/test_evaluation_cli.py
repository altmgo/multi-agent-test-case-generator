import csv
import fcntl
import json
import os
from concurrent.futures import ThreadPoolExecutor
from threading import Event

import pytest

import evaluation_cli
import persistence
from evaluation.embeddings import EmbeddingBatch, EmbeddingError
from persistence import update_evaluation
from schemas import GeneratedCase, GenerationResult, ReferenceCase, Requirement, Unit, UsageRecord


RUN = "2026-11-09_00-00-00"
UNITS = ("firefox_bookmarks", "e2edev_cart")
SECRET = "provider-secret-do-not-persist"


def read(path):
    return json.loads(path.read_bytes())


def config(run):
    return json.loads((run / "configs.md").read_text().split("```json\n")[1].split("\n```")[0])


def write_config(run, payload):
    persistence.write_text(run / "configs.md", "# Experiment configuration\n\n```json\n" + json.dumps(payload) + "\n```\n")


def saved_run(root, *, solutions=persistence.SOLUTIONS, units=UNITS, without_references=()):
    run = root / RUN
    run.mkdir(parents=True)
    for solution in solutions:
        for unit_id in units:
            requirement = Requirement(id="R-1", text="Persisted requirement", language="en", source="fixture")
            generated = GeneratedCase(id="G-1", title="Check item", description="Open item.", requirement_ids=["R-1"])
            references = [] if unit_id in without_references else [
                ReferenceCase(id="T-1", title="Check item", description="Open item.", requirement_ids=["R-1"],
                              source="fixture", link_method="fixture", link_status="fixture")
            ]
            persistence.save_unit(
                run, solution, Unit(id=unit_id, parent_id="persisted_parent", requirements=[requirement], reference_cases=references),
                GenerationResult(cases=[generated], usage=UsageRecord(input_tokens=11, output_tokens=5),
                                 trace={"initial": {"fixture": True}, "rounds": []}),
                None, generation_attempts=[UsageRecord(input_tokens=11, output_tokens=5)],
            )
    write_config(run, {
        "status": "generated", "solutions": list(solutions), "units": {unit: {"file": f"{unit}.json"} for unit in units},
        "outcomes": {solution: {unit: {"status": "generated"} for unit in units} for solution in solutions},
        "index_failures": {}, "provenance": {"keep": "verbatim"},
    })
    return run


class FakeEmbedder:
    def __init__(self, failures=()):
        self.failures = iter(failures)
        self.closed = False
        self.calls = 0

    def embed(self, texts):
        self.calls += 1
        failure = next(self.failures, None)
        if failure is not None:
            raise failure
        return EmbeddingBatch([[1, 0] for _ in texts], UsageRecord(input_tokens=17, output_tokens=0), request_count=1)

    def close(self):
        self.closed = True


@pytest.fixture
def embedder(monkeypatch):
    fake = FakeEmbedder()
    monkeypatch.setattr(evaluation_cli, "make_embedder", lambda: fake)
    return fake


def args(root, *filters):
    return ["--results-dir", str(root), "--run", RUN, *filters]


def test_cli_evaluates_generated_snapshots_in_place_and_completes_config(tmp_path, embedder):
    run = saved_run(tmp_path, without_references=(UNITS[1],))
    immutable = {path: path.read_bytes() for path in run.rglob("*") if path.is_file() and path.suffix == ".md"}

    assert evaluation_cli.main(args(tmp_path)) == 0

    for solution in persistence.SOLUTIONS:
        for unit_id, expected in zip(UNITS, ("evaluated", "not_evaluable")):
            directory = run / solution / unit_id
            payload = read(directory / "results.json")
            assert payload["status"] == expected
            assert payload["evaluation"]["status"] == expected
            assert payload["failure"] is None
            assert payload["usage"]["embedding_requests"] == (1 if expected == "evaluated" else 0)
            with (directory / "results.csv").open() as stream:
                row = next(csv.DictReader(stream))
            assert row["status"] == expected
            assert row["generation_input_tokens"] == "11"
            matches = read(directory / "semantic_matches.json")
            assert matches["status"] == expected
            assert len(matches["matches"]) == (1 if expected == "evaluated" else 0)
    comparison = read(run / "comparison.json")
    assert comparison["unit_ids"] == [UNITS[0]]
    assert comparison["coverage"] == 0.5
    assert all(metrics["f1"] == 1.0 for metrics in comparison["metrics"].values())
    recorded = config(run)
    assert recorded["status"] == "completed"
    assert recorded["comparison"] == "comparison.json"
    assert recorded["provenance"] == {"keep": "verbatim"}
    assert recorded["outcomes"]["GHL"] == {
        UNITS[0]: {"status": "evaluated"}, UNITS[1]: {"status": "not_evaluable"},
    }
    assert all(path.read_bytes() == original for path, original in immutable.items() if path.name != "configs.md")
    assert embedder.closed


def test_retry_preserves_generation_unknown_and_human_fields(tmp_path, embedder):
    run = saved_run(tmp_path, solutions=("GHL",), units=(UNITS[0],))
    path = run / "GHL" / UNITS[0] / "results.json"
    original = read(path)
    original.update(status="failed", failure={"stage": "evaluation", "error_type": "EmbeddingError"},
                    human_evaluation={"reviewed_at": "unchanged", "custom": [1, 2]},
                    human_evaluation_history=[{"old": True}], custom_unknown={"keep": True})
    persistence.write_json(path, original)
    files = {file: file.read_bytes() for file in path.parent.rglob("*") if file.is_file()}

    assert evaluation_cli.main(args(tmp_path)) == 0

    updated = read(path)
    assert updated["status"] == "evaluated"
    assert updated["failure"] is None
    for key in original.keys() - {"status", "failure", "evaluation", "usage"}:
        assert updated[key] == original[key]
    for key in ("generation", "generation_attempts", "generation_calls"):
        assert updated["usage"][key] == original["usage"][key]
    assert updated["usage"]["embedding"]["input_tokens"] == 17
    for file, before in files.items():
        if file.name not in {"results.json", "results.csv", "semantic_matches.json"}:
            assert file.read_bytes() == before


def snapshot_bytes(run):
    return {path: path.read_bytes() for path in run.rglob("*") if path.is_file()}


def test_filters_retain_all_finalized_units_in_comparison(tmp_path, embedder):
    run = saved_run(tmp_path)
    assert evaluation_cli.main(args(tmp_path)) == 0
    before = snapshot_bytes(run)

    assert evaluation_cli.main(args(tmp_path, "--solution", "ghl", "--unit", UNITS[0])) == 0

    assert read(run / "comparison.json")["unit_ids"] == sorted(UNITS)
    assert read(run / "comparison.json")["metrics"]["one-shot"]["match_count"] == 2
    for path, original in before.items():
        if path.name == "results.json" and path.parents[1].name != "GHL":
            assert path.read_bytes() == original


def test_filtered_success_returns_zero_while_run_is_partial(tmp_path, embedder):
    run = saved_run(tmp_path)

    assert evaluation_cli.main(args(tmp_path, "--solution", "ghl", "--unit", UNITS[0])) == 0

    assert config(run)["status"] == "partial"
    assert read(run / "GHL" / UNITS[0] / "results.json")["status"] == "evaluated"
    assert read(run / "GHL" / UNITS[1] / "results.json")["status"] == "generated"
    assert read(run / "comparison.json")["unit_ids"] == []
    assert set(read(run / "comparison.json")["metrics"]) == set(persistence.SOLUTIONS)


@pytest.mark.parametrize("filters", [
    ["--solution", "unknown"], ["--solution", "../GHL"], ["--solution", "/GHL"],
    ["--unit", "missing"], ["--unit", "../firefox_bookmarks"], ["--unit", "/firefox_bookmarks"],
])
def test_invalid_filters_make_no_requests_or_writes(tmp_path, embedder, filters):
    run = saved_run(tmp_path)
    before = snapshot_bytes(run)

    assert evaluation_cli.main(args(tmp_path, *filters)) == 1

    assert snapshot_bytes(run) == before
    assert embedder.calls == 0


@pytest.mark.parametrize("name", ["../2026-11-09_00-00-00", "/tmp", "..", "nested/run"])
def test_unsafe_run_names_make_no_requests_or_writes(tmp_path, embedder, name):
    run = saved_run(tmp_path)
    before = snapshot_bytes(run)

    assert evaluation_cli.main(["--results-dir", str(tmp_path), "--run", name]) == 1

    assert snapshot_bytes(run) == before
    assert embedder.calls == 0


@pytest.mark.parametrize("target", ["root", "run", "solution", "unit", "snapshot", "csv", "matches", "config", "comparison", "linked_case"])
def test_symlink_paths_make_no_requests_or_writes(tmp_path, embedder, target):
    root = tmp_path / "results"
    run = saved_run(root, solutions=("GHL",), units=(UNITS[0],))
    unit = run / "GHL" / UNITS[0]
    paths = {
        "root": root, "run": run, "solution": run / "GHL", "unit": unit,
        "snapshot": unit / "results.json", "csv": unit / "results.csv",
        "matches": unit / "semantic_matches.json", "config": run / "configs.md",
        "comparison": run / "comparison.json", "linked_case": next(unit.glob("*/test cases/*.md")),
    }
    path = paths[target]
    outside = tmp_path / "outside"
    if path.exists():
        path.rename(outside)
    else:
        outside.write_text("unchanged")
    path.symlink_to(outside, target_is_directory=outside.is_dir())
    before = snapshot_bytes(tmp_path)

    assert evaluation_cli.main(args(root)) == 1

    assert snapshot_bytes(tmp_path) == before
    assert embedder.calls == 0


@pytest.mark.parametrize("mutation", [
    "invalid_json", "schema", "schema_boolean", "schema_float", "parent_id", "solution", "unknown_unit", "duplicate_requirement", "duplicate_generated",
    "duplicate_reference", "generated_link", "reference_link", "artifact_link", "case_link", "status", "evaluation_count",
])
def test_malformed_snapshots_are_rejected_before_any_work(tmp_path, embedder, mutation):
    run = saved_run(tmp_path, solutions=("GHL",))
    path = run / "GHL" / UNITS[1] / "results.json"
    payload = read(path)
    if mutation == "schema":
        payload["schema_version"] = 2
    elif mutation == "schema_boolean":
        payload["schema_version"] = True
    elif mutation == "schema_float":
        payload["schema_version"] = 1.0
    elif mutation == "parent_id":
        payload["parent_id"] = "   "
    elif mutation == "solution":
        payload["solution"] = "one-shot"
    elif mutation == "unknown_unit":
        payload["unit_id"] = "unknown"
    elif mutation.startswith("duplicate_"):
        key = {"duplicate_requirement": "requirements", "duplicate_generated": "generated_cases", "duplicate_reference": "reference_cases"}[mutation]
        payload[key].append(payload[key][0])
    elif mutation in {"generated_link", "reference_link"}:
        payload["generated_cases" if mutation == "generated_link" else "reference_cases"][0]["requirement_ids"] = ["missing"]
    elif mutation == "artifact_link":
        payload["artifacts"]["csv"] = "../results.csv"
    elif mutation == "case_link":
        payload["links"]["cases"]["G-1"] = {"missing": "missing.md"}
    elif mutation == "status":
        payload["status"] = "evaluated"
    elif mutation == "evaluation_count":
        evaluation = evaluation_cli.evaluate(
            Unit(id=payload["unit_id"], requirements=payload["requirements"], reference_cases=payload["reference_cases"]),
            [GeneratedCase.model_validate(case) for case in payload["generated_cases"]], FakeEmbedder(),
        ).model_dump(mode="json")
        payload.update(status="evaluated", evaluation={**evaluation, "generated_count": 99})
    persistence.write_json(path, payload)
    if mutation == "invalid_json":
        path.write_text('{"secret": "' + SECRET)
    before = snapshot_bytes(run)

    assert evaluation_cli.main(args(tmp_path)) == 1

    assert snapshot_bytes(run) == before
    assert embedder.calls == 0


def test_duplicate_unit_ids_are_rejected_before_work(tmp_path, embedder):
    import shutil

    run = saved_run(tmp_path, solutions=("GHL",))
    shutil.copytree(run / "GHL" / UNITS[0], run / "GHL" / "duplicate")
    before = snapshot_bytes(run)

    assert evaluation_cli.main(args(tmp_path)) == 1

    assert snapshot_bytes(run) == before
    assert embedder.calls == 0


@pytest.mark.parametrize("change", ["rename", "swap"])
def test_renamed_or_swapped_unit_directories_are_rejected_before_work(tmp_path, embedder, change):
    run = saved_run(tmp_path, solutions=("GHL",))
    first, second = [run / "GHL" / unit for unit in UNITS]
    renamed = first.with_name("unknown")
    first.rename(renamed)
    if change == "swap":
        second.rename(first)
        renamed.rename(second)
    before = snapshot_bytes(run)

    assert evaluation_cli.main(args(tmp_path)) == 1

    assert snapshot_bytes(run) == before
    assert embedder.calls == 0


@pytest.mark.parametrize("unit_id", ["con", "unit with spaces"])
def test_hashed_unit_directories_can_be_evaluated_in_place(tmp_path, embedder, unit_id):
    run = saved_run(tmp_path, solutions=("GHL",), units=(unit_id,))
    directory = next((run / "GHL").iterdir())
    assert directory.name.startswith("~")

    assert evaluation_cli.main(args(tmp_path, "--unit", unit_id)) == 0

    assert read(directory / "results.json")["status"] == "evaluated"
    assert read(run / "comparison.json")["unit_ids"] == [unit_id]
    assert config(run)["status"] == "completed"


def test_concurrent_filtered_refreshes_keep_the_latest_complete_summary(tmp_path, monkeypatch):
    run = saved_run(tmp_path, solutions=("GHL",))
    monkeypatch.setattr(evaluation_cli, "make_embedder", FakeEmbedder)
    first_summary_ready, second_summary_attempted = Event(), Event()
    aggregate = evaluation_cli.aggregate
    write_text = evaluation_cli.write_text
    flock = fcntl.flock
    run_stat = run.stat()

    def pause_first_summary(results, **kwargs):
        comparison = aggregate(results, **kwargs)
        if not first_summary_ready.is_set():
            first_summary_ready.set()
            assert second_summary_attempted.wait(5), "Second filtered invocation never reached its summary"
        return comparison

    def observe_run_lock(fd, operation):
        stat = os.fstat(fd)
        if ((stat.st_dev, stat.st_ino) == (run_stat.st_dev, run_stat.st_ino)
                and operation & fcntl.LOCK_EX and first_summary_ready.is_set()):
            second_summary_attempted.set()
        return flock(fd, operation)

    def observe_summary_write(path, content):
        write_text(path, content)
        # Without a run lock, let the newer summary finish before the older one.
        if path == run / "configs.md" and first_summary_ready.is_set():
            second_summary_attempted.set()

    monkeypatch.setattr(evaluation_cli, "aggregate", pause_first_summary)
    monkeypatch.setattr(fcntl, "flock", observe_run_lock)
    monkeypatch.setattr(evaluation_cli, "write_text", observe_summary_write)
    with ThreadPoolExecutor(max_workers=2) as workers:
        first = workers.submit(evaluation_cli.evaluate_run, run, "GHL", UNITS[0])
        assert first_summary_ready.wait(5), "First filtered invocation never reached its summary"
        second = workers.submit(evaluation_cli.evaluate_run, run, "GHL", UNITS[1])
        assert first.result(timeout=10) == 0
        assert second.result(timeout=10) == 0

    comparison = read(run / "comparison.json")
    assert comparison["unit_ids"] == sorted(UNITS)
    assert comparison["coverage"] == 1.0
    assert comparison["metrics"]["GHL"]["match_count"] == 2
    recorded = config(run)
    assert recorded["status"] == "completed"
    assert recorded["outcomes"] == {"GHL": {unit: {"status": "evaluated"} for unit in UNITS}}


def test_generation_failures_are_skipped_and_run_stays_partial(tmp_path, embedder):
    run = saved_run(tmp_path, solutions=("GHL",))
    path = run / "GHL" / UNITS[0] / "results.json"
    payload = read(path)
    payload.update(status="failed", failure={"stage": "critic", "error_type": "ValueError"})
    persistence.write_json(path, payload)
    before = path.read_bytes()

    assert evaluation_cli.main(args(tmp_path)) == 0

    assert path.read_bytes() == before
    assert config(run)["status"] == "partial"
    assert config(run)["outcomes"]["GHL"][UNITS[0]] == {"status": "failed", "failure": payload["failure"]}
    assert config(run)["outcomes"]["GHL"][UNITS[1]] == {"status": "evaluated"}


@pytest.mark.parametrize("error", [
    EmbeddingError(SECRET, usage=UsageRecord(input_tokens=7), request_count=1), RuntimeError(SECRET),
])
def test_provider_failure_continues_and_retry_repairs_without_secret_leaks(tmp_path, monkeypatch, capsys, error):
    run = saved_run(tmp_path, solutions=("GHL",))
    fake = FakeEmbedder([error])
    monkeypatch.setattr(evaluation_cli, "make_embedder", lambda: fake)

    assert evaluation_cli.main(args(tmp_path)) == 1

    first, second = [read(run / "GHL" / unit / "results.json") for unit in sorted(UNITS)]
    assert first["failure"] == {"stage": "evaluation", "error_type": type(error).__name__}
    assert first["status"] == "failed"
    assert second["status"] == "evaluated"
    if isinstance(error, EmbeddingError):
        assert first["usage"]["embedding"]["input_tokens"] == 7
        assert first["usage"]["embedding_requests"] == 1
    assert fake.closed
    assert SECRET not in capsys.readouterr().err
    assert all(SECRET.encode() not in content for content in snapshot_bytes(run).values())
    monkeypatch.setattr(evaluation_cli, "make_embedder", FakeEmbedder)
    assert evaluation_cli.main(args(tmp_path, "--unit", sorted(UNITS)[0])) == 0
    assert config(run)["status"] == "completed"
    assert read(run / "comparison.json")["unit_ids"] == sorted(UNITS)


def test_held_unit_lock_prevents_publication_without_changing_unit_artifacts(tmp_path, embedder):
    run = saved_run(tmp_path, solutions=("GHL",), units=(UNITS[0],))
    directory = run / "GHL" / UNITS[0]
    before = snapshot_bytes(directory)
    fd = os.open(directory, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        assert evaluation_cli.main(args(tmp_path)) == 1
    finally:
        os.close(fd)
    assert snapshot_bytes(directory) == before


def test_changed_snapshot_cannot_overwrite_human_review(tmp_path, embedder):
    run = saved_run(tmp_path, solutions=("GHL",), units=(UNITS[0],))
    path = run / "GHL" / UNITS[0] / "results.json"
    expected = path.read_bytes()
    original = read(path)
    original["human_evaluation"] = {"new": "review"}
    persistence.write_json(path, original)
    before = snapshot_bytes(path.parent)
    result = evaluation_cli.evaluate(
        Unit(id=UNITS[0], requirements=original["requirements"], reference_cases=original["reference_cases"]),
        [GeneratedCase.model_validate(case) for case in original["generated_cases"]], embedder,
    )

    with pytest.raises(ValueError, match="changed"):
        update_evaluation(path, expected, result)

    assert snapshot_bytes(path.parent) == before


def test_results_json_is_replaced_last_and_temporary_files_are_cleaned(tmp_path, embedder, monkeypatch):
    run = saved_run(tmp_path, solutions=("GHL",), units=(UNITS[0],))
    path = run / "GHL" / UNITS[0] / "results.json"
    original = path.read_bytes()
    replaced = []
    replace = persistence.os.replace

    def record_replace(source, destination):
        if destination.parent == path.parent:
            replaced.append(destination.name)
            assert source.parent == destination.parent
            assert path.read_bytes() == original
        return replace(source, destination)

    monkeypatch.setattr(persistence.os, "replace", record_replace)
    assert evaluation_cli.main(args(tmp_path)) == 0
    assert replaced == ["results.csv", "semantic_matches.json", "results.json"]
    assert not list(run.rglob(".write-*"))


def test_embedder_close_failure_is_sanitized_and_keeps_persisted_evaluation(tmp_path, embedder, capsys):
    run = saved_run(tmp_path, solutions=("GHL",), units=(UNITS[0],))

    def fail_close():
        raise RuntimeError(SECRET)

    embedder.close = fail_close

    assert evaluation_cli.main(args(tmp_path)) == 1

    assert read(run / "GHL" / UNITS[0] / "results.json")["status"] == "evaluated"
    assert config(run)["status"] == "completed"
    assert SECRET not in capsys.readouterr().err
    assert all(SECRET.encode() not in content for content in snapshot_bytes(run).values())
