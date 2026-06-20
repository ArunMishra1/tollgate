"""Tollgate CLI.

    tollgate validate payment.xml --message-type pacs.008 --output report.md

This is a v1 skeleton: the `validate` command wires up the pipeline stages
but the stages themselves (xsd_validator, charset_rule, address_rule,
truncation_rule, mandatory_gap_rule, explainer) are not yet implemented.
Each raises NotImplementedError with a pointer to its module so this is
honest about being scaffolding, not a working tool yet.
"""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

app = typer.Typer(
    name="tollgate",
    help="Pre-submission safety gate for ISO 20022 payment messages.",
)
console = Console()


@app.command()
def validate(
    message_path: Path = typer.Argument(..., help="Path to the ISO 20022 XML message to check."),
    message_type: str = typer.Option(
        "pacs.008", "--message-type", help="Message type to validate against. v1 supports pacs.008 only."
    ),
    output: Optional[Path] = typer.Option(
        None, "--output", help="Write a markdown report to this path instead of printing to console."
    ),
) -> None:
    """Run the full validation pipeline against a single message file."""
    if message_type != "pacs.008":
        console.print(
            f"[red]Unsupported message type '{message_type}'.[/red] "
            "v1 only supports pacs.008.001.08. See README for scope."
        )
        raise typer.Exit(code=1)

    if not message_path.exists():
        console.print(f"[red]File not found:[/red] {message_path}")
        raise typer.Exit(code=1)

    console.print(f"[yellow]Tollgate v0.1.0 — scaffolding only.[/yellow]")
    console.print(f"Would validate: {message_path}")
    console.print("Pipeline stages (not yet implemented):")
    console.print("  1. XSD structural validation  -> src/tollgate/validation/xsd_validator.py")
    console.print("  2. SWIFT character set check   -> src/tollgate/validation/charset_rule.py")
    console.print("  3. Address structure check     -> src/tollgate/validation/address_rule.py")
    console.print("  4. Truncation heuristic check  -> src/tollgate/validation/truncation_rule.py")
    console.print("  5. MX-mandatory gap check      -> src/tollgate/validation/mandatory_gap_rule.py")
    console.print("  6. AI explanation layer        -> src/tollgate/explain/explainer.py")

    if output:
        console.print(f"\n(Would write report to {output} once stages are implemented.)")


@app.command()
def generate(
    count: int = typer.Option(10, "--count", help="Number of synthetic test fixtures to generate."),
    output_dir: Path = typer.Option(
        Path("tests/fixtures"), "--output-dir", help="Directory to write generated fixtures into."
    ),
) -> None:
    """Generate synthetic pacs.008 fixtures with labeled injected errors, for eval ground truth."""
    console.print("[yellow]Not yet implemented.[/yellow] See src/tollgate/generator/synthetic_fixtures.py")
    raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
