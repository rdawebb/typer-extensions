"""Pytest configuration for the typer-aliases tests"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import pytest

from typer.testing import CliRunner


# Get the project root
PROJECT_ROOT = Path(__file__).parent.parent


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


def pytest_configure(config):
    """Register custom markers."""
    config.addinivalue_line(
        "markers",
        "isolated: mark test to run in isolated subprocess (deselect with '-m \"not isolated\"')",
    )


@pytest.fixture
def subprocess_runner():
    """Fixture for running code in isolated subprocess."""

    def run_code(code: str, env: dict | None = None):
        """Execute Python code in a subprocess with optional environment variables.

        Args:
            code: Python code to execute
            env: Optional dict of environment variables to set

        Returns:
            subprocess.CompletedProcess with stdout, stderr, and returncode
        """
        import subprocess as sp
        import os

        # Start with current environment
        run_env = os.environ.copy()

        # Update with any provided environment variables
        if env:
            run_env.update(env)

        # Add src to Python path so the package can be imported
        python_path = run_env.get("PYTHONPATH", "")
        src_path = str(PROJECT_ROOT / "src")
        if python_path:
            python_path = f"{src_path}:{python_path}"
        else:
            python_path = src_path
        run_env["PYTHONPATH"] = python_path

        return sp.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=run_env,
        )

    return run_code
