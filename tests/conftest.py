"""Pytest configuration for the typer-extensions tests"""

import re

import pytest
from typer.testing import CliRunner

from typer_extensions import ExtendedTyper


def strip_ansi_codes(text: str) -> str:
    """Remove ANSI escape codes from text for consistent assertion testing

    This is needed because different environments (local vs CI runners) may
    have different color output settings, but the actual text content should
    be the same

    Args:
        text: The text potentially containing ANSI escape codes

    Returns:
        The text with all ANSI escape codes removed
    """
    ansi_pattern = re.compile(r"\x1b\[[^\]]*?[@-~]|\x1b[^\[]")
    return ansi_pattern.sub("", text)


@pytest.fixture(autouse=True)
def _wide_terminal(monkeypatch) -> None:
    """Fix Rich's width, so a narrow terminal can't wrap asserted help text

    Typer reads TERMINAL_WIDTH once at import, so setting the variable here
    would depend on import order
    """
    monkeypatch.setattr("typer.rich_utils.MAX_WIDTH", 100)


@pytest.fixture
def cli():
    """Fixture to invoke an app, assert its outcome and return plain output"""
    runner = CliRunner()

    def run(app, *args: str, ok: bool = True, **kwargs) -> str:
        """Invoke the app with the given arguments

        Args:
            app: The Typer app to invoke
            *args: The command line arguments
            ok: Whether the invocation should succeed
            **kwargs: Additional keyword arguments for CliRunner.invoke

        Returns:
            The output with ANSI escape codes removed
        """
        result = runner.invoke(app, list(args), **kwargs)
        assert (result.exit_code == 0) is ok, result.output
        return strip_ansi_codes(result.output)

    return run


@pytest.fixture
def make_app():
    """Fixture to build a multi-command app, with 'list' and 'delete' commands"""

    def build(*, aliases: bool = True, **kwargs) -> ExtendedTyper:
        """Build the app

        Args:
            aliases: Whether to register the commands with aliases
            **kwargs: Keyword arguments for ExtendedTyper

        Returns:
            The app, where 'list' has aliases 'ls' and 'l', and 'delete' has 'rm'
        """
        app = ExtendedTyper(**kwargs)

        @app.command("list", aliases=["ls", "l"] if aliases else None)
        def list_items():
            """List all items."""
            print("Listing items...")

        @app.command("delete", aliases=["rm"] if aliases else None)
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        return app

    return build
