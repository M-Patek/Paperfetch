# Docs

`paperfetch` is a source-installable Python project that turns arXiv and alphaXiv inputs into normalized JSON records and Markdown dossiers.

## Read This First

- [Architecture](architecture.md)
- [Schema and output contract](schema.md)
- [FAQ](faq.md)
- [Roadmap](roadmap.md)
- [中文文档](zh/README.md)

## Audience

- AI agent developers building paper-aware automations
- application developers who need a clean metadata layer
- research engineers who want reproducible paper dossiers

## Main Interfaces

- Python API: `extract(...)`, `batch_extract(...)`
- CLI: `paperfetch extract`, `paperfetch batch`, `paperfetch serve`
- Outputs: JSON record, Markdown dossier, provider provenance
