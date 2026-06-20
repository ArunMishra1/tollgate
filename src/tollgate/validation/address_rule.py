"""Postal address structure rules — hybrid end-state enforcement.

THE DEADLINE THIS MATTERS FOR: November 2026, unstructured free-text
addresses stop being accepted across SWIFT cross-border payments and
several clearing networks including Fedwire, CHIPS, SEPA, CHAPS-UK,
TARGET2-Euro, and SAMOS (docs/SOURCES.md#address-deadline-2026).
This is the single highest-value check in v1 given the dated, narrow,
approaching deadline.

TWO DIFFERENT RULE SETS APPLY DEPENDING ON PARTY ROLE
(source: Fedwire ISO 20022 Quick Reference Guide, docs/SOURCES.md#fedwire-qrg):

Interim-state roles (Debtor, Creditor, Debtor Agent, Creditor Agent,
Intermediary Agent 1-3, Previous Instructing Agent 1-3, Charges
Information Agent):
  - Name required to use Postal Address at all.
  - EITHER structured address alone OR free-format AdrLine alone —
    never both.
  - If structured: minimum TwnNm + Ctry.
  - If free-format: up to 3 lines, 35 chars each.

Hybrid-end-state roles (Ultimate Debtor, Initiating Party, Ultimate
Creditor, Originator):
  - Name required.
  - Structured alone, OR structured + free-format combined.
    Free-format ALONE is not permitted for these roles.
  - TwnNm + Ctry always required, even when AdrLine is also used.
  - Free-format lines: up to 2 lines, 70 chars each (note: NOT 35 —
    this differs from the interim limit and is a likely source of
    truncation bugs in systems that hardcode the legacy 35-char MT
    line limit across all address fields uniformly).

NOT YET IMPLEMENTED. Planned approach:
  - Maintain the role->ruleset mapping as data (not scattered if/else),
    since it's the kind of table that needs to stay easy to audit
    against the source document.
  - For each role present in the message, determine interim vs
    hybrid-end-state bucket, check structured/free-form presence and
    TwnNm/Ctry presence accordingly.
  - Flag RuleId.ADDRESS_FREEFORM_ONLY when a hybrid-end-state role has
    AdrLine present but TwnNm or Ctry absent.

VERIFIED AGAINST THE ACTUAL VENDORED XSD (2026-06-20): PostalAddress24
defines AdrLine with maxOccurs="7", type Max70Text — the schema itself
permits up to 7 free-format lines of 70 characters each, which is MORE
permissive than the Fedwire hybrid-end-state limit of 2 lines. A
message with, say, 5 AdrLine entries is fully schema-valid XML and
still violates the usage guideline. This is concrete, schema-level
proof that this rule earns its place as a separate, non-XSD check —
XSD validation alone cannot catch this class of violation, because the
schema is deliberately more permissive than any single network's
usage guidelines layered on top of it. Codeable rule: also flag
AdrLine count > 2 for hybrid-end-state roles, not just the
presence/absence check above.
"""

from pathlib import Path

from tollgate.validation.models import Violation

INTERIM_STATE_ROLES = {
    "Dbtr", "Cdtr", "DbtrAgt", "CdtrAgt",
    "IntrmyAgt1", "IntrmyAgt2", "IntrmyAgt3",
    "PrvsInstgAgt1", "PrvsInstgAgt2", "PrvsInstgAgt3",
    "ChrgsInf",
}

HYBRID_END_STATE_ROLES = {
    "UltmtDbtr", "InitgPty", "UltmtCdtr",
}


def check_address_structure(xml_path: Path) -> list[Violation]:
    raise NotImplementedError(
        "Address structure check not yet implemented. See module docstring for plan."
    )
