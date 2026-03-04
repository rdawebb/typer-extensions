"""Pytest configuration and shared fixtures for typer_extensions tests.

This module provides common fixtures and utilities used across the test suite:
- Application fixtures (basic, case-insensitive, with pre-registered commands)
- Mock fixtures (Click commands, options, contexts)
- Helper functions for common assertions and setup
- Environment management fixtures
- CLI runner fixtures
"""

import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Callable, Dict, Optional
from unittest.mock import Mock

import click
import pytest
from typer.testing import CliRunner

from typer_extensions import ExtendedTyper

# Project root — used to inject src/ onto PYTHONPATH for subprocess tests
PROJECT_ROOT = Path(__file__).parent.parent

# =============================================================================
# CLI Runner Fixtures
# =============================================================================


@pytest.fixture
def cli_runner():
    """Provide a Click CLI test runner.

    Returns:
        CliRunner: A Click test runner for invoking CLI commands.

    Example:
        def test_my_command(cli_runner):
            app = ExtendedTyper()

            @app.command()
            def hello():
                print("Hello!")

            result = cli_runner.invoke(app, ["hello"])
            assert result.exit_code == 0
    """
    return CliRunner()


@pytest.fixture
def clean_output():
    """Provide a function to clean CLI output for easier testing.

    Removes ANSI color codes, extra whitespace, and normalizes line endings
    to make assertion matching easier.

    Returns:
        Callable: Function that takes output string and returns cleaned string.

    Example:
        def test_colored_output(cli_runner, clean_output):
            result = cli_runner.invoke(app, ["--help"])
            cleaned = clean_output(result.output)
            assert "Commands:" in cleaned
    """
    return _clean


# Internal function to clean output
def _clean(output: str) -> str:
    # Remove ANSI escape codes
    ansi_escape = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
    cleaned = ansi_escape.sub("", output)

    # Normalize whitespace
    cleaned = re.sub(r"\s+", " ", cleaned)

    # Remove leading/trailing whitespace
    cleaned = cleaned.strip()

    return cleaned


@pytest.fixture
def subprocess_runner():
    """Provide a subprocess runner for isolated Python execution.

    Useful for testing import-time behavior and environment variables.

    Returns:
        Callable: Function that runs Python code in subprocess.

    Example:
        def test_env_var(subprocess_runner):
            code = '''
            import os
            os.environ["MY_VAR"] = "test"
            import mymodule
            print(mymodule.config)
            '''
            result = subprocess_runner(code, env={"MY_VAR": "test"})
            assert result.returncode == 0
    """

    def _run(
        code: str, env: Optional[Dict[str, str]] = None
    ) -> subprocess.CompletedProcess:
        full_env = os.environ.copy()
        if env:
            full_env.update(env)

        # Ensure the package is importable from src/ in subprocess
        python_path = full_env.get("PYTHONPATH", "")
        src_path = str(PROJECT_ROOT / "src")
        full_env["PYTHONPATH"] = (
            f"{src_path}:{python_path}" if python_path else src_path
        )

        return subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
            cwd=str(PROJECT_ROOT),
            env=full_env,
        )

    return _run


# =============================================================================
# Application Fixtures
# =============================================================================


@pytest.fixture
def app() -> ExtendedTyper:
    """Provide a basic ExtendedTyper instance.

    Returns:
        ExtendedTyper: A fresh ExtendedTyper instance with default settings.

    Example:
        def test_command(app, cli_runner):
            @app.command()
            def hello():
                print("Hello!")

            result = cli_runner.invoke(app, ["hello"])
            assert result.exit_code == 0
    """
    return ExtendedTyper()


@pytest.fixture
def app_case_insensitive() -> ExtendedTyper:
    """Provide a case-insensitive ExtendedTyper instance.

    Returns:
        ExtendedTyper: An ExtendedTyper with case_sensitive=False.

    Example:
        def test_case_insensitive(app_case_insensitive, cli_runner):
            @app_case_insensitive.command("Hello")
            def hello():
                print("Hi!")

            result = cli_runner.invoke(app_case_insensitive, ["HELLO"])
            assert result.exit_code == 0
    """
    return ExtendedTyper(alias_case_sensitive=False)


