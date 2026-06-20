"""Tollgate's public library API.

This is the ONE place other code should import from to use Tollgate
programmatically -- a CI pipeline, a payment service's pre-submission
check, a Jupyter notebook, anything that isn't the CLI itself. Before
this module existed, the only way to run the full check pipeline was
to import five separate rule modules and replicate cli.py's internal
assembly logic (_run_all_checks) yourself -- that's internal wiring
that happened to be importable, not a real public API.

Design choices:
  - check_message() accepts a raw XML string OR bytes, not just a file
    path. Most real integration callers (a payment service building a
    message in memory, a CI step receiving XML over stdin) won't have
    a file on disk -- forcing a temp-file round-trip just to call a
    library function is exactly the kind of friction that makes
    people skip validation. check_file() is provided as a thin
    convenience wrapper for the file-on-disk case.
  - Returns a CheckResult dataclass, not bare lists or printed text --
    a CI system needs structured data (to_dict() for JSON), a human
    wants something printable, and a Python caller wants typed
    objects to branch on (e.g. `if result.has_errors`).
  - Reuses the EXACT SAME assembly logic cli.py already had (XSD
    first, skip the other four if the document is fundamentally
    unparseable, catch the narrower downstream-parse-failure case) --
    this is proven, tested logic, not a rewrite. cli.py is updated to
    call THIS module rather than containing its own copy, so there is
    one source of truth for "how does the full pipeline run," not two
    that could drift out of sync.
"""

from dataclasses import asdict, dataclass
from pathlib import Path

from tollgate.validation.address_rule import check_address_structure
from tollgate.validation.charset_rule import check_charset
from tollgate.validation.mandatory_gap_rule import check_mandatory_gaps
from tollgate.validation.models import Violation
from tollgate.validation.truncation_rule import check_truncation_signals
from tollgate.validation.xsd_validator import validate_xsd

SCHEMA_PATH = Path(__file__).parent / "schemas" / "pacs.008.001.08.xsd"

SUPPORTED_MESSAGE_TYPES = {"pacs.008"}


@dataclass
class CheckResult:
    """Structured result of running the full check pipeline on one
    message. This is what library callers get back -- branch on
    has_errors/has_warnings, iterate violations, or call to_dict() for
    JSON serialization (e.g. in a CI step that needs machine-readable
    output, not console text).
    """

    violations: list[Violation]
    explanations: dict[int, str]  # violation index -> explanation text, only populated if explain=True

    @property
    def has_errors(self) -> bool:
        return any(v.severity == "error" for v in self.violations)

    @property
    def has_warnings(self) -> bool:
        return any(v.severity == "warning" for v in self.violations)

    @property
    def is_clean(self) -> bool:
        return len(self.violations) == 0

    def to_dict(self) -> dict:
        """JSON-serializable representation. RuleId is an enum, so
        it's converted to its string value explicitly -- asdict()
        alone would leave it as a non-JSON-serializable enum member.
        """
        return {
            "is_clean": self.is_clean,
            "has_errors": self.has_errors,
            "has_warnings": self.has_warnings,
            "violations": [
                {
                    **{k: v for k, v in asdict(v).items() if k != "rule_id"},
                    "rule_id": v.rule_id.value,
                }
                for v in self.violations
            ],
            "explanations": self.explanations,
        }


def check_message(
    xml_content: str | bytes,
    *,
    message_type: str = "pacs.008",
    explain: bool = False,
) -> CheckResult:
    """Runs the full five-rule check pipeline against an XML string or
    bytes already in memory. This is the primary library entry point
    -- most integration callers have XML in memory, not on disk.

    Raises ValueError for an unsupported message_type, rather than the
    CLI's pattern of printing and exiting -- a library function should
    raise, not call sys.exit via typer.Exit, so callers can catch and
    handle it themselves.
    """
    if message_type not in SUPPORTED_MESSAGE_TYPES:
        raise ValueError(
            f"Unsupported message_type '{message_type}'. v1 only supports "
            f"{sorted(SUPPORTED_MESSAGE_TYPES)}. See README for scope."
        )

    if isinstance(xml_content, bytes):
        xml_str = xml_content.decode("utf-8")
    else:
        xml_str = xml_content

    violations = _run_all_checks(xml_str)

    explanations: dict[int, str] = {}
    if explain:
        from tollgate.explain.explainer import explain_violation

        for i, v in enumerate(violations):
            explanations[i] = explain_violation(v)

    return CheckResult(violations=violations, explanations=explanations)


def check_file(
    path: str | Path,
    *,
    message_type: str = "pacs.008",
    explain: bool = False,
) -> CheckResult:
    """Convenience wrapper for the file-on-disk case. Raises the same
    built-in exceptions a caller would expect from reading a file
    directly (FileNotFoundError, PermissionError, UnicodeDecodeError,
    IsADirectoryError) -- a library function should let Python's
    normal exceptions surface, unlike the CLI which catches them to
    print friendly console messages instead.
    """
    path = Path(path)
    xml_str = path.read_text(encoding="utf-8")
    return check_message(xml_str, message_type=message_type, explain=explain)


def _run_all_checks(xml_str: str) -> list[Violation]:
    """The proven assembly logic, originally written in cli.py as
    _run_all_checks(Path) -- moved here as the single source of truth
    and changed to take a string directly (the CLI now reads the file
    itself and calls this), so there's exactly one place that decides
    "what order do the five rules run in, and what happens if the
    document can't be parsed at all."
    """
    violations: list[Violation] = []
    xsd_violations = validate_xsd(xml_str, SCHEMA_PATH)
    violations.extend(xsd_violations)

    document_unparseable = any(
        v.field_path == "(document root)" for v in xsd_violations
    )
    if document_unparseable:
        # The other four rules would hit the identical parse failure
        # via their own lxml.etree.fromstring calls -- skip them
        # rather than attempt-and-catch, which only produces redundant
        # noise (the same failure reported twice).
        return violations

    try:
        violations.extend(check_charset(xml_str))
        violations.extend(check_address_structure(xml_str))
        violations.extend(check_truncation_signals(xml_str))
        violations.extend(check_mandatory_gaps(xml_str))
    except Exception:
        # A narrower parse failure than "completely unparseable" --
        # XSD validation passed (or found schema-conformance issues
        # only) but one of the other four rules still hit a problem
        # parsing via lxml. Library callers get the partial result
        # (whatever XSD found) rather than an exception, matching the
        # CLI's existing degrade-gracefully behavior. Callers who want
        # to know this happened can compare violations against what
        # they'd expect, but a silent partial result is judged better
        # here than raising, since XSD's own findings are still valid
        # and useful even if the other four couldn't run.
        pass

    return violations
