import fcntl
import json
import os
from datetime import datetime

import pytest

import persistence
from schemas import EvaluationResult, GeneratedCase, GenerationResult, HumanDecision, ReferenceCase, Requirement, SemanticMatch, Unit


RUN = "2026-11-09_00-00-00"
SOL = "Multiagent"
UNIT = "firefox_bookmarks"


def saved_unit(root, *, has_references=True, has_matches=True, failed=False, reverse=False, run_name=RUN):
    requirements = [
        Requirement(id=f"req-{i}", text=f"Requirement text {i}", language="en", source="fixture")
        for i in range(1, 5)
    ]
    generated = [
        GeneratedCase(id=f"secret-solution-generated-{i}", title=f"Generated title {i}",
                      description=f"Generated text {i}", requirement_ids=[f"req-{i}"])
        for i in range(1, 5)
    ]
    references = [
        ReferenceCase(id=f"ref-{i}", title=f"ref-{i}" if i == 1 else f"Reference title {i}",
                      description=f"Reference text {i}", requirement_ids=[f"req-{2 if i == 1 else i}"],
                      source="fixture", link_method="inferred_row_alignment", link_status="pending_provenance_review")
        for i in range(1, 5)
    ] if has_references else []
    matches = [
        SemanticMatch(generated_id=gen.id, reference_id=ref.id, similarity=0.98765)
        for gen, ref in zip(generated[:3], references[:3])
    ] if has_matches else []
    if reverse:
        matches.reverse()
    score = len(matches) / len(generated) if has_references else None
    automatic = EvaluationResult(
        status="evaluated" if has_references else "not_evaluable",
        generated_count=len(generated), reference_count=len(references), matches=matches,
        precision=score, recall=score, f1=score,
    )
    run = root / run_name
    run.mkdir(parents=True)
    persistence.save_unit(
        run, SOL, Unit(id=UNIT, requirements=requirements, reference_cases=references),
        GenerationResult(cases=generated), None if failed else automatic,
        failure={"stage": "embedding", "error_type": "EmbeddingError"} if failed else None,
    )
    return run / SOL / UNIT / "results.json"


def decisions():
    return [
        HumanDecision(generated_id=f"secret-solution-generated-{i}", reference_id=f"ref-{i}",
                      verdict=verdict, justification="Different setup" if i == 2 else "")
        for i, verdict in enumerate(("equivalent", "different", "inconclusive"), 1)
    ]


def read(path):
    return json.loads(path.read_bytes())


def review_args(root):
    return ["--results-dir", str(root), "--run", RUN, "--solution", SOL.lower(), "--unit", UNIT]


def scripted_input(monkeypatch, answers):
    replies = iter(answers)

    def answer(prompt):
        print(prompt, end="")
        try:
            return next(replies)
        except StopIteration:
            raise EOFError from None

    monkeypatch.setattr("builtins.input", answer)


def test_credits_only_equivalent_positives_without_changing_automatic_data(tmp_path):
    from human_review import review_unit

    path = saved_unit(tmp_path)
    original = read(path)
    csv_before = path.with_suffix(".csv").read_bytes()
    result = review_unit(path, list(reversed(decisions())))
    assert result.scope == "automatic_matches_only"
    assert datetime.fromisoformat(result.model_dump(mode="json")["reviewed_at"]).utcoffset().total_seconds() == 0
    assert (result.equivalent_count, result.different_count, result.inconclusive_count) == (1, 1, 1)
    assert (result.generated_count, result.reference_count) == (4, 4)
    assert (result.precision, result.recall, result.f1) == (0.25, 0.25, 0.25)
    saved = read(path)
    assert saved.pop("human_evaluation") == result.model_dump(mode="json")
    assert saved.pop("human_evaluation_history", []) == []
    assert saved == original
    assert path.with_suffix(".csv").read_bytes() == csv_before


@pytest.mark.parametrize("with_references, expected", [(True, 0.0), (False, None)])
def test_empty_queue_metrics_depend_on_reference_availability(tmp_path, with_references, expected):
    from human_review import review_unit

    path = saved_unit(tmp_path, has_references=with_references, has_matches=False)
    result = review_unit(path, [])
    assert result.decisions == []
    assert (result.precision, result.recall, result.f1) == (expected, expected, expected)
    assert (result.generated_count, result.reference_count) == (4, 4 if with_references else 0)


@pytest.mark.parametrize("invalid", ["missing", "duplicate", "unmatched", "cross-paired"])
def test_invalid_decision_set_leaves_original_bytes(tmp_path, invalid):
    from human_review import review_unit

    path = saved_unit(tmp_path)
    original = path.read_bytes()
    submitted = decisions()
    if invalid == "missing":
        submitted.pop()
    elif invalid == "duplicate":
        submitted.append(submitted[0])
    elif invalid == "unmatched":
        submitted[0].reference_id = "ref-4"
    else:
        submitted[0].reference_id = "ref-2"

    with pytest.raises(ValueError):
        review_unit(path, submitted)
    assert path.read_bytes() == original


def test_failed_unit_has_no_reviewable_evaluation(tmp_path):
    from human_review import main, review_unit

    path = saved_unit(tmp_path, failed=True)
    original = path.read_bytes()
    with pytest.raises(ValueError, match="finalized automatic evaluation"):
        review_unit(path, [])
    assert main(review_args(tmp_path)) == 1
    assert path.read_bytes() == original


