import json

import httpx2
import numpy as np
import pytest

from evaluation.embeddings import EmbeddingBatch, EmbeddingError, GeminiEmbedder, canonical_text
from evaluation.matching import match
from evaluation.metrics import aggregate, evaluate
from schemas import EvaluationResult, GeneratedCase, ReferenceCase, Unit, UsageRecord


def _generated(case_id, title="Check bookmark", description="Open bookmarks."):
    return GeneratedCase(
        id=case_id, title=title, description=description, requirement_ids=["R-001"]
    )


def _reference(case_id, title="Check bookmark", description="Open bookmarks."):
    return ReferenceCase(
        id=case_id, title=title, description=description, requirement_ids=["R-001"],
        source="fixture", link_method="fixture", link_status="fixture",
    )


class FakeEmbedder:
    def __init__(self, vectors):
        self.vectors = vectors
        self.calls = []

    def embed(self, texts):
        self.calls.append(texts)
        return EmbeddingBatch(self.vectors, UsageRecord(input_tokens=17), request_count=1)


def test_canonical_text_collapses_whitespace_and_keeps_both_fields():
    assert canonical_text("  Check\tbookmark  ", "\nOpen\u00a0 bookmarks. \r\n") == (
        "Check bookmark Open bookmarks."
    )


def test_match_uses_the_unrounded_inclusive_threshold():
    similarities = np.diag([0.699999, 0.70, 0.700001])
    assert match(similarities) == [(1, 1, 0.70), (2, 2, 0.700001)]


def test_match_maximizes_cardinality_before_similarity():
    assert match(np.array([[1.0, 0.71], [0.72, 0.69]])) == [
        (0, 1, 0.71), (1, 0, 0.72)
    ]


def test_match_maximizes_similarity_at_fixed_cardinality():
    assert match(np.array([[0.71, 0.98], [0.91, 0.73]])) == [
        (0, 1, 0.98), (1, 0, 0.91)
    ]


def test_match_preserves_even_one_ulp_of_similarity_advantage():
    just_above = np.nextafter(0.70, np.inf)
    scores = np.array([[just_above, 0.95], [0.70, 0.95]])
    assert match(scores) == [(0, 0, just_above), (1, 1, 0.95)]


def test_tied_matches_are_stable_for_the_same_input_order():
    scores = np.full((3, 2), 0.8)
    assert match(scores) == match(scores.copy()) == [(0, 0, 0.8), (1, 1, 0.8)]


def test_evaluate_keeps_case_ids_and_matches_duplicate_text_only_once_per_reference():
    unit = Unit(
        id="firefox_bookmarks", parent_id="firefox_legacy", requirements=[],
        reference_cases=[
            _reference("TC-001", "TC-001", "\n Open bookmarks. "),
            _reference("TC-002", "Print", "Print the page."),
        ],
    )
    generated = [_generated("G-1"), _generated("G-2"), _generated("G-3", "Close", "Quit.")]
    embedder = FakeEmbedder([[3, 0], [3, 0], [-2, 0], [2, 0], [0, 8]])

    result = evaluate(unit, generated, embedder)

    assert embedder.calls == [[
        "Check bookmark Open bookmarks.", "Check bookmark Open bookmarks.",
        "Close Quit.", "Open bookmarks.", "Print Print the page.",
    ]]
    assert result.status == "evaluated"
    assert (result.generated_count, result.reference_count) == (3, 2)
    assert [item.model_dump() for item in result.matches] == [
        {"generated_id": "G-1", "reference_id": "TC-001", "similarity": 1.0},
    ]
    assert result.unmatched_generated_ids == ["G-2", "G-3"]
    assert result.unmatched_reference_ids == ["TC-002"]
    assert (result.precision, result.recall, result.f1) == pytest.approx((1 / 3, 1 / 2, 2 / 5))
    assert result.embedding_usage == UsageRecord(input_tokens=17)
    assert result.embedding_requests == 1


@pytest.mark.parametrize("vectors", [
    [[1, 0], [0, 0]],
    [[1, 0], [np.nan, 1]],
    [[1, 0], [np.inf, 1]],
    [[1, 0], [1]],
    [[1, 0]],
    [[], []],
    [[1, 0], [1j, 0]],
    [["1", "0"], ["1", "0"]],
])
def test_invalid_embeddings_raise_an_explicit_evaluation_error(vectors):
    unit = Unit(id="fixture", requirements=[], reference_cases=[_reference("T-1")])
    with pytest.raises(EmbeddingError):
        evaluate(unit, [_generated("G-1")], FakeEmbedder(vectors))


