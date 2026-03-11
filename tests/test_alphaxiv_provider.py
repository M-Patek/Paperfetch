from pathlib import Path

from paperfetch.normalize import normalize_input
from paperfetch.providers.alphaxiv import AlphaXivHtmlProvider


def test_parse_alphaxiv_html_fixture(monkeypatch) -> None:
    html = Path("tests/fixtures/alphaxiv_2301.12345.html").read_text(encoding="utf-8")

    def fake_fetch_text(url: str, *, timeout: int = 20, headers=None) -> str:
        return html

    monkeypatch.setattr("paperfetch.providers.alphaxiv.fetch_text", fake_fetch_text)

    provider = AlphaXivHtmlProvider()
    result = provider.fetch(normalize_input("https://www.alphaxiv.org/abs/2301.12345"))

    assert result.status == "success"
    assert result.data["canonical_id"] == "2301.12345"
    assert result.data["versioned_id"] == "2301.12345v1"
    assert result.data["metrics"]["views"] == 223
    assert result.details["group_id"] == "0185fbae-2888-7197-8590-e777925799e8"
