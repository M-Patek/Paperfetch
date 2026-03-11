from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import quote

from ..http import FetchError, fetch_text
from ..normalize import NormalizedInput
from .base import ProviderResult

ATOM_NS = {"atom": "http://www.w3.org/2005/Atom", "arxiv": "http://arxiv.org/schemas/atom"}


class ArxivProvider:
    name = "arxiv"

    def fetch(self, normalized: NormalizedInput) -> ProviderResult:
        if not normalized.canonical_id:
            return ProviderResult(provider=self.name, status="skipped", warnings=["No canonical arXiv ID available."])

        url = f"http://export.arxiv.org/api/query?id_list={quote(normalized.canonical_id)}"
        try:
            feed = fetch_text(url)
        except FetchError as exc:
            return ProviderResult(provider=self.name, status="failed", warnings=[f"arXiv fetch failed: {exc}"], details={"url": url})

        try:
            data = parse_arxiv_atom(feed)
        except Exception as exc:  # pragma: no cover
            return ProviderResult(provider=self.name, status="failed", warnings=[f"arXiv parse failed: {exc}"], details={"url": url})

        if not data:
            return ProviderResult(provider=self.name, status="failed", warnings=["arXiv entry not found."], details={"url": url})

        return ProviderResult(provider=self.name, status="success", data=data, details={"url": url})


def parse_arxiv_atom(feed: str) -> dict[str, Any]:
    root = ET.fromstring(feed)
    entry = root.find("atom:entry", ATOM_NS)
    if entry is None:
        return {}

    entry_id = _node_text(entry.find("atom:id", ATOM_NS))
    versioned_id = entry_id.rsplit("/", 1)[-1] if entry_id else None
    canonical_id = re.sub(r"v\d+$", "", versioned_id or "")
    title = _clean_space(_node_text(entry.find("atom:title", ATOM_NS)))
    abstract = _clean_space(_node_text(entry.find("atom:summary", ATOM_NS)))
    authors = [
        author
        for author in (
            _clean_space(_node_text(node.find("atom:name", ATOM_NS)))
            for node in entry.findall("atom:author", ATOM_NS)
        )
        if author is not None
    ]
    categories = [node.attrib.get("term") for node in entry.findall("atom:category", ATOM_NS) if node.attrib.get("term")]
    primary_category = entry.find("arxiv:primary_category", ATOM_NS)
    published = _normalize_datetime(_node_text(entry.find("atom:published", ATOM_NS)))
    updated = _normalize_datetime(_node_text(entry.find("atom:updated", ATOM_NS)))
    license_node = entry.find("arxiv:license", ATOM_NS)
    pdf_url = None
    for link in entry.findall("atom:link", ATOM_NS):
        if link.attrib.get("title") == "pdf":
            pdf_url = link.attrib.get("href")
            break
    if pdf_url and not pdf_url.endswith(".pdf"):
        pdf_url = f"{pdf_url}.pdf"

    primary_category_term = primary_category.attrib.get("term") if primary_category is not None else (categories[0] if categories else None)

    return {
        "canonical_id": canonical_id or None,
        "versioned_id": versioned_id,
        "title": title,
        "abstract": abstract,
        "authors": authors,
        "published_at": published,
        "updated_at": updated,
        "categories": categories,
        "primary_category": primary_category_term,
        "pdf_url": pdf_url or (f"https://arxiv.org/pdf/{versioned_id or canonical_id}.pdf" if canonical_id else None),
        "abs_url": f"https://arxiv.org/abs/{versioned_id or canonical_id}" if canonical_id else None,
        "license": _node_text(license_node),
        "bibtex": synthesize_bibtex(
            canonical_id=canonical_id or None,
            title=title,
            authors=authors,
            published_at=published,
            primary_category=primary_category_term,
        ),
    }


def synthesize_bibtex(
    *,
    canonical_id: str | None,
    title: str | None,
    authors: list[str],
    published_at: str | None,
    primary_category: str | None,
) -> str | None:
    if not canonical_id or not title:
        return None
    year = published_at[:4] if published_at else "unknown"
    key_author = authors[0].split()[-1].lower() if authors else "paper"
    key = f"{key_author}{year}{canonical_id.replace('/', '')}"
    author_block = " and ".join(authors) if authors else "Unknown"
    primary_class = primary_category or "unknown"
    return (
        f"@misc{{{key},\n"
        f"  title = {{{title}}},\n"
        f"  author = {{{author_block}}},\n"
        f"  year = {{{year}}},\n"
        f"  eprint = {{{canonical_id}}},\n"
        f"  archivePrefix = {{arXiv}},\n"
        f"  primaryClass = {{{primary_class}}},\n"
        f"  url = {{https://arxiv.org/abs/{canonical_id}}}\n"
        f"}}"
    )


def _node_text(node: ET.Element | None) -> str | None:
    if node is None or node.text is None:
        return None
    return node.text.strip()


def _clean_space(value: str | None) -> str | None:
    if value is None:
        return None
    return " ".join(value.split())


def _normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).isoformat().replace("+00:00", "Z")
    except ValueError:
        try:
            return parsedate_to_datetime(value).astimezone(UTC).isoformat().replace("+00:00", "Z")
        except (TypeError, ValueError):
            return value
