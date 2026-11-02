"""Integration tests for decorator usage in real CLI scenarios"""

from typer_extensions import Context, ExtendedTyper


def test_invoke_bare_decorator(cli) -> None:
    """Test invoking command decorated without parentheses"""
    app = ExtendedTyper()

    @app.command
    def hello():
        """Say hello."""
        print("Hello!")

    @app.command
    def goodbye():
        """Say goodbye."""

    assert "Hello!" in cli(app, "hello")


def test_decorator_with_typer_context(cli, make_app) -> None:
    """Test decorated command with Typer context"""
    app = make_app()

    @app.command("info", aliases=["i"])
    def show_info(ctx: Context):
        """Show info."""
        print(f"Command: {ctx.info_name}")

    assert "Command: info" in cli(app, "info")


def test_help_shows_no_alias_commands(cli, make_app) -> None:
    """Test that alias commands don't appear as rows of their own in help"""
    rows = [
        line.strip("│ ")
        for line in cli(make_app(), "--help").splitlines()
        if line.startswith("│")
    ]
    row_names = {row.split()[0] for row in rows if row}

    assert {"list", "delete"} <= row_names
    assert not {"ls", "l", "rm"} & row_names
