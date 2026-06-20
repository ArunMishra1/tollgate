"""Deterministic XSD structural validation.

TARGET SCHEMA: pacs.008.001.08 (FIToFICustomerCreditTransferV08)
Source the actual XSD from iso20022.org's message archive directly —
do not depend on a third-party GitHub mirror staying available or
unmodified. See docs/SOURCES.md#xsd-source for the exact archive URL
once pulled, and note the version decision rationale there (Fedwire
and CBPR+ guidance both reference .08 as of this research, even though
the iso20022.org catalogue's newest published version is .14 — pin to
.08 unless you've confirmed your target network has moved on).

NOT YET IMPLEMENTED. Planned approach:
  - Use `xmlschema` (preferred over raw lxml XSD validation for
    better error paths) to load the vendored XSD in schemas/.
  - Validate the input message, collect ALL errors (not just first),
    map each xmlschema.XMLSchemaValidationError into a Violation with
    rule_id=RuleId.XSD_STRUCTURAL and field_path derived from the
    error's XML path.
  - This stage must be airtight before any other rule runs — the other
    rules assume structurally valid XML, so a malformed document should
    short-circuit here rather than cause encoding errors in charset_rule
    or address_rule.
"""

from pathlib import Path

from tollgate.validation.models import Violation


def validate_xsd(xml_path: Path, schema_path: Path) -> list[Violation]:
    raise NotImplementedError(
        "XSD validation not yet implemented. See module docstring for plan."
    )
