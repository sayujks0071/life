"""Main CLI entry point."""

import typer

from spinalmodes.iec_cli import app as iec_app

app = typer.Typer(help="Spinal modes: Counter-curvature and IEC model")

# Register subcommands
app.add_typer(iec_app, name="iec")


@app.command()
def version():
    """Show version information."""
    from spinalmodes import __version__

    typer.echo(f"spinalmodes version {__version__}")


if __name__ == "__main__":
    app()

