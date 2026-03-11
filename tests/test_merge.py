from paperfetch.merge import finalize_record, merge_provider_result
from paperfetch.models import PaperRecord
from paperfetch.providers.base import ProviderResult


def test_arxiv_authoritative_merge_beats_alpha() -> None:
    record = PaperRecord(input="2301.12345")
    merge_provider_result(
        record,
        ProviderResult(
            provider="alphaxiv_html",
            status="success",
            data={"title": "Alpha Title", "metrics": {"views": 10}},
        ),
    )
    merge_provider_result(
        record,
        ProviderResult(
            provider="arxiv",
            status="success",
            data={"title": "Canonical Title", "canonical_id": "2301.12345"},
        ),
    )
    finalize_record(record)
    assert record.title == "Canonical Title"
    assert record.metrics["views"] == 10


def test_mentions_merge_sets_count() -> None:
    record = PaperRecord(input="2301.12345")
    merge_provider_result(
        record,
        ProviderResult(
            provider="alphaxiv_mentions",
            status="success",
            data={"mentions": [{"title": "Blog post"}], "metrics": {"mentions_count": 1}},
        ),
    )
    assert record.metrics["mentions_count"] == 1
