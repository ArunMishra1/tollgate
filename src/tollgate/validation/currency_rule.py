"""Currency decimal precision -- amounts with more decimal places than
their currency actually supports.

THE GOTCHA: ISO 4217 defines a per-currency "minor unit" exponent --
how many decimal places that specific currency supports. Most
currencies use 2 (USD, EUR, GBP). Some use 0, with no decimals at all
(JPY, KRW, VND, and others). A few use 3 (KWD, BHD, OMR, JOD, TND, LYD,
IQD). Source: ISO.org's own page on ISO 4217 confirms the standard
defines this minor-unit relationship per currency
(https://www.iso.org/iso-4217-currency-codes.html), cross-referenced
against three independent payment-processing technical references
(Adyen, Datatrans, LegalClarity) which state the same exponent
groupings for the well-known cases consistently with each other.

HONEST LIMITATION on sourcing (2026-06-21): the authoritative,
machine-readable ISO 4217 table itself (maintained by SIX Group on
ISO's behalf, redistributed as public domain by the datasets/
currency-codes GitHub project) could not be directly fetched in this
research session -- GitHub's raw content endpoint disallowed automated
access. The exponent groupings below are corroborated by multiple
independent technical sources rather than fetched from the primary
table directly. The well-known cases (JPY/KRW/VND at 0; KWD/BHD/OMR/
JOD/TND/LYD/IQD at 3) are consistent across every source checked. If
you are extending this list, verify new entries against the primary
source before adding them, rather than trusting a single secondary
reference -- see docs/SOURCES.md for the full citation list and this
caveat.

VERIFIED AGAINST THE ACTUAL VENDORED XSD (2026-06-21):
ActiveCurrencyAndAmount_SimpleType and
ActiveOrHistoricCurrencyAndAmount_SimpleType both define
fractionDigits="5" -- the schema permits up to 5 decimal places for
ANY currency, regardless of what that specific currency's own ISO 4217
exponent actually allows. A JPY amount like "1000.50" (JPY supports 0
decimal places) is fully schema-valid and still objectively wrong.
This is the same "schema is more permissive than reality" shape as
every other rule in this project.

STRUCTURAL NOTE: there is no single element name to walk for this rule
the way charset_rule walks Nm/AdrLine -- the schema uses at least 22
different element names (Amt, IntrBkSttlmAmt, InstdAmt, RmtdAmt,
TtlIntrBkSttlmAmt, and others) for currency-and-amount content, many
sharing the generic tag "Amt" across different contexts. The schema's
Ccy attribute is use="required" on every one of them, so this rule
walks by ATTRIBUTE PRESENCE (any element with a Ccy attribute) rather
than by tag name -- verified to correctly find amount elements
regardless of which of the 22 element names is used, without needing
to enumerate them all.

SEVERITY NOTE: unlike address_too_many_lines or charset_violation,
this is not necessarily a guaranteed hard rejection -- depending on
the receiving system, an over-precise amount might be rejected, or it
might be silently rounded/misinterpreted. Reported as "warning", not
"error", to avoid overstating certainty the available sources don't
support.
"""

from pathlib import Path

from lxml import etree

from tollgate.validation.models import RuleId, Violation

# Sourced per the HONEST LIMITATION note above -- corroborated across
# multiple independent technical references, not fetched from the
# primary ISO 4217 table directly. Verify against a primary source
# before extending.
ZERO_DECIMAL_CURRENCIES = {
    "JPY", "KRW", "VND", "ISK", "CLP", "PYG", "RWF", "UGX", "VUV",
    "XAF", "XOF", "XPF", "DJF", "GNF", "KMF",
}
THREE_DECIMAL_CURRENCIES = {
    "KWD", "BHD", "OMR", "JOD", "TND", "LYD", "IQD",
}
# Everything else defaults to 2 decimal places -- the common case
# covering USD, EUR, GBP, and the large majority of active currencies.
DEFAULT_DECIMAL_PLACES = 2


def _expected_decimal_places(currency_code: str) -> int:
    if currency_code in ZERO_DECIMAL_CURRENCIES:
        return 0
    if currency_code in THREE_DECIMAL_CURRENCIES:
        return 3
    return DEFAULT_DECIMAL_PLACES


def _actual_decimal_places(value_text: str) -> int:
    if "." not in value_text:
        return 0
    return len(value_text.split(".", 1)[1])


def _local_path(element: etree._Element, doc_root: etree._Element) -> str:
    """Same readable-path helper used in the other rule modules."""
    parts = []
    node = element
    while node is not None and node != doc_root:
        parts.append(etree.QName(node.tag).localname)
        node = node.getparent()
    return "/".join(reversed(parts))


def check_currency_decimal_precision(xml_input: str | Path) -> list[Violation]:
    """Walks every element carrying a Ccy attribute (required on all
    22+ amount element types in the schema) and checks whether the
    value's actual decimal places match that currency's expected
    exponent. Assumes input already passed XSD validation -- does not
    re-check structure, only the currency-specific precision rule
    layered on top of what the schema's generic fractionDigits="5"
    allows.
    """
    if isinstance(xml_input, Path):
        root = etree.parse(str(xml_input)).getroot()
    else:
        root = etree.fromstring(xml_input.encode("utf-8"))

    violations: list[Violation] = []
    for element in root.iter():
        currency_code = element.get("Ccy")
        if currency_code is None:
            continue
        if element.text is None:
            continue

        expected = _expected_decimal_places(currency_code)
        actual = _actual_decimal_places(element.text)

        if actual > expected:
            tag = etree.QName(element.tag).localname
            path = _local_path(element, root)
            violations.append(
                Violation(
                    rule_id=RuleId.CURRENCY_DECIMAL_MISMATCH,
                    field_path=path,
                    message=(
                        f"{tag} has {actual} decimal place(s) for currency "
                        f"{currency_code}, which supports {expected}. The "
                        f"schema itself permits up to 5 decimal places for "
                        f"any currency, so this passes XSD validation -- "
                        f"but {currency_code} does not actually support "
                        f"this level of precision."
                    ),
                    severity="warning",
                    raw_value=element.text,
                    source_ref="currency-decimal-precision",
                    extra={
                        "currency_code": currency_code,
                        "expected_decimal_places": expected,
                        "actual_decimal_places": actual,
                    },
                )
            )
    return violations
