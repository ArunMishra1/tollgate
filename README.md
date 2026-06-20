# tollgate

> **Placeholder.** This is scaffolding, not the real README. The actual
> README needs to be written by Arun, in Arun's voice, per the project's
> writing rules — no AI-generated filler, no invented case studies, every
> technical concept anchored to a real scenario before code/jargon shows
> up. Do not ship this file as-is.

## What this is going to be

A pre-submission safety gate for ISO 20022 pacs.008 payment messages.
Checks a message against the official XSD plus a small set of
documented, sourced gotchas that XSD validation alone misses — things
like SWIFT's network-level character set restriction, which can reject
a message that's 100% schema-valid. See `docs/SOURCES.md` for the
source behind every rule and `docs/RESEARCH_NOTES.md` for the full
research writeup this scaffold was built from.

## Status

Pre-alpha. Module structure exists; rule logic does not yet. Every
`validation/*.py` and `explain/*.py` file raises `NotImplementedError`
with a docstring describing the planned approach and its source.

## Scope (v1)

- pacs.008.001.08 only (FI to FI Customer Credit Transfer).
- Structural validation (XSD) + a handful of sourced, documented
  transformation gotchas. Not a SWIFT-certified compliance tool.
- See `docs/SOURCES.md` for what's covered and what's explicitly out
  of scope, with citations.

## License

Apache 2.0. See `LICENSE`.
