# Tollgate — Research Findings & v1 Plan

Status: pre-build research, all claims sourced below. Verify dates against primary sources before publishing anything externally — payment migration dates have moved before (Fedwire address requirements alone were extended three times).

## 1. Correction to original framing

The original brief said the 2026 migration creates a unified forced-migration moment across Fedwire, CHIPS, and CBPR+. Closer to accurate: those *core* MX cutovers already happened —

- CHIPS migrated to ISO 20022 in April 2024.
- Fedwire Funds Service migrated March 10, 2025 (some sources say July 14, 2025 for full mandatory cutover — there were phased dates; confirm current state before quoting).
- SWIFT cross-border (CBPR+) coexistence period for MT/MX ended November 2025.

What's actually live and dated for **2026** is the next wave: full address-structure enforcement. The November 2026 deadline requires fully structured or hybrid address formats — unstructured free-text addresses stop being accepted — across SWIFT cross-border payments and clearing systems including Fedwire, CHIPS, SEPA, Swiss SIC, CHAPS-UK, TARGET2-Euro, and South Africa's SAMOS.

This is a *better* hook than "general migration year" — it's one concrete, dated, narrow rule with five months of runway, and it maps directly to codeable validation logic. Lead with this in the README rather than the more diffuse "2026 is a big migration year" framing.

## 2. Message type: confirmed pacs.008

Stick with pacs.008.001.08 as the primary target version, not the newest catalogue version (currently pacs.008.001.14 on iso20022.org).

Reasoning: .08 is the version actually referenced across Fedwire's own Quick Reference Guide, CBPR+ guidance, and most bank migration FAQs (Citi, JPMorgan, BNY) as of this research. Banks pin to specific versions per clearing network — building against the bleeding-edge catalogue version would validate against a schema nobody's actually sending. Confirm the exact pinned version against SWIFT MyStandards for whichever network you want the eval fixtures to mirror most closely (Fedwire vs CBPR+ have separate usage guideline profiles even on the same base version).

Action item: pull the actual XSD for pacs.008.001.08, not .14. Public GitHub mirrors exist (e.g. sladjan/xsd-camt, yudhik/example-iso-20022) but treat those as convenience copies only — the authoritative source is the ISO 20022 message archive at iso20022.org/iso-20022-message-definitions, which hosts the official XSD as a downloadable artifact per message version. Pull from there directly for the version you ship; don't depend on a third-party GitHub mirror staying available or unmodified.

## 3. Sourced gotcha list for v1

Each entry below has a primary source. This is the credibility-bearing part of the project — do not add entries you can't trace to a source.

### 3.1 Hybrid/end-state postal address rules (Fedwire Quick Reference Guide, source-verified)

Two regimes exist and the rules differ by which party/agent role is involved:

**Interim state** (legacy-adjacent parties: Debtor, Creditor, Debtor Agent, Creditor Agent, Intermediary Agents, Previous Instructing Agents, Charges Information Agent):
- Name must be present to use the Postal Address component at all.
- Either structured address alone OR free-format address lines alone — never both.
- If structured: minimum Town Name + Country required.
- If free-format: up to 3 lines, 35 characters each.

**Hybrid end-state** (Ultimate Debtor, Initiating Party, Ultimate Creditor, Originator):
- Name must be present.
- Structured address alone, OR structured + free-format combined. Free-format alone is **not permitted**.
- Town Name + Country always required, even when free-format lines are used.
- Free-format lines: up to 2 lines, **70 characters each** (not 35 — this differs from the interim-state limit, a likely source of legacy-conversion truncation bugs since old systems often hardcode the 35-char MT line limit).

**Codeable rule for v1**: detect free-format-only addresses (AdrLine present, TwnNm/Ctry absent) for any of the four hybrid-end-state roles → flag as a hard rejection risk under the November 2026 enforcement, even if current systems still accept it under transition tolerance. This is the single highest-value check in the whole tool given the dated deadline.

