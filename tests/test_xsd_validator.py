"""Tests for xsd_validator.py against the real vendored XSD.

These are the first genuinely working tests in the project -- not
testing stubs, testing real validation logic against the real schema.
Uses generator.synthetic_fixtures for input rather than hand-rolled
XML strings, so test fixtures and "real" usage exercise the same code
path.
"""

from pathlib import Path

import pytest

from tollgate.generator.synthetic_fixtures import build_valid_baseline
from tollgate.validation.models import RuleId
from tollgate.validation.xsd_validator import validate_xsd

SCHEMA_PATH = (
    Path(__file__).parent.parent
    / "src"
    / "tollgate"
    / "schemas"
    / "pacs.008.001.08.xsd"
)


def test_schema_file_exists():
    """Sanity check that runs before anything else -- if this fails,
    every other test's failure is misleading (it'll look like a logic
    bug when it's actually a missing vendored file).
    """
    assert SCHEMA_PATH.exists(), (
        f"Vendored XSD not found at {SCHEMA_PATH}. "
        "See docs/SOURCES.md#xsd-source to re-download."
    )


def test_valid_baseline_has_zero_violations():
    xml_str = build_valid_baseline(seed=42)
    violations = validate_xsd(xml_str, SCHEMA_PATH)
    assert violations == [], f"Expected zero violations, got: {violations}"


def test_missing_mandatory_field_is_caught():
    xml_str = build_valid_baseline(seed=42)
    broken = xml_str.replace("<ChrgBr>SHAR</ChrgBr>", "")
    violations = validate_xsd(broken, SCHEMA_PATH)

    assert len(violations) >= 1
    assert all(v.rule_id == RuleId.XSD_STRUCTURAL for v in violations)
    assert all(v.field_path for v in violations), "every violation needs a field_path"


def test_invalid_bic_pattern_is_caught():
    xml_str = build_valid_baseline(seed=42)
    broken = xml_str.replace("<BICFI>HBVWUS66</BICFI>", "<BICFI>123</BICFI>")
    violations = validate_xsd(broken, SCHEMA_PATH)

    assert len(violations) >= 1
    assert any("pattern" in v.message.lower() for v in violations)


def test_multiple_simultaneous_errors_all_collected():
    """The brief is explicit: don't just dump the first XSD error,
    collect everything wrong in one pass. This test exists specifically
    to catch a regression to stop-at-first-error behavior.
    """
    xml_str = build_valid_baseline(seed=42)
    broken = xml_str.replace("<ChrgBr>SHAR</ChrgBr>", "")
    broken = broken.replace("<BICFI>HBVWUS66</BICFI>", "<BICFI>123</BICFI>")

    violations = validate_xsd(broken, SCHEMA_PATH)
    assert len(violations) >= 2, (
        "Expected both the missing-ChrgBr error and the bad-BIC-pattern "
        "error to be collected in a single validation pass."
    )


def test_violations_have_required_fields_populated():
    """Every Violation must be usable by the explain/ layer downstream
    -- field_path and message can't be empty, since explain_violation()
    has nothing to narrate otherwise.
    """
    xml_str = build_valid_baseline(seed=42)
    broken = xml_str.replace("<ChrgBr>SHAR</ChrgBr>", "")
    violations = validate_xsd(broken, SCHEMA_PATH)

    for v in violations:
        assert v.field_path != ""
        assert v.message != ""
        assert v.severity in ("error", "warning")


@pytest.mark.parametrize("seed", [1, 2, 3, 4, 5])
def test_generator_produces_valid_messages_across_seeds(seed):
    """The generator's randomization (bank choice, names, currency,
    amount) shouldn't ever produce an accidentally-invalid message --
    if this fails for some seed, the generator has a structural bug,
    not a data bug.
    """
    xml_str = build_valid_baseline(seed=seed)
    violations = validate_xsd(xml_str, SCHEMA_PATH)
    assert violations == [], f"Seed {seed} produced violations: {violations}"