def test_evaluate_normalizes_finite_vectors_without_underflow_or_overflow():
    unit = Unit(id="fixture", requirements=[], reference_cases=[_reference("T-1")])
    result = evaluate(
        unit, [_generated("G-1")], FakeEmbedder([[1e308, 1e308], [1e-320, 1e-320]])
    )
    assert len(result.matches) == 1
    assert result.matches[0].similarity == pytest.approx(1)


@pytest.mark.parametrize("with_references", [False, True])
def test_no_work_preserves_ids_and_reports_no_embedding_requests(with_references):
    unit = Unit(
        id="fixture", requirements=[],
        reference_cases=[_reference("T-1")] if with_references else [],
    )
    generated = [] if with_references else [_generated("G-1")]
    embedder = FakeEmbedder([])

    result = evaluate(unit, generated, embedder)

    assert embedder.calls == []
    assert result.embedding_requests == 0
    assert result.embedding_usage == UsageRecord(input_tokens=0, output_tokens=0)
    if with_references:
        assert result.status == "evaluated"
        assert result.unmatched_reference_ids == ["T-1"]
        assert (result.precision, result.recall, result.f1) == (0.0, 0.0, 0.0)
    else:
        assert result.status == "not_evaluable"
        assert result.unmatched_generated_ids == ["G-1"]
        assert (result.precision, result.recall, result.f1) == (None, None, None)


def test_aggregate_compares_common_units_by_totals_and_exposes_coverage():
    refs = Unit(id="fixture", requirements=[], reference_cases=[_reference("T-1")])
    one_match = evaluate(refs, [_generated("G-1")], FakeEmbedder([[1, 0], [1, 0]]))
    one_of_three = evaluate(
        refs, [_generated("G-1"), _generated("G-2"), _generated("G-3")],
        FakeEmbedder([[1, 0], [0, 1], [0, 1], [1, 0]]),
    )
    empty = evaluate(refs, [], FakeEmbedder([]))
    unavailable = EvaluationResult(status="not_evaluable", generated_count=1)

    comparison = aggregate(
        {
            "one-shot": {"A": one_match, "B": one_of_three, "C": one_match},
            "ghl": {"A": empty, "B": one_match, "C": unavailable, "D": one_match},
        },
        selected_unit_ids=["A", "B", "C", "D", "E"],
    )

    assert comparison.unit_ids == ["A", "B"]
    assert comparison.total_unit_ids == ["A", "B", "C", "D", "E"]
    assert comparison.evaluable_unit_ids == {"one-shot": ["A", "B", "C"], "ghl": ["A", "B", "D"]}
    assert comparison.coverage == 0.4
    left, right = comparison.metrics["one-shot"], comparison.metrics["ghl"]
    assert (left.generated_count, left.reference_count, left.match_count) == (4, 2, 2)
    assert (left.precision, left.recall, left.f1) == pytest.approx((0.5, 1.0, 2 / 3))
    assert (right.generated_count, right.reference_count, right.match_count) == (1, 2, 1)
    assert (right.precision, right.recall, right.f1) == pytest.approx((1.0, 0.5, 2 / 3))


def test_aggregate_has_null_scores_when_no_common_units_are_evaluable():
    result = EvaluationResult(status="evaluated", generated_count=0, reference_count=1)
    comparison = aggregate({"one-shot": {"A": result}, "ghl": {"B": result}})

    assert comparison.unit_ids == []
    assert comparison.coverage == 0.0
    for metrics in comparison.metrics.values():
        assert (metrics.generated_count, metrics.reference_count, metrics.match_count) == (0, 0, 0)
        assert (metrics.precision, metrics.recall, metrics.f1) == (None, None, None)


def _gemini(monkeypatch, *responses):
    requests = []
    responses = iter(responses)

    def respond(request):
        requests.append((request.url.path, json.loads(request.content)))
        response = next(responses)
        status, payload = response if isinstance(response, tuple) else (200, response)
        return httpx2.Response(status, json=payload)

    monkeypatch.setenv("GOOGLE_API_KEY", "test-key")
    return GeminiEmbedder(client_args={"transport": httpx2.MockTransport(respond)}), requests


