# Contributing

Tollgate's credibility rests on one thing: every rule traces to a real source, and every claim has been tested, not assumed. That's not a style preference — it's the whole point of the project. If you're adding a rule, a fix, or a feature, the norms below exist to keep that true.

## The non-negotiable: source every rule

If you're adding a new validation rule, it needs a citation in [`docs/SOURCES.md`](docs/SOURCES.md) before it ships — a primary source where possible (a regulator's own documentation, the official XSD, SWIFT's own specifications), or a clearly-identified secondary source with the gap stated honestly if a primary source isn't available.

Don't add a rule based on something you half-remember or a claim you found in someone else's blog post without checking it yourself. This project has already found and corrected one rule that was built on an unverified secondhand citation (see `docs/SOURCES.md`'s `fedwire-faim-comparison` entry, kept visible specifically as an example of what *not* to ship) — that correction is part of the project's history on purpose, so the bar stays visible.

## Test against real generated fixtures, not assumptions

Every rule module has a corresponding test file that runs the rule against output from `generator/synthetic_fixtures.py` — not hand-written XML strings, not mocked data. If you're fixing a bug, write a regression test that would have caught it, using the same generator.

This project has a real track record of bugs found specifically by testing rather than trusting:
- A character-set rule that flagged completely normal text as a violation because the allowed-character list was missing a plain space
- An address rule that assumed every party type stored its address at the same nesting depth, which would have silently missed every bank-address violation
- A truncation rule that would have false-positived on values legitimately using a field's own real maximum length — caught by reasoning through the design before any code was written
- An AI explanation layer that sent a real person's name to a third-party API, found by checking what data actually left the machine

None of these were caught by code review or by the implementation "looking right." They were caught by deliberately running the code against real or adversarial input and checking the actual output. Do the same for anything you add.

## The deterministic-check / AI-narration split is load-bearing

Validation logic (does this violate a rule) must be deterministic code — no AI in `validation/*.py`. AI only narrates an *already-detected* violation, in `explain/explainer.py`, via a single API call with no tool use or agentic loop. This split exists so the eval harness can score explanations against known ground truth, and so nothing in this tool can be second-guessed as "is this a real finding or a model's guess." If you're tempted to use AI to *detect* something rather than explain something already detected, that's the wrong layer — open an issue and discuss first.

## Data handling boundary

Never send `Violation.raw_value` (or any field content) across the network to a third-party API by default. See `docs/SOURCES.md`'s `data-handling-ai-boundary` section and `tests/test_data_handling.py` for what this means in practice and how it's verified — that test mocks the API client and inspects the actual payload sent, which is the standard to match for any change touching the explain layer.

## Before opening a PR

- Run the full test suite: `pytest tests/`. It should pass without an `ANTHROPIC_API_KEY` set — the 3 live-API tests in `test_explainer.py` skip automatically without one; that's expected, not a failure.
- If you're touching anything in `explain/`, also run with a real `ANTHROPIC_API_KEY` set at least once before merging, since that's the one part of the codebase that can't be fully verified by the deterministic suite alone.
- If you're adding a rule, confirm it's cited in `docs/SOURCES.md` and that your test file exercises both the violation case and a clean-message case (no false positives).

## Scope

v1 covers exactly one message type: pacs.008.001.08. If you want to add a second message type or extend beyond what's documented in [`docs/why.md`](docs/why.md)'s "what it explicitly does not do" section, raise it as an issue first — that's a scope decision, not just a code change.
