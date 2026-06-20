"""Synthetic test fixture generator.

Produces realistic, valid pacs.008.001.08 messages, then injects
labeled, documented errors from the gotcha list in docs/SOURCES.md.
Real bank names, real-format BICs, real currency codes — no
placeholder "ACME Corp" filler. This is the ground truth the eval
harness scores against.
"""
