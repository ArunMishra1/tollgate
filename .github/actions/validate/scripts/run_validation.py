#!/usr/bin/env python3
"""Helper script for the Tollgate GitHub Action.

Pulled out of action.yml deliberately: embedding multi-line Python
inside a bash heredoc inside a YAML block scalar is fragile and hard
to read -- a real YAML syntax error was found in an earlier draft of
action.yml caused by exactly this nesting. A standalone script is
easier to test, easier to read, and avoids YAML/bash/Python
quoting interactions entirely.

Usage:
    python3 run_validation.py "<glob-pattern>" <fail-on-warning: true|false>

Exits 1 if any file has an error-severity violation (or a warning,
if fail-on-warning is true). Prints the combined results as JSON to
stdout, and writes outputs to $GITHUB_OUTPUT if that env var is set.
"""

import glob
import json
import os
import subprocess
import sys


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: run_validation.py <glob-pattern> <fail-on-warning>", file=sys.stderr)
        return 1

    pattern, fail_on_warning_str = sys.argv[1], sys.argv[2]
    fail_on_warning = fail_on_warning_str.strip().lower() == "true"

    files = sorted(glob.glob(pattern, recursive=True))
    if not files:
        print(f"::error::No files matched path pattern: {pattern}")
        return 1

    combined_results = []
    overall_has_errors = False

    for file_path in files:
        print(f"Validating {file_path}...")
        proc = subprocess.run(
            ["tollgate", "validate", file_path, "--json"],
            capture_output=True,
            text=True,
        )

        try:
            entry = json.loads(proc.stdout)
        except json.JSONDecodeError:
            print(f"::error file={file_path}::Tollgate produced unparseable output: {proc.stdout!r}")
            overall_has_errors = True
            continue

        entry["file"] = file_path
        combined_results.append(entry)

        if entry.get("has_errors"):
            print(f"::error file={file_path}::Tollgate found error-severity violation(s)")
            overall_has_errors = True

        if entry.get("has_warnings") and fail_on_warning:
            print(f"::error file={file_path}::Tollgate found warning-severity finding(s) (fail-on-warning enabled)")
            overall_has_errors = True

    results_json = json.dumps(combined_results)

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a") as f:
            f.write(f"has-errors={'true' if overall_has_errors else 'false'}\n")
            f.write("results-json<<TOLLGATE_EOF\n")
            f.write(results_json + "\n")
            f.write("TOLLGATE_EOF\n")

    print(results_json)
    return 1 if overall_has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
