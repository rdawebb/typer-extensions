"""Pytest configuration for the typer-aliases tests"""

import re

import pytest

from typer.testing import CliRunner


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


def assert_formatted_command(
    output: str, command: str, aliases: str, separator: str = ", "
) -> None:
    """Assert that a formatted command appears in the output with its aliases.

    Ignores padding/spacing differences.

    Args:
        output: The output text to search.
        command: The command name to find.
        aliases: The expected aliases for the command.
        separator: The separator used between aliases.
    """
    pattern = rf"{re.escape(command)}\s+.*?{re.escape(aliases)}"
    assert re.search(pattern, output), (
        f"Command '{command}' with aliases '{aliases}' not found in output.\n"
        f"Output:\n{output}"
    )


@pytest.fixture
def cli_runner() -> CliRunner:
    """Fixture for the CLI test runner"""
    return CliRunner()


@pytest.fixture
def clean_output():
    """Fixture providing the strip_ansi_codes function for use in tests"""
    return strip_ansi_codes


@pytest.fixture
def assert_formatted_cmd():
    """Fixture providing the assert_formatted_command function for use in tests"""
    return assert_formatted_command
