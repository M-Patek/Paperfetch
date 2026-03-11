from paperfetch.service import extract


def test_extract_with_stubbed_providers(monkeypatch) -> None:
    monkeypatch.setattr(
        "paperfetch.providers.arxiv.fetch_text",
        lambda url: """<?xml version="1.0" encoding="UTF-8"?><feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom"><entry><id>http://arxiv.org/abs/2301.12345v1</id><updated>2023-01-31T00:00:00Z</updated><published>2023-01-29T03:59:33Z</published><title>Canonical Title</title><summary>Summary</summary><author><name>Alice</name></author><link title="pdf" href="https://arxiv.org/pdf/2301.12345v1.pdf" /><arxiv:primary_category term="cs.CL" /><category term="cs.CL" /></entry></feed>""",
    )
    monkeypatch.setattr(
        "paperfetch.providers.alphaxiv.fetch_text",
        lambda url, timeout=20, headers=None: """<html><head><meta property="og:image" content="https://example.com/image.png"><script type="application/ld+json">{"headline": "Alpha Title", "abstract": "Alpha Summary", "author":[{"name":"Alice"}], "citation":{"identifier":"0185fbae-2888-7197-8590-e777925799e8"}, "interactionStatistic":[{"interactionType":{"url":"https://schema.org/ViewAction"},"userInteractionCount":15},{"interactionType":{"url":"https://schema.org/LikeAction"},"userInteractionCount":2}]}</script></head><body>https://fetcher.alphaxiv.org/v2/pdf/2301.12345v1.pdf</body></html>""",
    )
    monkeypatch.setattr(
        "paperfetch.providers.alphaxiv.fetch_json",
        lambda url, timeout=20, headers=None: {"mentions": [{"title": "Mention"}]},
    )

    record = extract("https://www.alphaxiv.org/abs/2301.12345")
    assert record.canonical_id == "2301.12345"
    assert record.title == "Canonical Title"
    assert record.metrics["views"] == 15
    assert record.metrics["mentions_count"] == 1
