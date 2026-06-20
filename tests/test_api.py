"""Tests for tollgate.api -- the public library API.

This is the integration surface for anyone calling Tollgate
programmatically (a CI pipeline, a payment service's own pre-submission
check) rather than via the CLI. The most important property these
tests check: check_message() works on a raw string/bytes with NO file
on disk at all -- that's the whole point of having a library API
distinct from the CLI's file-based interface.
"""

from pathlib import Path

import pytest

from tollgate import CheckResult, check_file, check_message
from tollgate.generator.synthetic_fixtures import build_valid_baseline, inject_error
from tollgate.validation.models import RuleId


def test_check_message_on_clean_string_has_no_violations():
    xml_str = build_valid_baseline(seed=10)
    result = check_message(xml_str)

    assert isinstance(result, CheckResult)
    assert result.is_clean
    assert not result.has_errors
    assert not result.has_warnings
    assert result.violations == []


def test_check_message_works_with_no_file_on_disk_at_all():
    """The defining property of a library API vs. a CLI: no
    Path/file involved anywhere in this test.
    """
    baseline = build_valid_baseline(seed=11)
    broken, _ = inject_error(baseline, RuleId.CHARSET_VIOLATION)

    result = check_message(broken)
    assert result.has_errors
    assert len(result.violations) >= 1


def test_check_message_accepts_bytes():
    baseline = build_valid_baseline(seed=12)
    broken, _ = inject_error(baseline, RuleId.CHARSET_VIOLATION)

    result_str = check_message(broken)
    result_bytes = check_message(broken.encode("utf-8"))

    assert result_str.has_errors == result_bytes.has_errors
    assert len(result_str.violations) == len(result_bytes.violations)


def test_check_message_rejects_unsupported_message_type():
    xml_str = build_valid_baseline(seed=13)
    with pytest.raises(ValueError, match="Unsupported message_type"):
        check_message(xml_str, message_type="pacs.009")


def test_check_file_reads_and_checks_a_real_file(tmp_path):
    xml_str = build_valid_baseline(seed=14)
    path = tmp_path / "payment.xml"
    path.write_text(xml_str, encoding="utf-8")

    result = check_file(path)
    assert result.is_clean


def test_check_file_accepts_str_path_not_just_path_object(tmp_path):
    xml_str = build_valid_baseline(seed=15)
    path = tmp_path / "payment.xml"
    path.write_text(xml_str, encoding="utf-8")

    result = check_file(str(path))  # str, not Path
    assert result.is_clean


def test_check_file_raises_builtin_exceptions_not_caught(tmp_path):
    """Unlike the CLI, the library should let normal Python exceptions
    surface -- a caller decides how to handle a missing file, not
    Tollgate printing a console message on the caller's behalf.
    """
    with pytest.raises(FileNotFoundError):
        check_file(tmp_path / "does_not_exist.xml")


def test_check_result_to_dict_is_json_serializable():
    import json

    baseline = build_valid_baseline(seed=16)
    broken, _ = inject_error(baseline, RuleId.MANDATORY_FIELD_GAP)

    result = check_message(broken)
    d = result.to_dict()

    # Must not raise -- this is the actual contract, not just "returns a dict"
    serialized = json.dumps(d)
    assert "mandatory_field_gap" in serialized
    assert isinstance(d["violations"][0]["rule_id"], str)  # enum converted to plain string


def test_check_result_to_dict_on_clean_message():
    xml_str = build_valid_baseline(seed=17)
    result = check_message(xml_str)
    d = result.to_dict()

    assert d["is_clean"] is True
    assert d["violations"] == []


def test_check_message_with_explain_false_has_empty_explanations():
    baseline = build_valid_baseline(seed=18)
    broken, _ = inject_error(baseline, RuleId.CHARSET_VIOLATION)

    result = check_message(broken, explain=False)
    assert result.explanations == {}


def test_check_message_with_explain_true_and_no_api_key_raises(monkeypatch):
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    baseline = build_valid_baseline(seed=19)
    broken, _ = inject_error(baseline, RuleId.CHARSET_VIOLATION)

    with pytest.raises(RuntimeError, match="ANTHROPIC_API_KEY"):
        check_message(broken, explain=True)


def test_top_level_import_works():
    """from tollgate import check_message -- this is the whole point
    of __init__.py exposing the API; if this import shape breaks,
    every usage example in the README breaks with it.
    """
    import tollgate

    assert hasattr(tollgate, "check_message")
    assert hasattr(tollgate, "check_file")
    assert hasattr(tollgate, "CheckResult")
