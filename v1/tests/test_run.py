import asyncio
import csv
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from datasets.e2edev import SOURCE_COMMIT
from model_runtime import CallRecord, ContextEstimate
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
        self.call_records = []
        self.usage_records = []

    async def run(self, stage, instructions, input, output_type, *, extra=None):
        assert len(input.requirements) == 3
        assert "reference_cases" not in input.model_dump()
        self.calls.append((stage, input.unit_id, extra))
        usage = UsageRecord(input_tokens=2, output_tokens=3)
        record = CallRecord(
            stage=stage, unit_id=input.unit_id, model_id=MODEL, call_id=len(self.calls), attempt=1,
            context=ContextEstimate(requirements_tokens=10, instructions_tokens=5, extra_tokens=0,
                                    schema_tokens=5, output_tokens=100),
            usage=usage,
        )
        self.call_records.append(record)
        self.usage_records.append(usage)
        try:
            value = self.respond(stage, input.unit_id, extra)
            await asyncio.sleep(0)
            output = output_type.model_validate(value)
        except (asyncio.CancelledError, Exception) as error:
            record.status = "failed"
            record.error_type = type(error).__name__
            raise
        record.status = "succeeded"
        return output


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

    def embedder():
        pytest.fail("Generation runs must not construct an embedder")

    monkeypatch.setattr(cli_module, "make_runtime", lambda _: runtime)
    monkeypatch.setattr(cli_module, "make_embedder", embedder, raising=False)

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
    assert result["status"] == "generated"
    assert result["failure"] is None
    assert result["evaluation"] is None
    assert result["usage"]["embedding_requests"] == 0
    matches = read_json(unit_dir / "semantic_matches.json")
    assert matches["status"] == "generated"
    assert matches["matches"] == []
    assert matches["unmatched_generated_ids"] is None
    assert matches["unmatched_reference_ids"] is None
    assert set(result["links"]["cases"]["G-001"]) == {"R1", "R2"}
    row = csv_row(unit_dir)
    assert row["status"] == "generated"
    assert row["generated_count"] == "1"
    assert row["match_count"] == ""
    assert row["tokens_used"] == "5"
    assert row["embedding_requests"] == "0"
    assert row["precision"] == row["recall"] == row["f1"] == ""
    assert not (execution / "comparison.json").exists()
    assert config(execution)["status"] == "generated"
    assert config(execution)["outcomes"] == {"one-shot": {FIREFOX: {"status": "generated"}}}
    assert config(execution)["units"][FIREFOX]["sha256"] == expected_sha
    assert config(execution)["credential"]["present"] is True
    assert SECRET not in (execution / "configs.md").read_text()


def test_units_continue_after_generation_failures(cli):
    _, data, runs, runtime, _, run = cli
    for unit_id in (E2EDEV, CALIBRATION, FIREFOX):
        put(data, make_unit(unit_id))

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

    assert partial["usage"]["embedding_requests"] == 0
    assert read_json(multi / E2EDEV / "results.json")["status"] == "generated"
    assert read_json(multi / CALIBRATION / "results.json")["status"] == "generated"
    assert read_json(execution / "one-shot" / FIREFOX / "results.json")["status"] == "generated"
    assert not (execution / "comparison.json").exists()
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


def test_unit_without_references_publishes_generated_counts(cli):
    _, data, runs, _, _, run = cli
    put(data, make_unit(E2EDEV, reference=False))
    assert run("--solutions", "one-shot", "--units", E2EDEV) == 0
    execution, = runs.iterdir()
    unit_dir = execution / "one-shot" / E2EDEV
    assert csv_row(unit_dir)["status"] == "generated"
    assert csv_row(unit_dir)["generated_count"] == "1"
    assert csv_row(unit_dir)["reference_count"] == "0"
    assert csv_row(unit_dir)["precision"] == ""
    assert csv_row(unit_dir)["embedding_requests"] == "0"
    assert not (execution / "comparison.json").exists()


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
    from persistence import save_unit

    unit = make_unit("../outside", reference=False)
    unit.requirements[0].id = "../../R1"
    unit.requirements[1].id = "intermediate"
    result = GenerationResult(cases=[GeneratedCase(
        id="case-1", title="..\\..//", description="Case", requirement_ids=["../../R1"]
    )])
    run = tmp_path / "run"
    run.mkdir()
    save_unit(run, "one-shot", unit, result, None)
    artifact, = run.glob("one-shot/*/results.json")
    snapshots = read_json(artifact)
    assert snapshots["unit_id"] == "../outside"
    assert snapshots["status"] == "generated"
    assert snapshots["failure"] is None
    assert snapshots["evaluation"] is None
    assert snapshots["usage"]["embedding_requests"] == 0
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
    from persistence import save_unit

    unit = make_unit(FIREFOX, reference=False)
    result = GenerationResult(cases=[
        GeneratedCase(id="G-001", title="Open document", description="Case", requirement_ids=["R1"])
    ])
    run = tmp_path / "run"
    run.mkdir()
    save_unit(run, "one-shot", unit, result, None)
    old_artifact = run / "one-shot" / FIREFOX / "results.json"
    original = old_artifact.read_bytes()

    replacement = GenerationResult(cases=[])
    with pytest.raises(FileExistsError):
        save_unit(run, "one-shot", unit, replacement, None)
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