def test_gemini_sends_separate_content_and_charges_only_cache_misses(monkeypatch):
    embedder, requests = _gemini(
        monkeypatch,
        {
            "embeddings": [{"values": [1, 0]}, {"values": [0, 1]}],
            "usageMetadata": {"promptTokenCount": 12},
        },
        {"embeddings": [{"values": [-1, 0]}]},
    )

    first = embedder.embed(["Open bookmarks", "Print page", "Open bookmarks"])
    cached = embedder.embed(["Print page", "Open bookmarks"])
    mixed = embedder.embed(["Print page", "Close browser"])

    assert [path for path, _ in requests] == ["/v1beta/models/gemini-embedding-2:batchEmbedContents"] * 2
    for (_, payload), expected in zip(
        requests, (["Open bookmarks", "Print page"], ["Close browser"]), strict=True
    ):
        assert len(payload["requests"]) == len(expected)
        for request, text in zip(payload["requests"], expected, strict=True):
            assert "taskType" not in request
            assert request["content"]["parts"] == [
                {"text": f"task: sentence similarity | query: {text}"}
            ]
    np.testing.assert_array_equal(first.vectors, [[1, 0], [0, 1], [1, 0]])
    np.testing.assert_array_equal(cached.vectors, [[0, 1], [1, 0]])
    np.testing.assert_array_equal(mixed.vectors, [[0, 1], [-1, 0]])
    assert first.request_count == 1
    assert first.usage == UsageRecord(input_tokens=12)
    assert cached.request_count == 0
    assert cached.usage == UsageRecord(input_tokens=0, output_tokens=0)
    assert mixed.request_count == 1
    assert mixed.usage == UsageRecord()
    embedder.close()


def test_gemini_rejects_aggregated_response_and_retries_without_poisoned_cache(monkeypatch):
    embedder, requests = _gemini(
        monkeypatch,
        {"embeddings": [{"values": [1, 0]}], "usageMetadata": {"promptTokenCount": 12}},
        {"embeddings": [{"values": [0, 1]}, {"values": [1, 1]}]},
    )
    with pytest.raises(EmbeddingError) as error:
        embedder.embed(["Open bookmarks", "Print page"])

    assert error.value.request_count == 1
    assert error.value.usage == UsageRecord(input_tokens=12)
    recovered = embedder.embed(["Open bookmarks", "Print page"])
    np.testing.assert_array_equal(recovered.vectors, [[0, 1], [1, 1]])
    assert len(requests) == 2
    assert requests[0] == requests[1]
    embedder.close()


def test_gemini_sums_reported_counts_across_separate_http_batches(monkeypatch):
    embedder, requests = _gemini(
        monkeypatch,
        {
            "embeddings": [{"values": [1, 0]}] * 100,
            "usageMetadata": {"promptTokenCount": 1000, "promptTokenDetails": [
                {"modality": "TEXT", "tokenCount": 1000},
            ]},
        },
        {
            "embeddings": [{"values": [0, 1]}],
            "usageMetadata": {"promptTokenCount": 10, "promptTokenDetails": [
                {"modality": "TEXT", "tokenCount": 10},
            ]},
        },
    )
    result = embedder.embed([f"Case {index}" for index in range(101)])

    assert [len(payload["requests"]) for _, payload in requests] == [100, 1]
    assert len(result.vectors) == 101
    assert result.vectors[-1] == (0.0, 1.0)
    assert result.request_count == 2
    assert result.usage == UsageRecord(input_tokens=1010, details={"text_prompt_tokens": 1010})
    embedder.close()


def test_gemini_http_failure_retains_reported_usage_and_hides_response_details(monkeypatch):
    embedder, requests = _gemini(
        monkeypatch,
        (429, {"error": {
            "code": 429,
            "message": "private provider response",
            "status": "RESOURCE_EXHAUSTED",
            "usageMetadata": {"promptTokenCount": 4},
        }}),
    )
    with pytest.raises(EmbeddingError) as error:
        embedder.embed(["Open bookmarks"])

    assert len(requests) == 1
    assert error.value.request_count == 1
    assert error.value.usage == UsageRecord(input_tokens=4)
    assert "private provider response" not in str(error.value)
    assert error.value.__context__ is None
    embedder.close()


def test_empty_gemini_batch_needs_no_credentials(monkeypatch):
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    embedder = GeminiEmbedder()
    assert embedder.embed([]).request_count == 0
    with pytest.raises(EmbeddingError, match="GOOGLE_API_KEY") as error:
        embedder.embed(["Open bookmarks"])

    assert error.value.request_count == 0
