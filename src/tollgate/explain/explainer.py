"""The explanation layer's only public function.

Deliberately a single function, not a class, not an agent loop —
per the explicit decision: single-prompt Claude API calls in v1,
revisit only if evals demand more.
"""

from tollgate.explain.prompts import EXPLAIN_VIOLATION_SYSTEM_PROMPT, EXPLAIN_VIOLATION_USER_TEMPLATE
from tollgate.validation.models import Violation


def explain_violation(violation: Violation, model: str = "claude-sonnet-4-6") -> str:
    """Given one already-detected Violation, return a plain-English
    explanation grounded in the specific rule and field involved.

    NOT YET IMPLEMENTED. Planned approach:
      - Single call to the Anthropic API, system prompt + user prompt
        from prompts.py, no tools.
      - No retry-with-different-prompt logic in v1 — if the eval
        harness shows a class of explanation is consistently weak,
        fix the prompt template, don't paper over it with retries.
    """
    raise NotImplementedError(
        "Explanation layer not yet implemented. See module docstring for plan."
    )
