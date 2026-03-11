from __future__ import annotations

import json
from datetime import UTC, datetime
from typing import Any

from ..html_utils import MetadataHTMLParser
from ..http import FetchError, fetch_json, fetch_text
from ..normalize import UUID_PATTERN, NormalizedInput, extract_arxiv_id
from .base import ProviderResult

VIEW_ACTION = "ViewAction"
LIKE_ACTION = "LikeAction"


class AlphaXivHtmlProvider:
    name = "alphaxiv_html"

    def fetch(self, normalized: NormalizedInput) -> ProviderResult:
        target_url = normalized.alphaxiv_url
        if not target_url and normalized.canonical_id:
            target_url = f"https://www.alphaxiv.org/abs/{normalized.canonical_id}"
        if not target_url and normalized.alphaxiv_token:
            target_url = f"https://www.alphaxiv.org/abs/{normalized.alphaxiv_token}"
        if not target_url:
            return ProviderResult(provider=self.name, status="skipped", warnings=["No alphaXiv target URL available."])

        try:
            html = fetch_text(target_url)
        except FetchError as exc:
            return ProviderResult(provider=self.name, status="failed", warnings=[f"alphaXiv fetch failed: {exc}"], details={"url": target_url})

        parser = MetadataHTMLParser()
        parser.feed(html)
        json_ld = _first_json_ld(parser.json_ld_blocks)
        discovered_canonical, discovered_versioned = extract_arxiv_id(html)
        group_id = _extract_group_id(json_ld, html)

        data: dict[str, Any] = {
            "alphaxiv_url": target_url,
            "image_url": parser.meta.get("og:image"),
        }
        warnings: list[str] = []

        if json_ld:
            authors = [
                author.get("name")
                for author in json_ld.get("author", [])
                if isinstance(author, dict) and author.get("name")
            ]
            views, likes = _extract_metrics(json_ld.get("interactionStatistic", []))
            data.update(
                {
                    "title": json_ld.get("headline"),
                    "abstract": json_ld.get("abstract"),
                    "authors": authors,
                    "published_at": _normalize_datetime(json_ld.get("datePublished")),
                    "discussion_url": json_ld.get("discussionUrl") or json_ld.get("url"),
                    "metrics": {
                        "views": views,
                        "likes": likes,
                    },
                }
            )
        else:
            warnings.append("No JSON-LD block found on alphaXiv page.")

        if discovered_canonical:
            data["canonical_id"] = discovered_canonical
        if discovered_versioned:
            data["versioned_id"] = discovered_versioned
            data.setdefault("pdf_url", f"https://arxiv.org/pdf/{discovered_versioned}.pdf")
            data.setdefault("abs_url", f"https://arxiv.org/abs/{discovered_versioned}")

        return ProviderResult(
            provider=self.name,
            status="success",
            data=data,
            warnings=warnings,
            details={"url": target_url, "group_id": group_id},
        )


class AlphaXivMentionsProvider:
    name = "alphaxiv_mentions"

    def fetch(self, group_id: str | None) -> ProviderResult:
        if not group_id:
            return ProviderResult(provider=self.name, status="skipped", warnings=["No alphaXiv group ID available."])
        url = f"https://api.alphaxiv.org/papers/v3/x-mentions-db/{group_id}"
        try:
            payload = fetch_json(url)
        except FetchError as exc:
            return ProviderResult(provider=self.name, status="failed", warnings=[f"alphaXiv mentions fetch failed: {exc}"], details={"url": url})
        mentions = payload.get("mentions", []) if isinstance(payload, dict) else []
        return ProviderResult(
            provider=self.name,
            status="success",
            data={"mentions": mentions, "metrics": {"mentions_count": len(mentions)}},
            details={"url": url, "group_id": group_id},
        )


class ExperimentalAlphaXivBrowserProvider:
    name = "alphaxiv_browser"

    def fetch(self, target_url: str | None) -> ProviderResult:
        if not target_url:
            return ProviderResult(provider=self.name, status="skipped", warnings=["No alphaXiv target URL available."])
        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            return ProviderResult(
                provider=self.name,
                status="failed",
                warnings=["Playwright is not installed. Install with `pip install -e \".[browser]\"`."],
            )

        details: dict[str, Any] = {"url": target_url, "network_hints": []}
        try:
            with sync_playwright() as playwright:
                browser = playwright.chromium.launch(headless=True)
                page = browser.new_page()
                page.on("response", lambda response: _capture_network_hint(response.url, details["network_hints"]))
                page.goto(target_url, wait_until="networkidle", timeout=30000)
                rendered_json_ld = page.eval_on_selector(
                    "script[type='application/ld+json']",
                    "node => node ? node.textContent : null",
                )
                browser.close()
        except Exception as exc:
            return ProviderResult(
                provider=self.name,
                status="failed",
                warnings=[f"Playwright alphaXiv inspection failed: {exc}"],
                details=details,
            )

        data: dict[str, Any] = {}
        if rendered_json_ld:
            try:
                payload = json.loads(rendered_json_ld)
                views, likes = _extract_metrics(payload.get("interactionStatistic", []))
                data["metrics"] = {"views": views, "likes": likes}
            except json.JSONDecodeError:
                pass
        return ProviderResult(provider=self.name, status="success", data=data, details=details)


def _capture_network_hint(url: str, sink: list[str]) -> None:
    if "api.alphaxiv.org" in url and url not in sink:
        sink.append(url)


def _first_json_ld(blocks: list[str]) -> dict[str, Any] | None:
    for block in blocks:
        try:
            payload = json.loads(block)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _extract_group_id(json_ld: dict[str, Any] | None, html: str) -> str | None:
    if json_ld:
        citation = json_ld.get("citation")
        if isinstance(citation, dict) and isinstance(citation.get("identifier"), str):
            return citation["identifier"]
        if isinstance(json_ld.get("url"), str):
            match = UUID_PATTERN.search(json_ld["url"])
            if match:
                return match.group(0)
    match = UUID_PATTERN.search(html)
    return match.group(0) if match else None


def _extract_metrics(interaction_stats: list[dict[str, Any]]) -> tuple[int | None, int | None]:
    views = None
    likes = None
    for item in interaction_stats:
        if not isinstance(item, dict):
            continue
        interaction_type = item.get("interactionType")
        if isinstance(interaction_type, dict):
            url = interaction_type.get("url", "")
            if VIEW_ACTION in url:
                views = item.get("userInteractionCount")
            if LIKE_ACTION in url:
                likes = item.get("userInteractionCount")
    return views, likes


def _normalize_datetime(value: str | None) -> str | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(UTC).isoformat().replace("+00:00", "Z")
    except ValueError:
        for fmt in ("%a %b %d %Y %H:%M:%S GMT%z (%Z)", "%a %b %d %Y %H:%M:%S GMT+0000 (Coordinated Universal Time)"):
            try:
                parsed = datetime.strptime(value, fmt)
                if parsed.tzinfo is None:
                    parsed = parsed.replace(tzinfo=UTC)
                return parsed.astimezone(UTC).isoformat().replace("+00:00", "Z")
            except ValueError:
                continue
        return value
