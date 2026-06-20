"""Legacy MT-to-MX truncation heuristic.

THE GOTCHA: SWIFT's own CBPR+ pilot testing used a named test category
called "truncation and warning" scenarios (docs/SOURCES.md#truncation-
pilot), confirming this is a recognized class of problem, not a
hypothetical. Legacy MT fields have hard line-length limits (commonly
35 characters); MX fields are typically longer (Max70Text, Max140Text).
Data converted from MT to MX, or MX-native data later squeezed back
through an MT-shaped integration, can be silently truncated.

THE HEURISTIC (not a hard rule, hence "suspected" not "violation"):
a field value landing at EXACTLY a known legacy boundary (35 or 70
chars) is a meaningfully stronger truncation signal than a field that's
merely under its XSD max length — coincidentally hitting an old MT line
limit exactly is unlikely. This is exactly the "explain why, not just
that" case: XSD validation alone would not flag this at all, since a
35-char value is well within Max70Text's limit and schema-valid.

NOT YET IMPLEMENTED. Planned approach:
  - For text fields with Max*Text constraints, check actual value
    length against the known legacy boundary set {35, 70}.
  - Flag as RuleId.TRUNCATION_SUSPECTED with severity="warning" (this
    is a heuristic, not a certain violation — be honest about that
    distinction in both the code and any user-facing explanation).
"""

from pathlib import Path

from tollgate.validation.models import Violation

LEGACY_MT_LINE_BOUNDARIES = {35, 70}


def check_truncation_signals(xml_path: Path) -> list[Violation]:
    raise NotImplementedError(
        "Truncation heuristic not yet implemented. See module docstring for plan."
    )
