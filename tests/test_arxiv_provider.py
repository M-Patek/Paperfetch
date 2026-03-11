from pathlib import Path

from paperfetch.providers.arxiv import parse_arxiv_atom


def test_parse_arxiv_atom_fixture() -> None:
    fixture = Path("tests/fixtures/arxiv_feed.xml").read_text(encoding="utf-8")
    data = parse_arxiv_atom(fixture)
    assert data["canonical_id"] == "2301.12345"
    assert data["versioned_id"] == "2301.12345v1"
    assert data["primary_category"] == "physics.bio-ph"
    assert data["authors"][1] == "Andrej Košmrlj"
    assert "archivePrefix = {arXiv}" in data["bibtex"]