### 3.2 SWIFT network character set restriction (verified, two sources)

ISO 20022 XML itself permits full UTF-8 Unicode. SWIFT's network layer restricts allowed characters to Basic Latin regardless of what the XSD permits. SWIFT's character set X is specifically: `a-z A-Z 0-9 / - ? : ( ) . , ' +` plus CR/LF (sourced from ECB/T2S documentation, which documents the formal definition used for FIN/MX coexistence).

This is the single most useful non-obvious check: **a message can pass XSD validation and still get rejected at the network layer** because XSD doesn't know about SWIFT's character set restriction — it's a SWIFT network rule, not an ISO 20022 schema rule. Legacy systems converting from MT (which already enforced X-set characters) usually don't introduce new violations, but systems originating data directly in XML/Unicode (modern core banking, web-based payment portals) can easily introduce names with diacritics, em-dashes, curly quotes, or non-Latin scripts that are schema-valid XML but network-invalid payloads.

**Codeable rule for v1**: regex scan of all `Nm`, `AdrLine`, and remittance text fields against the character set X allowlist; flag any character outside it with the specific offending character and field path.

### 3.3 MT-to-MX field length mismatches / truncation (verified pattern, SWIFT-documented test category)

SWIFT's own CBPR+ pilot testing explicitly included a category called "truncation and warning" scenarios as one of two test scenario types (the other being "happy path"), confirming this is a recognized, named class of problem, not a hypothetical. The mechanism: legacy MT fields have hard character limits (e.g., 35-char lines in many MT fields) and when converting MT-sourced data into MX's typically longer field allowances (Max70Text, Max140Text, etc.), conversely when *downgrading* MX-native long-form data for MT-compatible legacy systems, this can result in silent truncation that previously caused no visible failure but now surfaces as either data loss or a structural rejection depending on direction.

**Codeable rule for v1**: for any field with a documented Max*Text constraint in the XSD, check actual content length against the limit (XSD validation already does this technically, but the *value-add* is flagging fields where length is suspiciously exactly at a legacy MT boundary, e.g. exactly 35 or 70 chars, which is a strong signal of truncation rather than coincidence — this is exactly the kind of "AI explains why, not just that" case from your brief).

### 3.4 Mandatory-in-MX-but-optional-in-MT fields

Source: Fedwire's FAIM-to-ISO-20022 tag comparison table documents fields with "No equivalent" in legacy FAIM — meaning these are new mandatory MX concepts that legacy systems have no source data for at all, not just a truncation risk but a complete data gap (e.g. several `{6xxx}` series legacy tags map to "No equivalent" in MX). Separately, structured fields like Creditor Agent's full identification become mandatory in pacs.008 in cases (e.g. US Treasury tax payments) where the legacy format allowed bare routing-number shorthand.

**Codeable rule for v1**: maintain a small table of "MX-mandatory, MT-had-no-equivalent" fields (start with the documented Fedwire FAIM-tag-comparison gaps) and flag their absence with an explanation that names the legacy gap specifically, rather than a generic "missing required element" XSD error.

## 4. What v1 does NOT cover (be explicit in README)

- Not a SWIFT-certified compliance tool. Does not replace MyStandards testing.
- Does not cover pacs.009, pacs.004, camt.05x, or any message type beyond pacs.008.001.08 in v1.
- Does not validate business-level routing/BIC reachability — only structural/format-level checks.
- Character set X check covers the FIN/MX coexistence-era restriction as documented for T2S; confirm this is still the operative rule for your target network (Fedwire vs CBPR+) before treating it as universal, since extended character set proposals have been discussed by some market infrastructures (UK working group reference found in research) and policy could differ by network/region.
- Address rule enforcement timeline (interim vs hybrid end-state) has shifted multiple times historically — treat the November 2026 date as the best current public information, not a guarantee; link sources in README rather than asserting it as fixed fact.

