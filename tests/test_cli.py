from __future__ import annotations

import json
import shutil
import uuid
from pathlib import Path

import pytest

from paperfetch import cli
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


def make_local_tmp_dir() -> Path:
    root = Path(".test-output")
    root.mkdir(exist_ok=True)
    path = root / f"cli-{uuid.uuid4().hex}"
    path.mkdir()
    return path


def test_cli_extract_to_stdout(monkeypatch, capfd) -> None:
    monkeypatch.setattr("paperfetch.cli.extract", lambda *args, **kwargs: sample_record())

    exit_code = cli.main(["extract", "2301.12345", "--format", "json"])

    assert exit_code == 0
    stdout = capfd.readouterr().out
    payload = json.loads(stdout)
    assert payload["canonical_id"] == "2301.12345"


def test_cli_help(capsys) -> None:
    with pytest.raises(SystemExit) as exc_info:
        cli.main(["--help"])

    assert exc_info.value.code == 0
    assert "Extract structured paper metadata" in capsys.readouterr().out


def test_cli_extract_to_file(monkeypatch) -> None:
    temp_dir = make_local_tmp_dir()
    output_path = temp_dir / "record.md"
    monkeypatch.setattr("paperfetch.cli.extract", lambda *args, **kwargs: sample_record())

    try:
        exit_code = cli.main(["extract", "2301.12345", "--format", "md", "--output", str(output_path)])
        assert exit_code == 0
        assert output_path.exists()
        assert output_path.read_text(encoding="utf-8").startswith("# Sample Paper")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_cli_batch_ndjson(monkeypatch, capfd) -> None:
    temp_dir = make_local_tmp_dir()
    input_file = temp_dir / "papers.txt"
    input_file.write_text("2301.12345\n2401.00001\n", encoding="utf-8")
    monkeypatch.setattr(
        "paperfetch.cli.batch_extract",
        lambda *args, **kwargs: [sample_record(), sample_record()],
    )

    try:
        exit_code = cli.main(["batch", str(input_file), "--format", "ndjson"])
        assert exit_code == 0
        stdout = capfd.readouterr().out.strip().splitlines()
        assert len(stdout) == 2
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