@pytest.mark.parametrize("invalid_output", [False, True], ids=["provider-error", "invalid-links"])
def test_late_ghl_failure_preserves_validated_cases_and_techniques(cli, monkeypatch, invalid_output):
    module, data, runs, runtime, _, run = cli
    put(data, make_unit(FIREFOX))
    monkeypatch.setattr(module, "make_embedder", lambda: pytest.fail("A partial GHL result cannot be evaluated"))

    def scripted(stage, unit_id, extra):
        if stage == "ghl_generate_use_case" and extra["target"] == "R3":
            if invalid_output:
                return response(stage, unit_id, {**extra, "target": "R999"})
            raise RuntimeError(SECRET)
        return response(stage, unit_id, extra)

    runtime.respond = scripted
    assert run("--solutions", "GHL", "--units", FIREFOX, "--output-mode", "per_requirement") == 1
    execution, = runs.iterdir()
    unit_dir = execution / "GHL" / FIREFOX
    saved = read_json(unit_dir / "results.json")
    assert saved["status"] == "failed"
    assert saved["failure"] == {
        "stage": "ghl_generate_use_case", "error_type": "ValueError" if invalid_output else "RuntimeError"
    }
    assert saved["evaluation"] is None
    assert saved["generation"]["selected_techniques"] == ["use_case"]
    assert saved["generation"]["technique_rationales"] == {"use_case": "A workflow"}
    generated, = saved["generated_cases"]
    assert generated["id"] == "G-001"
    assert generated["requirement_ids"] == ["R1", "R2"]
    assert set(saved["links"]["cases"]["G-001"]) == {"R1", "R2"}
    assert csv_row(unit_dir)["tokens_used"] == "20"
    assert not (execution / "comparison.json").exists()
    assert config(execution)["status"] == "failed"
    assert all(SECRET not in path.read_text() for path in execution.rglob("*") if path.is_file())


def interrupted_result(cli, monkeypatch, solution, stage, *options):
    module, data, runs, runtime, _, run = cli
    for unit_id in (FIREFOX, E2EDEV):
        put(data, make_unit(unit_id))
    monkeypatch.setattr(module, "make_embedder", lambda: pytest.fail("Interrupted generation cannot be evaluated"))

    with pytest.raises(asyncio.CancelledError, match=SECRET):
        run("--solutions", solution, "--units", FIREFOX, E2EDEV, *options)

    execution, = runs.iterdir()
    recorded = config(execution)
    assert recorded["status"] == "interrupted"
    failure = {"stage": stage, "error_type": "CancelledError"}
    assert recorded["outcomes"] == {solution: {FIREFOX: {"status": "failed", "failure": failure}}}
    assert not (execution / "comparison.json").exists()
    assert {unit_id for _, unit_id, _ in runtime.calls} == {FIREFOX}
    unit_dir = execution / solution / FIREFOX
    saved = read_json(unit_dir / "results.json")
    assert saved["status"] == "failed"
    assert saved["failure"] == failure
    assert saved["evaluation"] is None
    assert saved["usage"]["embedding_requests"] == 0
    assert csv_row(unit_dir)["precision"] == ""
    assert all(SECRET not in path.read_text() for path in execution.rglob("*") if path.is_file())
    return saved, unit_dir


def test_ghl_interruption_saves_validated_cases_selection_and_call_usage(cli, monkeypatch):
    _, _, _, runtime, _, _ = cli

    def scripted(stage, unit_id, extra):
        if stage == "ghl_select_techniques":
            return {"selections": [
                {"technique_id": "use_case", "rationale": "A workflow"},
                {"technique_id": "state_transition", "rationale": "State changes"},
            ]}
        if stage == "ghl_generate_state_transition":
            asyncio.current_task().cancel(SECRET)
        return response(stage, unit_id, extra)

    runtime.respond = scripted
    saved, unit_dir = interrupted_result(cli, monkeypatch, "GHL", "ghl_generate_state_transition")
    assert saved["generation"]["selected_techniques"] == ["use_case", "state_transition"]
    assert saved["generation"]["technique_rationales"] == {"use_case": "A workflow", "state_transition": "State changes"}
    generated, = saved["generated_cases"]
    assert generated["id"] == "G-001"
    assert set(saved["links"]["cases"]["G-001"]) == {"R1", "R2"}
    assert [(call["stage"], call["status"], call["error_type"]) for call in saved["usage"]["generation_calls"]] == [
        ("ghl_select_techniques", "succeeded", None),
        ("ghl_generate_use_case", "succeeded", None),
        ("ghl_generate_state_transition", "failed", "CancelledError"),
    ]
    assert len(saved["usage"]["generation_attempts"]) == 3
    assert csv_row(unit_dir)["tokens_used"] == "15"


