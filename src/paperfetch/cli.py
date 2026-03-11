from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Iterable
from pathlib import Path

from .service import batch_extract, extract


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="paperfetch", description="Extract structured paper metadata from arXiv and alphaXiv.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    extract_parser = subparsers.add_parser("extract", help="Extract a single record.")
    extract_parser.add_argument("input", help="arXiv ID, arXiv URL, or alphaXiv URL")
    extract_parser.add_argument("--format", choices=["json", "md"], default="json")
    extract_parser.add_argument("--output", help="Write output to a file instead of stdout")
    extract_parser.add_argument("--no-alpha", action="store_true", help="Disable alphaXiv enrichment")
    extract_parser.add_argument("--browser", action="store_true", help="Enable experimental Playwright enhancement")

    batch_parser = subparsers.add_parser("batch", help="Extract a batch of records from a text file.")
    batch_parser.add_argument("file", help="Text file containing one paper input per line")
    batch_parser.add_argument("--format", choices=["ndjson", "json"], default="ndjson")
    batch_parser.add_argument("--output", help="Write output to a file instead of stdout")
    batch_parser.add_argument("--no-alpha", action="store_true", help="Disable alphaXiv enrichment")
    batch_parser.add_argument("--browser", action="store_true", help="Enable experimental Playwright enhancement")

    serve_parser = subparsers.add_parser("serve", help="Run the local demo app.")
    serve_parser.add_argument("--host", default="127.0.0.1")
    serve_parser.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "extract":
        record = extract(args.input, enrich_alpha=not args.no_alpha, browser=args.browser)
        output = record.to_json() if args.format == "json" else record.to_markdown()
        _write_output(output, args.output)
        return 0

    if args.command == "batch":
        lines = [line for line in _read_inputs(Path(args.file)) if line]
        records = batch_extract(lines, enrich_alpha=not args.no_alpha, browser=args.browser)
        if args.format == "json":
            output = json.dumps([record.to_dict() for record in records], indent=2, ensure_ascii=False)
        else:
            output = "\n".join(record.to_json(indent=None) for record in records)
        _write_output(output, args.output)
        return 0

    if args.command == "serve":
        try:
            import uvicorn
        except ImportError as exc:
            parser.error("`paperfetch serve` requires demo dependencies. Install with `pip install -e \".[demo]\"`.")
            raise SystemExit(2) from exc
        uvicorn.run("paperfetch.demo.app:app", host=args.host, port=args.port, reload=False)
        return 0

    parser.error("unknown command")
    return 2


def _read_inputs(path: Path) -> Iterable[str]:
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


def _write_output(output: str, target: str | None) -> None:
    if target:
        path = Path(target)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(output, encoding="utf-8")
    else:
        sys.stdout.buffer.write(output.encode("utf-8"))
        if not output.endswith("\n"):
            sys.stdout.buffer.write(b"\n")
