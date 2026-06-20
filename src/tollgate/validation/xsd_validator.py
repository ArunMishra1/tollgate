"""Deterministic XSD structural validation.

TARGET SCHEMA: pacs.008.001.08 (FIToFICustomerCreditTransferV08)
Confirmed download (verified working 2026-06-20):
  https://www.iso20022.org/message/14231/download
This version was superseded in the live catalogue (current is .14)
and now lives in the ISO 20022 Messages Archive, under "Payments
Clearing and Settlement V09" (archived 01 Feb 2019). Fedwire and
CBPR+ guidance both reference .08 as of this research even though
it's no longer the catalogue's newest — pin to .08 unless you've
confirmed your target network has moved on. See docs/SOURCES.md#xsd-
source for both the current-catalogue and archive URLs.

Do not depend on a third-party GitHub mirror staying available or
unmodified — pull from the URL above directly.

VERIFIED 2026-06-20: a generator-built baseline message (see
generator/synthetic_fixtures.py) validates clean against this exact
vendored XSD with zero errors, and a deliberately broken variant
(mandatory ChrgBr removed) is correctly caught with a specific,
actionable error and XML path. The approach below is proven, not
theoretical.
"""

from pathlib import Path

import xmlschema

from tollgate.validation.models import RuleId, Violation


def validate_xsd(xml_input: str | Path, schema_path: str | Path) -> list[Violation]:
    """Validates xml_input (a path or raw XML string) against the XSD
    at schema_path. Collects ALL errors in one pass via iter_errors(),
    not just the first -- a report with "found 1 error, fix it and
    rerun" is a worse experience than "here are all 4 things wrong."

    This stage is the foundation every other rule module assumes ran
    first and passed (or at least didn't find a structural problem in
    the specific area that rule cares about) -- a malformed document
    should be caught here, not cause a confusing downstream failure in
    charset_rule or address_rule trying to parse something invalid.
    """
    schema = xmlschema.XMLSchema(str(schema_path))

    if isinstance(xml_input, Path):
        source = str(xml_input)
    else:
        # Raw XML string -- xmlschema's iter_errors accepts bytes or
        # a file-like source; encode explicitly rather than relying on
        # implicit encoding detection.
        source = xml_input.encode("utf-8")

    violations: list[Violation] = []
    for error in schema.iter_errors(source):
        violations.append(
            Violation(
                rule_id=RuleId.XSD_STRUCTURAL,
                field_path=error.path or "(unknown path)",
                message=error.reason or str(error),
                severity="error",
                source_ref="iso20022-xsd-pacs008-001-08",
            )
        )
    return violations

