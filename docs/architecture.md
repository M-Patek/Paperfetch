# Architecture

`paperfetch` is organized as a small provider pipeline with a normalized output model.

## Flow

1. `normalize_input(...)` converts an identifier or URL into a canonical internal representation.
2. `ArxivProvider` fetches canonical metadata from the arXiv Atom API.
3. `AlphaXivHtmlProvider` optionally extracts enrichment data from page HTML and JSON-LD.
4. `AlphaXivMentionsProvider` optionally adds mentions when a usable alphaXiv group ID exists.
5. `ExperimentalAlphaXivBrowserProvider` is opt-in and only runs when browser mode is requested.
6. Merge logic resolves precedence and writes `provider_trace` plus `warnings`.

## Precedence

- arXiv is authoritative for identifiers, categories, dates, and PDF links
- alphaXiv only fills missing fields or adds auxiliary fields
- browser-mode data is always enrichment, never canonical truth

## Error Model

- provider failures do not crash extraction by default
- failed or skipped providers append structured trace entries
- callers should inspect `warnings` and `provider_trace` before assuming completeness

## Design Constraints

- metadata first, not full PDF parsing
- explicit provenance over silent guessing
- usable from CLI, Python, and lightweight web surfaces