def test_multiagent_interruption_saves_the_last_accepted_decision(cli, monkeypatch):
    _, _, _, runtime, _, _ = cli
    revised = 0

    def scripted(stage, unit_id, extra):
        nonlocal revised
        if stage == "multiagent_critic":
            blockers = ["Unclear setup"]
            if revised != 1:
                blockers.append("Bad result")
            return {"feedback": "Improve the case", "request_revision": True, "confirmed_blockers": blockers}
        answer = response(stage, unit_id, extra)
        if extra["revision"] is not None:
            revised += 1
            if revised == 1:
                answer["cases"][0]["title"] = "Accepted improvement"
            if revised == 4:
                asyncio.current_task().cancel(SECRET)
        return answer

    runtime.respond = scripted
    saved, unit_dir = interrupted_result(cli, monkeypatch, "Multiagent", "generator", "--agents", "critic", "validator")
    generated, = saved["generated_cases"]
    assert generated["title"] == "Accepted improvement"
    trace = read_json(unit_dir / "intermediate" / "trace.json")
    assert trace["status"] == "failed"
    assert trace["failure"] == {"stage": "generator", "error_type": "CancelledError", "detail": None}
    assert trace["accepted_id"] == "round-1-candidate-1"
    decision, = trace["rounds"]
    assert read_json(unit_dir / "intermediate" / "round_001" / "decision.json") == decision
    assert decision["selected_id"] == "round-1-candidate-1"
    assert trace["pending_controls"] == ["critic", "validator"]
    assert trace["calls"][-1] == {
        "stage": "generator", "subject_id": "round-2-candidate-1", "output": None,
        "error_type": "CancelledError",
        "usage": [{"input_tokens": 2, "output_tokens": 3, "details": None, "status": "available"}],
    }
    assert len(saved["usage"]["generation_attempts"]) == len(saved["usage"]["generation_calls"]) == 9
    assert csv_row(unit_dir)["tokens_used"] == "45"


def test_one_shot_interruption_saves_reported_usage(cli, monkeypatch):
    _, _, _, runtime, _, _ = cli

    def scripted(stage, unit_id, extra):
        asyncio.current_task().cancel(SECRET)
        return response(stage, unit_id, extra)

    runtime.respond = scripted
    saved, unit_dir = interrupted_result(cli, monkeypatch, "one-shot", "one_shot")
    assert saved["generated_cases"] == []
    assert saved["usage"]["generation"] == {
        "input_tokens": 2, "output_tokens": 3, "details": None, "status": "available",
    }
    call, = saved["usage"]["generation_calls"]
    assert (call["stage"], call["status"], call["error_type"]) == ("one_shot", "failed", "CancelledError")
    assert csv_row(unit_dir)["tokens_used"] == "5"


def test_index_write_failure_preserves_generated_units_and_continues(cli, monkeypatch, capsys):
    import persistence

    _, data, runs, _, _, run = cli
    put(data, make_unit(FIREFOX))
    write_text = persistence.write_text

    def fail_one_index(path, content):
        if path.name == "requirements_to_tests.md" and path.parent.name == "one-shot":
            raise OSError(SECRET)
        write_text(path, content)

    monkeypatch.setattr(persistence, "write_text", fail_one_index)
    assert run("--solutions", "one-shot", "GHL", "--units", FIREFOX) == 1
    execution, = runs.iterdir()
    unit_dir = execution / "one-shot" / FIREFOX
    assert not (execution / "one-shot" / "requirements_to_tests.md").exists()
    assert (execution / "GHL" / "requirements_to_tests.md").is_file()
    assert read_json(unit_dir / "results.json")["status"] == "generated"
    assert csv_row(unit_dir)["status"] == "generated"
    assert not (execution / "comparison.json").exists()
    recorded = config(execution)
    assert recorded["status"] == "partial"
    assert recorded["outcomes"]["one-shot"][FIREFOX] == {"status": "generated"}
    assert recorded["index_failures"] == {"one-shot": {"error_type": "OSError"}}
    error = capsys.readouterr().err
    assert "one-shot/requirements_to_tests.md" in error
    assert SECRET not in error
