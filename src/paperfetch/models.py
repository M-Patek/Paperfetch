from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass
class ProviderTrace:
    provider: str
    status: str
    fields: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class PaperRecord:
    input: str
    canonical_id: str | None = None
    versioned_id: str | None = None
    title: str | None = None
    abstract: str | None = None
    authors: list[str] = field(default_factory=list)
    published_at: str | None = None
    updated_at: str | None = None
    categories: list[str] = field(default_factory=list)
    primary_category: str | None = None
    pdf_url: str | None = None
    abs_url: str | None = None
    alphaxiv_url: str | None = None
    bibtex: str | None = None
    license: str | None = None
    metrics: dict[str, int | None] = field(
        default_factory=lambda: {"views": None, "likes": None, "mentions_count": 0}
    )
    discussion_url: str | None = None
    mentions: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    provider_trace: list[ProviderTrace] = field(default_factory=list)
    image_url: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    def to_json(self, *, indent: int | None = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def to_markdown(self) -> str:
        title = self.title or self.canonical_id or "Untitled paper"
        authors = ", ".join(self.authors) if self.authors else "Unknown authors"
        categories = ", ".join(self.categories) if self.categories else "Unknown"
        warnings = "\n".join(f"- {warning}" for warning in self.warnings) or "- None"
        links = []
        if self.abs_url:
            links.append(f"- arXiv abstract: {self.abs_url}")
        if self.pdf_url:
            links.append(f"- PDF: {self.pdf_url}")
        if self.alphaxiv_url:
            links.append(f"- alphaXiv: {self.alphaxiv_url}")
        if self.discussion_url:
            links.append(f"- Discussion: {self.discussion_url}")
        links_block = "\n".join(links) or "- None"

        mentions_block = "\n".join(
            f"- {mention.get('title') or mention.get('url') or json.dumps(mention, ensure_ascii=False)}"
            for mention in self.mentions[:10]
        ) or "- None"

        bibtex_block = self.bibtex or "Not available"

        return (
            f"# {title}\n\n"
            f"## Authors\n\n{authors}\n\n"
            f"## Abstract\n\n{self.abstract or 'Not available'}\n\n"
            f"## Metadata\n\n"
            f"- Canonical ID: {self.canonical_id or 'Unknown'}\n"
            f"- Versioned ID: {self.versioned_id or 'Unknown'}\n"
            f"- Published: {self.published_at or 'Unknown'}\n"
            f"- Updated: {self.updated_at or 'Unknown'}\n"
            f"- Primary category: {self.primary_category or 'Unknown'}\n"
            f"- Categories: {categories}\n"
            f"- License: {self.license or 'Unknown'}\n"
            f"- Views: {self.metrics.get('views')}\n"
            f"- Likes: {self.metrics.get('likes')}\n"
            f"- Mentions: {self.metrics.get('mentions_count')}\n\n"
            f"## Links\n\n{links_block}\n\n"
            f"## Mentions\n\n{mentions_block}\n\n"
            f"## BibTeX\n\n```bibtex\n{bibtex_block}\n```\n\n"
            f"## Warnings\n\n{warnings}\n"
        )