@pytest.fixture
def unreg_commands() -> tuple[Callable, Callable]:
    """Provide unregistered commands for testing.

    Returns:
        A tuple of unregistered command functions.
    """

    def list_items():
        """List all items."""
        print("Listing items...")

    def delete_item(name: str):
        """Delete an item."""
        print(f"Deleting item: {name}")

    return list_items, delete_item


@pytest.fixture
def app_with_commands() -> ExtendedTyper:
    """Provide an ExtendedTyper with registered commands without aliases.

    Returns:
        ExtendedTyper: An app with list and delete commands.

    Example:
        def test_list_command(app_with_commands, cli_runner):
            result = cli_runner.invoke(app_with_commands, ["list"])
            assert result.exit_code == 0
            assert "Listing items" in result.output
    """
    app = ExtendedTyper()

    @app.command("list")
    def list_items():
        """List all items."""
        print("Listing items...")

    @app.command("delete")
    def delete_item():
        """Delete an item."""
        print("Deleting item...")

    return app


@pytest.fixture
def app_with_aliases() -> ExtendedTyper:
    """Provide an ExtendedTyper with registered commands that use aliases.

    Returns:
        ExtendedTyper: An app with commands that have multiple aliases.
    """
    app = ExtendedTyper()

    @app.command("list", aliases=["ls", "l"])
    def list_items():
        """List all items."""
        print("Listing items...")

    @app.command("delete", aliases=["rm"])
    def delete_item():
        """Delete an item."""
        print("Deleting item...")

    return app


@pytest.fixture
def app_with_options() -> ExtendedTyper:
    """Provide an ExtendedTyper with commands that use various option types.

    Returns:
        ExtendedTyper: An app with commands demonstrating different option patterns.

    Example:
        def test_bool_option(app_with_options, cli_runner):
            result = cli_runner.invoke(app_with_options, ["process", "--verbose"])
            assert "verbose mode" in result.output
    """
    app = ExtendedTyper()

    @app.command("process", aliases=["proc", "p"])
    def process(
        verbose: bool = app.Option(False, "--verbose", "-v", help="Verbose output"),
        output: str = app.Option("output.txt", "--output", "-o", help="Output file"),
        count: int = app.Option(1, "--count", "-c", help="Number of items"),
    ):
        """Process items with various options."""
        mode = "verbose" if verbose else "normal"
        print(f"Processing {count} items in {mode} mode, output to {output}")

    @app.command("config", aliases=["cfg"])
    def config(
        set_value: bool = app.Option(False, "--set", help="Set configuration"),
        get_value: bool = app.Option(False, "--get", help="Get configuration"),
    ):
        """Manage configuration."""
        if set_value:
            print("Setting configuration")
        elif get_value:
            print("Getting configuration")
        else:
            print("No action specified")

    return app


@pytest.fixture
def app_with_args() -> ExtendedTyper:
    """Provide an ExtendedTyper with commands that use various argument types.

    Returns:
        ExtendedTyper: An app with commands demonstrating different argument patterns.

    Example:
        def test_bool_option(app_with_args, cli_runner):
            result = cli_runner.invoke(app_with_args, ["process", "--verbose"])
            assert "verbose mode" in result.output
    """
    app = ExtendedTyper()

    # Single positional argument
    @app.command("greet", aliases=["hello", "hi"])
    def greet(name: str):
        """Greet someone by name."""
        print(f"Hello, {name}!")

    # Multiple positional arguments & options
    @app.command("copy", aliases=["cp", "c"])
    def copy_file(
        src: str = app.Argument(..., help="Source file path"),
        dest: str = app.Argument(..., help="Destination file path"),
        force: bool = app.Option(False, "--force", "-f", help="Force overwrite"),
        backup: bool = app.Option(False, "--backup", "-b", help="Create a backup copy"),
    ):
        """Copy a file"""
        action = "Copying"
        if force:
            action = "Force copying"
        if backup:
            action += " with backup"

        print(f"{action} {src} to {dest}")

    # Default argument
    @app.command("say", aliases=["s"])
    def say(message: str = app.Argument("Hello")):
        """Say a message."""
        print(f"Message: {message}")

    # Int type conversion
    @app.command("process", aliases=["proc", "p"])
    def process(count: int, force: bool = app.Option(False, "--force", "-f")):
        """Process a number of items"""
        if force:
            print(f"Force processing {count} items")
        else:
            print(f"Processing {count} items")

    # Float type conversion
    @app.command("calculate", aliases=["calc"])
    def calculate(value: float):
        """Calculate something."""
        result = value * 2
        print(f"Result: {result}")

    return app


