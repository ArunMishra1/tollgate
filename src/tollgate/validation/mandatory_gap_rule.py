"""MX-mandatory fields that had no FAIM/MT equivalent.

THE GOTCHA: some fields are mandatory in pacs.008 but the legacy format
a message was converted from had no equivalent concept at all — not a
truncation or mapping problem, a genuine data gap. Source: Fedwire's
FAIM-tag-to-ISO-20022-element comparison table documents several legacy
tags (the {6xxx} series, e.g. {6100} Receiver FI Information, {6200}
Intermediary FI Information) as "No equivalent" in MX
(docs/SOURCES.md#fedwire-faim-comparison).

When a system that auto-converts legacy data hits one of these, it has
no source value to populate the new mandatory field with at all — the
resulting XSD error ("required element missing") is technically
correct but unhelpful, because it doesn't tell the integrator WHY the
data was never there to begin with.

NOT YET IMPLEMENTED. Planned approach:
  - Maintain a small table: {mx_field_path: legacy_context_note}.
    Start narrow with only the documented Fedwire FAIM-comparison gaps
    rather than guessing at others.
  - When XSD validation already reports a missing-required-element
    error for one of these specific paths, attach the legacy-gap note
    so the explainer can say "this wasn't optional before, it's that
    the old format had nowhere to put this information" instead of a
    generic restatement of the XSD error.
"""

from pathlib import Path

from tollgate.validation.models import Violation

# Narrow and sourced — extend only with traceable citations in SOURCES.md.
MX_MANDATORY_NO_LEGACY_EQUIVALENT = {
    # field_path: legacy_context_note
}


def check_mandatory_gaps(xml_path: Path, xsd_violations: list[Violation]) -> list[Violation]:
    raise NotImplementedError(
        "Mandatory gap check not yet implemented. See module docstring for plan."
    )
