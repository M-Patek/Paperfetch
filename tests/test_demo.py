from __future__ import annotations

from fastapi.testclient import TestClient

from paperfetch.demo.app import app
from paperfetch.models import PaperRecord


def sample_record() -> PaperRecord:
    return PaperRecord(
        input="2301.12345",
        canonical_id="2301.12345",
        versioned_id="2301.12345v1",
        title="Sample Paper",
        authors=["Alice Example"],
        primary_category="cs.CL",
    )


def test_demo_healthz() -> None:
    client = TestClient(app)
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_demo_extract(monkeypatch) -> None:
    client = TestClient(app)
    monkeypatch.setattr("paperfetch.demo.app.extract", lambda *args, **kwargs: sample_record())

    response = client.post("/api/extract", json={"input": "2301.12345"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["record"]["canonical_id"] == "2301.12345"
    assert payload["markdown"].startswith("# Sample Paper")


def test_demo_requires_input() -> None:
    client = TestClient(app)
    response = client.post("/api/extract", json={"input": ""})
    assert response.status_code == 400
