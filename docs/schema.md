# Schema And Output Contract

The public record shape is defined by `PaperRecord`.

## Core Fields

- `input`: original user input
- `canonical_id`: normalized arXiv identifier without version suffix
- `versioned_id`: version-aware identifier when available
- `title`, `abstract`, `authors`
- `published_at`, `updated_at`
- `categories`, `primary_category`
- `pdf_url`, `abs_url`, `alphaxiv_url`
- `bibtex`, `license`

## Enrichment Fields

- `metrics.views`
- `metrics.likes`
- `metrics.mentions_count`
- `discussion_url`
- `mentions`
- `image_url`

## Provenance Fields

- `warnings`: human-readable extraction warnings
- `provider_trace`: ordered provider execution records

Each `provider_trace` item includes:

- `provider`
- `status`
- `fields`
- `warnings`
- `details`

## Stability

- the Python API and CLI entrypoints are public
- the record schema is stable for `0.1.x`, but new fields may be added over time
- provider-specific `details` are informative and may change more frequently than top-level fields
