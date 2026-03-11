# Contributing

Thanks for contributing to `paperfetch`.

## Development Setup

```bash
pip install -e ".[dev,demo]"
```

## Required Checks

Run these before opening a pull request:

```bash
python -m pytest
python -m ruff check .
python -m mypy src
python -m build --no-isolation
```

## Contribution Guidelines

- keep user-facing behavior aligned across the CLI, Python API, and demo
- prefer stable public contracts over provider-specific shortcuts
- preserve the arXiv-first / alphaXiv-enrichment precedence model
- add or update fixtures when provider behavior changes
- document public-facing changes in `README.md`, `docs/`, and `CHANGELOG.md`

## Pull Requests

- describe the user-facing change
- call out schema or CLI contract changes explicitly
- include tests for new behavior
- include screenshots when the demo or docs visuals change
