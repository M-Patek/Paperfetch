from __future__ import annotations

from .merge import finalize_record, merge_provider_result
from .models import PaperRecord
from .normalize import normalize_input
from .providers import (
    AlphaXivHtmlProvider,
    AlphaXivMentionsProvider,
    ArxivProvider,
    ExperimentalAlphaXivBrowserProvider,
)
from .providers.base import ProviderResult


def extract(input: str, *, enrich_alpha: bool = True, browser: bool = False) -> PaperRecord:
    normalized = normalize_input(input)
    record = PaperRecord(
        input=input,
        canonical_id=normalized.canonical_id,
        versioned_id=normalized.versioned_id,
        abs_url=normalized.abs_url,
        pdf_url=normalized.pdf_url,
        alphaxiv_url=normalized.alphaxiv_url,
    )

    arxiv_provider = ArxivProvider()
    alpha_provider = AlphaXivHtmlProvider()
    mentions_provider = AlphaXivMentionsProvider()
    browser_provider = ExperimentalAlphaXivBrowserProvider()

    merge_provider_result(record, arxiv_provider.fetch(normalized))

    if enrich_alpha:
        alpha_result = alpha_provider.fetch(normalized)
        merge_provider_result(record, alpha_result)

        if not record.canonical_id and alpha_result.data.get("canonical_id"):
            normalized = normalize_input(alpha_result.data["canonical_id"])
            merge_provider_result(record, arxiv_provider.fetch(normalized))

        group_id = alpha_result.details.get("group_id")
        if group_id:
            merge_provider_result(record, mentions_provider.fetch(group_id))
        else:
            merge_provider_result(
                record,
                ProviderResult(
                    provider="alphaxiv_mentions",
                    status="skipped",
                    details={"reason": "no_group_id"},
                ),
            )

        if browser:
            merge_provider_result(record, browser_provider.fetch(record.alphaxiv_url))
    else:
        merge_provider_result(
            record,
            ProviderResult(
                provider="alphaxiv_html",
                status="skipped",
                details={"reason": "disabled"},
            ),
        )
        merge_provider_result(
            record,
            ProviderResult(
                provider="alphaxiv_mentions",
                status="skipped",
                details={"reason": "disabled"},
            ),
        )

    return finalize_record(record)


def batch_extract(inputs: list[str], *, enrich_alpha: bool = True, browser: bool = False) -> list[PaperRecord]:
    return [extract(item, enrich_alpha=enrich_alpha, browser=browser) for item in inputs]
