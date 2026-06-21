"""Shared data model for validation results.

Every rule module (xsd_validator, charset_rule, address_rule,
truncation_rule, mandatory_gap_rule) returns a list of Violation objects
using this shape, so the explain/ layer and the eval harness can treat
all rule types uniformly.
"""

from dataclasses import dataclass, field
from enum import Enum


class RuleId(str, Enum):
    """Stable identifiers. Used as the ground-truth label in synthetic
    fixtures and in eval scoring — do not rename these once fixtures
    reference them, or old eval results become unscorable.
    """

    XSD_STRUCTURAL = "xsd_structural"
    CHARSET_VIOLATION = "charset_violation"
    ADDRESS_FREEFORM_ONLY = "address_freeform_only"
    ADDRESS_MISSING_TOWN_COUNTRY = "address_missing_town_country"
    ADDRESS_TOO_MANY_LINES = "address_too_many_lines"
    TRUNCATION_SUSPECTED = "truncation_suspected"
    MANDATORY_FIELD_GAP = "mandatory_field_gap"
    CURRENCY_DECIMAL_MISMATCH = "currency_decimal_mismatch"


@dataclass
class Violation:
    rule_id: RuleId
    field_path: str  # e.g. "CdtTrfTxInf/Cdtr/PstlAdr/AdrLine"
    message: str  # short, human-unreadable-ok, deterministic description
    severity: str = "error"  # "error" | "warning"
    raw_value: str | None = None  # offending value, for explainer context
    source_ref: str | None = None  # key into docs/SOURCES.md, e.g. "fedwire-qrg-2024-07"
    extra: dict = field(default_factory=dict)
