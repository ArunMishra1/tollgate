# Eval harness baseline report

Run 2026-06-21, entirely in sandbox, no API key required. Two mock
explainers run against 10 synthetic fixtures per rule (70 fixtures
total per run) to establish what the scoring function actually does
before comparing it against real Claude output.

## Run 1: "realistic" explainer (field name + deterministic message)

This explainer doesn't call any model — it just combines the field
name with `Violation.message`, the same two pieces of information the
real prompt template gives Claude. Every one of the seven rules
scored 100% "correct":

| Rule | Score |
|---|---|
| xsd_structural | 10/10 correct |
| charset_violation | 10/10 correct |
| address_freeform_only | 10/10 correct |
| address_missing_town_country | 10/10 correct |
| address_too_many_lines | 10/10 correct |
| truncation_suspected | 10/10 correct |
| mandatory_field_gap | 10/10 correct |

**What this actually proves:** every rule's deterministic `message`
field already contains enough signal (the right field name, the right
cause language) to score "correct" on its own, with zero AI
involvement. This is the right baseline to know before judging a real
model's output — if a real Claude explanation ever scores *worse* than
this trivial combination, that's a signal the prompt is making things
worse, not just failing to add value. It also confirms the explain
layer's job is narration, not investigation: the facts needed for a
good explanation are already sitting in the deterministic output.

## Run 2: "field-only" explainer (deliberately weak, stress test)

Same fixtures, a deliberately worse explainer that mentions the field
but never states a cause ("There's something to look at in the Nm
field."). Every rule dropped to 100% "partial," with zero "correct,"
"wrong," or "hallucinated":

| Rule | Score |
|---|---|
| All seven rules | 10/10 partial |

**What this proves:** the scoring function's two-signal design
(field_mentioned AND cause_mentioned) actually discriminates between
explanation quality levels — it isn't trivially generous. An
explanation has to genuinely state the cause, not just gesture at the
field, to earn "correct."

## What's still untested by this report

This report uses mock explainers, not the real Claude API -- by
design, so it could be run without an API key. The real model's
explanation quality was separately confirmed live (see git history /
prior session notes: all 3 live-API tests in test_explainer.py pass
against a real key, including the eval-harness-integration test,
which confirmed a real explanation scores "correct" or "partial" on at
least the charset_violation case specifically).

What hasn't been done yet: running the full 7-rule x N-fixture sweep
against the REAL API rather than a mock, the way this report ran it
against mocks. That would need:
  1. A real ANTHROPIC_API_KEY (on a machine that can reach
     api.anthropic.com -- this sandbox cannot)
  2. Calling run_eval(explain_fn=explain_violation, ...) instead of a
     mock -- a one-line change, since the harness was built decoupled
     from the explainer specifically for this reason
  3. Reviewing whether any rule scores meaningfully worse against the
     real model than against this mock baseline -- if so, that rule's
     prompt likely needs tuning, not the detection logic itself
