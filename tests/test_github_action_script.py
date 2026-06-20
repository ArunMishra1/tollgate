"""Tests for .github/actions/validate/scripts/run_validation.py.

This script underwent a real fix during development: an earlier draft
embedded multi-line Python inside a bash heredoc inside action.yml's
YAML block scalar, which produced a YAML syntax error -- found only
by actually parsing the YAML with PyYAML rather than trusting it
looked right. Pulling the logic into this standalone script avoided
the fragile nesting entirely.
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

from tollgate.generator.synthetic_fixtures import build_valid_baseline, inject_error
from tollgate.validation.models import RuleId

SCRIPT_PATH = (
    Path(__file__).parent.parent
    / ".github"
    / "actions"
    / "validate"
    / "scripts"
    / "run_validation.py"
)


def test_script_file_exists():
    assert SCRIPT_PATH.exists(), f"Helper script not found at {SCRIPT_PATH}"


def _run_script(pattern: str, fail_on_warning: str = "false") -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), pattern, fail_on_warning],
        capture_output=True,
        text=True,
    )


def test_no_files_matched_fails_clearly(tmp_path):
    result = _run_script(str(tmp_path / "nonexistent" / "*.xml"))
    assert result.returncode == 1
    assert "No files matched" in result.stdout


def test_clean_file_passes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    xml_str = build_valid_baseline(seed=20)
    (tmp_path / "clean.xml").write_text(xml_str, encoding="utf-8")

    result = _run_script("clean.xml")
    assert result.returncode == 0

    output_lines = [l for l in result.stdout.splitlines() if l.startswith("[")]
    parsed = json.loads(output_lines[-1])
    assert parsed[0]["is_clean"] is True


def test_error_violation_fails_build(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    baseline = build_valid_baseline(seed=21)
    broken, _ = inject_error(baseline, RuleId.CHARSET_VIOLATION)
    (tmp_path / "broken.xml").write_text(broken, encoding="utf-8")

    result = _run_script("broken.xml")
    assert result.returncode == 1
    assert "::error" in result.stdout


def test_warning_only_passes_by_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    baseline = build_valid_baseline(seed=22)
    broken, _ = inject_error(baseline, RuleId.TRUNCATION_SUSPECTED)
    (tmp_path / "warning.xml").write_text(broken, encoding="utf-8")

    result = _run_script("warning.xml", fail_on_warning="false")
    assert result.returncode == 0


def test_warning_only_fails_when_fail_on_warning_enabled(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    baseline = build_valid_baseline(seed=23)
    broken, _ = inject_error(baseline, RuleId.TRUNCATION_SUSPECTED)
    (tmp_path / "warning.xml").write_text(broken, encoding="utf-8")

    result = _run_script("warning.xml", fail_on_warning="true")
    assert result.returncode == 1
    assert "::error" in result.stdout


def test_multiple_files_all_checked(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    (tmp_path / "clean.xml").write_text(build_valid_baseline(seed=24), encoding="utf-8")
    baseline = build_valid_baseline(seed=25)
    broken, _ = inject_error(baseline, RuleId.MANDATORY_FIELD_GAP)
    (tmp_path / "broken.xml").write_text(broken, encoding="utf-8")

    result = _run_script("*.xml")
    assert result.returncode == 1  # one of the two files has an error

    output_lines = [l for l in result.stdout.splitlines() if l.startswith("[")]
    parsed = json.loads(output_lines[-1])
    assert len(parsed) == 2


def test_glob_pattern_with_subdirectories(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    subdir = tmp_path / "payments"
    subdir.mkdir()
    (subdir / "clean.xml").write_text(build_valid_baseline(seed=26), encoding="utf-8")

    result = _run_script("payments/*.xml")
    assert result.returncode == 0
