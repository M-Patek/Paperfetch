# FAQ

## Why not use alphaXiv as the only source?

Because alphaXiv is valuable for enrichment, but arXiv remains the canonical metadata source. `paperfetch` is designed to degrade gracefully when alphaXiv is slow or unavailable.

## Why is browser mode experimental?

Because browser mode depends on runtime behavior that is harder to guarantee than API or HTML parsing. It is useful for exploration, not for the canonical pipeline.

## Does this parse PDFs into sections?

No. `paperfetch` intentionally focuses on identifiers, metadata, and Markdown dossiers.

## Why keep `warnings` instead of hiding failures?

Because downstream agents need to know whether a field is missing because the paper lacked it or because a provider failed.