def test_cli_displays_only_positive_pairs_with_relevant_text_in_stable_blind_order(tmp_path, monkeypatch, capsys):
    from human_review import main

    outputs = []
    for i, reverse in enumerate((False, True)):
        root = tmp_path / str(i)
        path = saved_unit(root, reverse=reverse)
        scripted_input(monkeypatch, [
            "equivalent", "", "different", "Different setup", "inconclusive", "", "y",
        ])
        assert main(review_args(root)) == 0
        output = capsys.readouterr().out
        assert "Pair 1 of 3" in output and "Pair 3 of 3" in output
        for present in ("Requirement text 1", "Requirement text 2", "Reference text 1", "Generated text 1",
                        "Reference title 2", "Generated title 3"):
            assert present in output
        for hidden in (SOL, "0.98765", "secret-solution-generated-", "req-", "ref-1",
                       "Generated text 4", "Reference text 4", "Requirement text 4"):
            assert hidden not in output
        saved = read(path)["human_evaluation"]
        assert [decision["verdict"] for decision in saved["decisions"]] == [
            "equivalent", "different", "inconclusive",
        ]
        assert saved["decisions"][1]["justification"] == "Different setup"
        outputs.append(output)
    assert outputs[0] == outputs[1]


@pytest.mark.parametrize("answers", [[], ["q"], ["equivalent", ""], ["equivalent", "", "different", "", "inconclusive", "", "n"]])
def test_cancel_or_eof_preserves_original_bytes(tmp_path, monkeypatch, answers):
    from human_review import main

    path = saved_unit(tmp_path)
    original = path.read_bytes()
    scripted_input(monkeypatch, answers)
    assert main(review_args(tmp_path)) == 0
    assert path.read_bytes() == original


def test_cli_can_select_run_solution_and_unit_from_menus(tmp_path, monkeypatch):
    from human_review import main

    path = saved_unit(tmp_path, has_matches=False)
    scripted_input(monkeypatch, ["1", "1", "1", "y"])
    assert main(["--results-dir", str(tmp_path)]) == 0
    assert read(path)["human_evaluation"]["precision"] == 0.0


def test_run_menu_excludes_runs_with_only_failed_units(tmp_path, monkeypatch, capsys):
    from human_review import main

    path = saved_unit(tmp_path, has_matches=False)
    failed_run = "2026-11-09_00-00-01"
    saved_unit(tmp_path, failed=True, run_name=failed_run)
    scripted_input(monkeypatch, ["1", "1", "1", "y"])
    assert main(["--results-dir", str(tmp_path)]) == 0
    assert failed_run not in capsys.readouterr().out
    assert read(path)["human_evaluation"]["precision"] == 0.0


def test_confirmed_rereview_archives_previous_and_cancel_preserves_it(tmp_path, monkeypatch):
    from human_review import main, review_unit

    path = saved_unit(tmp_path)
    previous = review_unit(path, decisions()).model_dump(mode="json")
    original = path.read_bytes()

    scripted_input(monkeypatch, ["n"])
    assert main(review_args(tmp_path)) == 0
    assert path.read_bytes() == original

    scripted_input(monkeypatch, ["y", "different", "", "different", "", "different", "", "y"])
    assert main(review_args(tmp_path)) == 0
    saved = read(path)
    assert saved["human_evaluation_history"] == [previous]
    assert saved["human_evaluation"]["different_count"] == 3
    assert saved["evaluation"]["precision"] == 0.75

    review_unit(path, decisions())
    assert read(path)["human_evaluation_history"] == [previous, saved["human_evaluation"]]


def test_failed_atomic_replace_keeps_previous_review_and_cleans_temporary_files(tmp_path, monkeypatch):
    from human_review import main, review_unit

    path = saved_unit(tmp_path)
    review_unit(path, decisions())
    original = path.read_bytes()
    contents = set(path.parent.iterdir())

    def fail_replace(source, destination):
        assert destination == path
        assert source.read_bytes() != original
        raise OSError("simulated failed replacement")

    monkeypatch.setattr(persistence.os, "replace", fail_replace)
    scripted_input(monkeypatch, ["y", "different", "", "different", "", "different", "", "y"])
    assert main(review_args(tmp_path)) == 1
    assert path.read_bytes() == original
    assert set(path.parent.iterdir()) == contents


def test_stale_cli_review_cannot_replace_concurrently_published_review(tmp_path, monkeypatch):
    from human_review import main, review_unit

    path = saved_unit(tmp_path)
    replies = iter(["different", "", "different", "", "different", "", "y"])
    published = []

    def answer(prompt):
        reply = next(replies)
        if reply == "y":
            review_unit(path, decisions())
            published.append(path.read_bytes())
        return reply

    monkeypatch.setattr("builtins.input", answer)
    assert main(review_args(tmp_path)) == 1
    assert path.read_bytes() == published[0]


def test_active_writer_lock_preserves_original_bytes(tmp_path):
    from human_review import review_unit

    path = saved_unit(tmp_path)
    original = path.read_bytes()
    fd = os.open(path.parent, os.O_RDONLY)
    try:
        fcntl.flock(fd, fcntl.LOCK_EX)
        with pytest.raises(ValueError, match="being saved"):
            review_unit(path, decisions())
    finally:
        os.close(fd)
    assert path.read_bytes() == original
