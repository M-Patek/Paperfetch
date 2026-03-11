from __future__ import annotations

from typing import Any

from .models import PaperRecord, ProviderTrace
from .providers.base import ProviderResult

ARXIV_CANONICAL_FIELDS = {
    "canonical_id",
    "versioned_id",
    "title",
    "abstract",
    "authors",
    "published_at",
    "updated_at",
    "categories",
    "primary_category",
    "pdf_url",
    "abs_url",
    "license",
    "bibtex",
}


def merge_provider_result(record: PaperRecord, result: ProviderResult) -> None:
    if result.status == "success":
        if result.provider == "arxiv":
            _merge_authoritative(record, result.data)
        else:
            _merge_enrichment(record, result.data)

    trace = ProviderTrace(
        provider=result.provider,
        status=result.status,
        fields=sorted(result.data.keys()),
        warnings=result.warnings,
        details=result.details,
    )
    record.provider_trace.append(trace)
    for warning in result.warnings:
        if warning not in record.warnings:
            record.warnings.append(warning)


def finalize_record(record: PaperRecord) -> PaperRecord:
    if record.canonical_id and not record.abs_url:
        record.abs_url = f"https://arxiv.org/abs/{record.versioned_id or record.canonical_id}"
    if record.canonical_id and not record.pdf_url:
        record.pdf_url = f"https://arxiv.org/pdf/{record.versioned_id or record.canonical_id}.pdf"
    if record.canonical_id and not record.alphaxiv_url:
        record.alphaxiv_url = f"https://www.alphaxiv.org/abs/{record.canonical_id}"
    record.metrics.setdefault("views", None)
    record.metrics.setdefault("likes", None)
    record.metrics["mentions_count"] = len(record.mentions)
    return record


def _merge_authoritative(record: PaperRecord, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if value in (None, "", []):
            continue
        if key == "metrics":
            record.metrics.update(
                {
                    metric_key: metric_value
                    for metric_key, metric_value in value.items()
                    if metric_value is not None
                }
            )
            continue
        setattr(record, key, value)


def _merge_enrichment(record: PaperRecord, data: dict[str, Any]) -> None:
    for key, value in data.items():
        if value in (None, "", []):
            continue
        if key == "metrics":
            for metric_key, metric_value in value.items():
                if metric_value is None:
                    continue
                if metric_key == "mentions_count":
                    record.metrics[metric_key] = metric_value
                elif record.metrics.get(metric_key) is None:
                    record.metrics[metric_key] = metric_value
            continue
        if key == "mentions":
            record.mentions = value
            record.metrics["mentions_count"] = len(value)
            continue
        current = getattr(record, key, None)
        if key in ARXIV_CANONICAL_FIELDS and current not in (None, "", []):
            continue
        if current in (None, "", []):
            setattr(record, key, value)
