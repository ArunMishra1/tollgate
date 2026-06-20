"""AI explanation layer.

Single-prompt Claude API calls only — no agent/tool-use loop in v1.
Each Violation (already deterministically identified by validation/)
gets explained in plain English, grounded in the specific rule that
was violated. The model never decides WHAT is wrong; it only narrates
WHY a given, already-detected violation matters and what to fix.

This split matters for the eval harness: a single deterministic
input->output call is easy to score against injected ground truth.
Revisit this decision only if evals show single-prompt explanations
are consistently insufficient — don't add agentic complexity
preemptively.
"""