## 5. Proposed repo structure

```
tollgate/
├── README.md
├── LICENSE                          (Apache 2.0)
├── pyproject.toml
├── src/tollgate/
│   ├── __init__.py
│   ├── cli.py                       # Typer entrypoint
│   ├── schemas/
│   │   └── pacs.008.001.08.xsd      # vendored official XSD, with source URL in a comment header
│   ├── validation/
│   │   ├── xsd_validator.py         # deterministic XSD check via xmlschema or lxml
│   │   ├── charset_rule.py          # SWIFT character set X check
│   │   ├── address_rule.py          # hybrid end-state address structure check
│   │   ├── truncation_rule.py       # legacy-boundary length heuristic
│   │   └── mandatory_gap_rule.py    # MX-mandatory/MT-no-equivalent table check
│   ├── explain/
│   │   ├── explainer.py             # single function: explain_failure(violation) -> str
│   │   └── prompts.py               # prompt template, kept separate from logic
│   ├── generator/
│   │   └── synthetic_fixtures.py    # builds valid pacs.008 + injects labeled errors
│   └── report/
│       └── markdown_report.py       # --output report.md renderer
├── tests/
│   ├── fixtures/                    # generated + a few hand-built golden files
│   ├── test_xsd_validator.py
│   ├── test_charset_rule.py
│   ├── test_address_rule.py
│   └── evals/
│       ├── eval_harness.py
│       └── eval_results/            # tracked scoring runs over time
└── docs/
    └── SOURCES.md                   # every gotcha rule traced to its primary source
```

`docs/SOURCES.md` matters as much as any code file — it's what separates this from the unsourced AI-flavored content the project rules explicitly forbid. Each rule in the validation/ folder should have a one-line comment pointing to the matching entry in SOURCES.md.

## 6. Eval harness design

Same pattern as your migration-drift project: you control ground truth because you inject the errors.

1. `synthetic_fixtures.py` generates a valid baseline pacs.008.001.08 message (randomized but realistic — real bank names, real-format BICs, real currency codes, no placeholder "ACME Corp" filler).
2. For each gotcha rule, generate N corrupted variants with a structured label: `{rule_id, field_path, injected_value, expected_violation_type}`.
3. Run the full validation pipeline (XSD + rule checks) → get raw violations.
4. Run the AI explainer on each raw violation → get explanation text.
5. Score: does the explanation's stated root cause match `expected_violation_type`? Score categorically (correct / partially correct / wrong / hallucinated-a-different-rule), not just pass/fail — partial credit matters because "found the right field but wrong reason" is a different failure mode than "missed it entirely."
6. Track score per rule_id over time in `eval_results/`, so a prompt change that improves charset-rule explanations but regresses address-rule explanations is visible.

Scoring itself: start with a deterministic keyword/structure check (does the explanation mention the correct field path and rule name) before reaching for an LLM-as-judge step — deterministic scoring is more trustworthy for a credibility-sensitive project and you can always add LLM-judge as a secondary signal later.

## 7. Naming

Package: **Tollgate**. Repo/CLI name `tollgate`, PyPI distribution name `iso-tollgate` to avoid collision with an old, dormant, unrelated 2008–2014 Django captive-portal project of the same repo name on GitHub (different domain, inactive, low collision risk but worth the disambiguation in the PyPI name). License: Apache 2.0, confirmed as your choice.

## 8. Open items before writing code

- [ ] Confirm exact pacs.008 version to pin against (recommend .08, verify against current Fedwire/CBPR+ guidance)
- [ ] Pull authoritative XSD from iso20022.org directly (not GitHub mirror)
- [ ] Verify current Fedwire address-enforcement phase (interim vs hybrid end-state) — this moves
- [ ] Decide whether v1 targets Fedwire-specific usage guidelines or generic CBPR+ guidelines (they have separate profiles even on the same XSD version)