# =============================================================================
# Mock Fixtures
# =============================================================================


@pytest.fixture
def mock_cmd():
    """Provide a mock Click Command object.

    Returns:
        Mock: A mock Click Command with standard attributes.

    Example:
        def test_help_formatting(mock_cmd):
            mock_cmd.help = "Test help text"
            mock_cmd.deprecated = False
            # Use in tests that need a Click command
    """
    cmd = Mock(spec=click.Command)

    cmd.name = "test"
    cmd.help = "Test command"
    cmd.deprecated = False
    cmd.hidden = False
    cmd.params = []
    cmd.callback = Mock()

    return cmd


@pytest.fixture
def mock_opt():
    """Provide a mock ExtendedTyper Option object.

    Returns:
        Mock: A mock ExtendedTyper Option with standard attributes.

    Example:
        def test_option_help(mock_opt):
            mock_opt.name = "verbose"
            mock_opt.opts = ["--verbose", "-v"]
            # Use in tests that format option help
    """
    opt = Mock(spec=click.Option)

    opt.name = "test_option"
    opt.opts = ["--test", "-t"]
    opt.secondary_opts = []
    opt.help = "Test option help"
    opt.required = False
    opt.default = None
    opt.show_default = False
    opt.envvar = None
    opt.allow_from_auto_envvar = False
    opt.auto_envvar_prefix = None
    opt.hidden = False

    return opt


@pytest.fixture
def mock_arg():
    """Provide a mock ExtendedTyper Argument object.

    Returns:
        Mock: A mock ExtendedTyper Argument with standard attributes.

    Example:
        def test_argument_help(mock_arg):
            mock_arg.name = "filename"
            mock_arg.required = True
            # Use in tests that format argument help
    """
    arg = Mock(spec=click.Argument)

    arg.name = "test_arg"
    arg.help = "Test argument help"
    arg.required = True
    arg.default = None
    arg.envvar = None
    arg.hidden = False

    return arg


@pytest.fixture
def mock_ctx():
    """Provide a mock typer-extensions Context object.

    Returns:
        Mock: A mock typer-extensions Context with standard attributes.

    Example:
        def test_context_usage(mock_ctx):
            mock_ctx.info_name = "myapp"
            mock_ctx.parent = None
            # Use in tests that need a context
    """
    ctx = Mock(spec=click.Context)

    ctx.info_name = "test_app"
    ctx.parent = None
    ctx.obj = None
    ctx.auto_envvar_prefix = None
    ctx.show_default = False

    return ctx


# =============================================================================
# Environment Management Fixtures
# =============================================================================


@pytest.fixture
def clean_environment(monkeypatch):
    """Provide a clean environment with specific variables removed.

    Useful for testing environment variable behavior without interference.

    Returns:
        Callable: Function that removes specified env vars.

    Example:
        def test_env_behavior(clean_environment):
            clean_environment(["TYPER_EXTENSIONS_RICH", "DEBUG"])
            # Now test with clean environment
    """

    def _clean(var_names: list):
        for var_name in var_names:
            monkeypatch.delenv(var_name, raising=False)

    return _clean


@pytest.fixture
def set_env_vars(monkeypatch):
    """Provide a helper to set multiple environment variables.

    Returns:
        Callable: Function that sets env vars from a dict.

    Example:
        def test_with_env(set_env_vars):
            set_env_vars({
                "DEBUG": "1",
                "LOG_LEVEL": "info"
            })
            # Test with these env vars set
    """

    def _set(env_dict: Dict[str, str]):
        for key, value in env_dict.items():
            monkeypatch.setenv(key, value)

    return _set


# =============================================================================
# Helper Function Fixtures
# =============================================================================


@pytest.fixture
def create_basic_app_with_commands():
    """Provide a factory function for creating apps with custom commands.

    Returns:
        Callable: Function that creates an ExtendedTyper with specified commands.

    Example:
        def test_custom_commands(create_basic_app_with_commands):
            app = create_basic_app_with_commands({
                "hello": (lambda: print("Hi!"), ["hi", "h"]),
                "bye": (lambda: print("Goodbye!"), ["gb"])
            })
            # App now has hello and bye commands with aliases
    """

    def _create(commands: Dict[str, tuple]) -> ExtendedTyper:
        """Create an ExtendedTyper with specified commands.

        Args:
            commands: Dict mapping command names to (callback, aliases) tuples.

        Returns:
            ExtendedTyper with registered commands.
        """
        app = ExtendedTyper()

        for cmd_name, (callback, aliases) in commands.items():
            app.command(cmd_name, aliases=aliases)(callback)

        return app

    return _create


