"""Eval harness: scores AI explanations against injected-error ground truth.

Same pattern as the migration-drift project this repo's author has
built before — because the errors are injected by generator/, the
correct violation type is always known, so explanation quality is
scorable rather than judged by feel.

NOT YET IMPLEMENTED. Planned approach:
  1. For each RuleId, generate N corrupted fixtures via
     generator.synthetic_fixtures.inject_error().
  2. Run the full validation pipeline on each -> raw Violations.
  3. Run explain_violation() on each Violation -> explanation text.
  4. Score each explanation against the fixture's ground_truth_label:
       - "correct": names the right field_path AND the right rule/cause
       - "partial": names the right field but wrong/vague cause, or
         vice versa — this is a distinct failure mode from being
         totally wrong and should be tracked separately
       - "wrong": names a different field or a different rule entirely
       - "hallucinated": claims a violation/rule that doesn't exist
     Start with deterministic keyword/field-path matching for scoring
     before reaching for an LLM-as-judge step. Deterministic scoring
     is more trustworthy for a credibility-sensitive tool; LLM-judge
     can be a secondary signal added later if deterministic scoring
     proves too brittle.
  5. Write results to eval_results/<timestamp>.json with per-rule_id
     breakdown, so a prompt change that improves one rule's
     explanations but regresses another's is visible over time.
"""

from pathlib import Path

from tollgate.validation.models import RuleId


def run_eval(rule_ids: list[RuleId] | None = None, fixtures_per_rule: int = 10) -> dict:
    raise NotImplementedError("See module docstring for plan.")
