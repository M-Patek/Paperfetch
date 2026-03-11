from __future__ import annotations

import re
from dataclasses import dataclass
from urllib.parse import urlparse

NEW_STYLE_ID = re.compile(r"(?P<canonical>\d{4}\.\d{4,5})(?P<version>v\d+)?", re.IGNORECASE)
OLD_STYLE_ID = re.compile(
    r"(?P<canonical>[a-z\-]+(?:\.[a-z\-]+)?/\d{7})(?P<version>v\d+)?",
    re.IGNORECASE,
)
UUID_PATTERN = re.compile(
    r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
    re.IGNORECASE,
)


@dataclass
class NormalizedInput:
    raw_input: str
    input_kind: str
    canonical_id: str | None = None
    versioned_id: str | None = None
    alphaxiv_url: str | None = None
    abs_url: str | None = None
    pdf_url: str | None = None
    alphaxiv_token: str | None = None


def normalize_input(raw_input: str) -> NormalizedInput:
    raw_input = raw_input.strip()
    if raw_input.startswith("http://") or raw_input.startswith("https://"):
        return _normalize_url(raw_input)
    return _normalize_identifier(raw_input)


def extract_arxiv_id(value: str) -> tuple[str | None, str | None]:
    for pattern in (NEW_STYLE_ID, OLD_STYLE_ID):
        match = pattern.search(value)
        if match:
            canonical = match.group("canonical")
            version = match.group("version")
            versioned = f"{canonical}{version}" if version else None
            return canonical, versioned
    return None, None


def _normalize_identifier(raw_input: str) -> NormalizedInput:
    canonical_id, versioned_id = extract_arxiv_id(raw_input)
    return NormalizedInput(
        raw_input=raw_input,
        input_kind="identifier" if canonical_id else "unknown",
        canonical_id=canonical_id,
        versioned_id=versioned_id,
        alphaxiv_url=f"https://www.alphaxiv.org/abs/{canonical_id}" if canonical_id else None,
        abs_url=f"https://arxiv.org/abs/{versioned_id or canonical_id}" if canonical_id else None,
        pdf_url=f"https://arxiv.org/pdf/{versioned_id or canonical_id}.pdf" if canonical_id else None,
        alphaxiv_token=raw_input if UUID_PATTERN.fullmatch(raw_input) else None,
    )


def _normalize_url(raw_input: str) -> NormalizedInput:
    parsed = urlparse(raw_input)
    host = parsed.netloc.lower()
    path = parsed.path.strip("/")
    canonical_id, versioned_id = extract_arxiv_id(raw_input)
    token = path.split("/")[-1] if path else None

    if "alphaxiv.org" in host:
        return NormalizedInput(
            raw_input=raw_input,
            input_kind="alphaxiv_url",
            canonical_id=canonical_id,
            versioned_id=versioned_id,
            alphaxiv_url=raw_input,
            abs_url=f"https://arxiv.org/abs/{versioned_id or canonical_id}" if canonical_id else None,
            pdf_url=f"https://arxiv.org/pdf/{versioned_id or canonical_id}.pdf" if canonical_id else None,
            alphaxiv_token=token,
        )

    if "arxiv.org" in host or "export.arxiv.org" in host:
        return NormalizedInput(
            raw_input=raw_input,
            input_kind="arxiv_url",
            canonical_id=canonical_id,
            versioned_id=versioned_id,
            alphaxiv_url=f"https://www.alphaxiv.org/abs/{canonical_id}" if canonical_id else None,
            abs_url=f"https://arxiv.org/abs/{versioned_id or canonical_id}" if canonical_id else raw_input,
            pdf_url=f"https://arxiv.org/pdf/{versioned_id or canonical_id}.pdf" if canonical_id else None,
        )

    return NormalizedInput(raw_input=raw_input, input_kind="url")