@pytest.fixture
def assert_formatted_cmd():
    """Assert that a formatted command appears in the output with its aliases.

    Ignores padding/spacing differences.

    Args:
        output: The output text to search.
        command: The command name to find.
        aliases: The expected aliases for the command.
        separator: The separator used between aliases.
    """

    def _assert(output: str, command: str, aliases: str, separator: str = ", ") -> None:
        pattern = rf"{re.escape(command)}\s+.*?{re.escape(aliases)}"
        assert re.search(pattern, output), (
            f"Command '{command}' with aliases '{aliases}' not found in output.\n"
            f"Output:\n{output}"
        )

    return _assert


@pytest.fixture
def assert_success(cli_runner):
    """Provide a helper function to assert command execution succeeds.

    Returns:
        Function that runs command and asserts success.

    Example:
        def test_commands(cli_runner, app, assert_success):
            @app.command()
            def hello():
                print("Hi!")

            assert_success(cli_runner, app, ["hello"], "Hi!")
    """

    def _assert(
        app: ExtendedTyper,
        args: list[str],
        expected: Optional[str | list[str]] = None,
        not_expected: Optional[str | list[str]] = None,
    ) -> None:
        """Assert that a command succeeds and optionally check output.

        Args:
            app: ExtendedTyper application.
            args: Command arguments.
            expected: String or list of strings expected in output.
            not_expected: String or list of strings NOT expected in output.
        """
        result = cli_runner.invoke(app, args)
        assert result.exit_code == 0, f"Command failed: {result.output}"

        if expected is not None:
            items = [expected] if isinstance(expected, str) else expected
            for exp in items:
                assert exp in _clean(result.output), (
                    f"Expected '{exp}' in output: {result.output}"
                )

        if not_expected is not None:
            items = [not_expected] if isinstance(not_expected, str) else not_expected
            for not_exp in items:
                assert not_exp not in _clean(result.output), (
                    f"Did not expect '{not_exp}' in output: {result.output}"
                )

    return _assert


@pytest.fixture
def assert_failure(cli_runner):
    """Provide a helper function to assert command execution fails.

    Returns:
        Function that runs command and asserts failure.

    Example:
        def test_invalid_command(cli_runner, app, assert_failure):
            assert_failure(cli_runner, app, ["nonexistent"])
    """

    def _assert(
        app: ExtendedTyper,
        args: list[str],
        expected_exit_code: Optional[int] = None,
        expected: Optional[str | list[str]] = None,
    ):
        """Assert that a command fails.

        Args:
            app: ExtendedTyper application.
            args: Command arguments.
            expected_exit_code: Optional specific exit code to check.
            expected: String or list of strings expected in output.
        """
        result = cli_runner.invoke(app, args)
        assert result.exit_code != 0, f"Command should have failed: {result.output}"

        if expected_exit_code is not None:
            assert result.exit_code == expected_exit_code, (
                f"Expected exit code {expected_exit_code}, got {result.exit_code}"
            )

        if expected is not None:
            items = [expected] if isinstance(expected, str) else expected
            for exp in items:
                assert exp in _clean(result.output), (
                    f"Expected '{exp}' in output: {result.output}"
                )

    return _assert


# =============================================================================
# Pytest Markers
# =============================================================================


def pytest_configure(config):
    """Register custom pytest markers."""
    config.addinivalue_line(
        "markers", "isolated: mark test as requiring isolated subprocess execution"
    )
    config.addinivalue_line("markers", "slow: mark test as slow running")
    config.addinivalue_line("markers", "integration: mark test as integration test")
    config.addinivalue_line("markers", "unit: mark test as unit test")


# =============================================================================
# Test Collection Customisation
# =============================================================================


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark tests in integration/ as integration tests
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # Mark tests in unit/ as unit tests
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)

        # Mark subprocess tests as isolated
        if "subprocess" in item.name.lower() or "isolated" in item.name.lower():
            item.add_marker(pytest.mark.isolated)
