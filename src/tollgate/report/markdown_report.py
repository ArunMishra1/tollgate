"""Renders a list of (Violation, explanation) pairs into report.md.

NOT YET IMPLEMENTED. Planned approach:
  - Group by severity (errors before warnings).
  - Each entry: rule_id, field_path, the deterministic message, then
    the AI explanation as prose underneath — visually distinct so a
    reader can tell which part is deterministic fact and which part
    is narrated, per the project's deterministic-check/AI-narration
    split.
  - Footer: scope disclaimer (not SWIFT-certified, pacs.008.001.08
    only, etc.) — same disclaimer language as the README, kept in
    one place and imported rather than duplicated.
"""

from pathlib import Path

from tollgate.validation.models import Violation


def render_report(violations_with_explanations: list[tuple[Violation, str]], output_path: Path) -> None:
    raise NotImplementedError("See module docstring for plan.")
