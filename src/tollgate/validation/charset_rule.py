"""SWIFT network character set restriction.

THE GOTCHA: ISO 20022 XML permits full UTF-8 Unicode at the schema level.
SWIFT's network layer separately restricts allowed characters to its
character set X for messages traveling over FIN/MX coexistence —
meaning a message can be 100% XSD-valid and still get rejected at the
network layer for a reason the schema has no way to express.

Character set X, per ECB/T2S documentation (docs/SOURCES.md#charset-x):
    a-z A-Z 0-9 / - ? : ( ) . , ' + and CR/LF

CAVEAT (be honest about this in any explanation text): the universality
of this restriction across all networks is not fully confirmed — some
market infrastructures have discussed extended character set proposals
(see UK Interoperability Working Group reference in research notes).
Confirm this is still the operative rule for your target network
(Fedwire vs CBPR+) before treating it as a hard universal rule rather
than a FIN/MX-coexistence-era default. Surface this caveat to the user
rather than asserting it unconditionally.

NOT YET IMPLEMENTED. Planned approach:
  - Extract text content from Nm, AdrLine, and remittance-info text
    fields (the field list should be derived from the XSD's Max*Text
    elements, not hardcoded, so it doesn't silently miss fields).
  - Regex-match against the allowlist above.
  - For each violation, return the specific offending character(s) and
    field path, not just "contains invalid characters" — the explainer
    needs the actual character to say something useful ("the 'ü' in
    Creditor Name will be rejected by SWIFT's character set X, even
    though it passed XML schema validation").
"""

from pathlib import Path

from tollgate.validation.models import Violation

CHARSET_X_PATTERN = r"^[a-zA-Z0-9/\-?:().,'+\r\n]*$"


def check_charset(xml_path: Path) -> list[Violation]:
    raise NotImplementedError(
        "Character set check not yet implemented. See module docstring for plan."
    )
