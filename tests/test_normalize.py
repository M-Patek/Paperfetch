from paperfetch.normalize import normalize_input


def test_normalize_plain_identifier() -> None:
    normalized = normalize_input("2301.12345v1")
    assert normalized.canonical_id == "2301.12345"
    assert normalized.versioned_id == "2301.12345v1"
    assert normalized.alphaxiv_url == "https://www.alphaxiv.org/abs/2301.12345"


def test_normalize_alphaxiv_url() -> None:
    normalized = normalize_input("https://www.alphaxiv.org/abs/2301.12345")
    assert normalized.input_kind == "alphaxiv_url"
    assert normalized.canonical_id == "2301.12345"
