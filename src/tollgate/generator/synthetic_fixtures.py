"""Generates baseline-valid pacs.008 messages and labeled corrupted variants.

NOT YET IMPLEMENTED. Planned approach:
  1. build_valid_baseline() — a realistic, schema-valid pacs.008.001.08
     message. Realistic means real-format BICs (not "XXXXUS00"-style
     placeholders), real currency codes, plausible amounts, plausible
     bank/person names — not because real data is needed (it explicitly
     isn't, and shouldn't be), but because unrealistic filler makes it
     too easy for the AI explainer to "succeed" on fixtures that don't
     resemble anything a real conversion pipeline would produce.
  2. inject_error(baseline, rule_id) -> (corrupted_xml, ground_truth_label)
     One function per RuleId in validation/models.py. Each injection
     should correspond to an actual documented gotcha (see
     docs/SOURCES.md) — don't invent corruption modes that aren't
     traceable to a real, sourced failure pattern.
  3. ground_truth_label is a small dataclass: {rule_id, field_path,
     injected_value, expected_violation_type} — this is what
     eval_harness.py scores the AI explanation against.
"""

from pathlib import Path

from tollgate.validation.models import RuleId


def build_valid_baseline() -> str:
    raise NotImplementedError("See module docstring for plan.")


def inject_error(baseline_xml: str, rule_id: RuleId) -> tuple[str, dict]:
    raise NotImplementedError("See module docstring for plan.")
