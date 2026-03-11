from __future__ import annotations

from html.parser import HTMLParser


class MetadataHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.meta: dict[str, str] = {}
        self.json_ld_blocks: list[str] = []
        self._script_type: str | None = None
        self._script_buffer: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attr_map = {key.lower(): value for key, value in attrs}
        if tag.lower() == "meta":
            key = attr_map.get("property") or attr_map.get("name")
            content = attr_map.get("content")
            if key and content:
                self.meta[key] = content
        if tag.lower() == "script":
            self._script_type = (attr_map.get("type") or "").lower()
            self._script_buffer = []

    def handle_data(self, data: str) -> None:
        if self._script_type == "application/ld+json":
            self._script_buffer.append(data)

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "script":
            if self._script_type == "application/ld+json":
                content = "".join(self._script_buffer).strip()
                if content:
                    self.json_ld_blocks.append(content)
            self._script_type = None
            self._script_buffer = []
