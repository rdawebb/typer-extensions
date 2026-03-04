"""Integration tests for Argument with command aliases.

This module tests that positional arguments work identically whether invoked
via the primary command name or an alias. The alias routing mechanism itself
is tested exhaustively in unit/test_core.py and unit/test_programmatic_api.py;
these tests confirm arguments pass through correctly end-to-end.
"""

import pytest


class TestArgumentsWithAliases:
    """Tests for arguments working identically with primary commands and aliases."""

    @pytest.mark.parametrize(
        "cmd,arg,expected",
        [
            ("greet", "Alice", "Hello, Alice!"),
            ("hi", "Bob", "Hello, Bob!"),  # alias
            ("hello", "Charlie", "Hello, Charlie!"),  # second alias
        ],
    )
    def test_single_argument_routing(
        self, app_with_args, assert_success, cmd, arg, expected
    ):
        """Test single positional argument routes correctly via primary and aliases."""
        assert_success(app_with_args, [cmd, arg], expected)

    @pytest.mark.parametrize("cmd", ["copy", "cp"])
    def test_multiple_arguments_routing(self, app_with_args, assert_success, cmd):
        """Test multiple positional arguments route correctly via primary and alias."""
        assert_success(
            app_with_args,
            [cmd, "file1.txt", "file2.txt"],
            "Copying file1.txt to file2.txt",
        )

    @pytest.mark.parametrize(
        "cmd,count",
        [("process", "5"), ("proc", "10")],
    )
    def test_argument_with_type_conversion_int(
        self, app_with_args, assert_success, cmd, count
    ):
        """Test integer argument type conversion via primary and alias."""
        assert_success(app_with_args, [cmd, count], f"Processing {count} items")

    @pytest.mark.parametrize(
        "cmd,value,expected",
        [("calculate", "3.5", "7.0"), ("calc", "2.5", "5.0")],
    )
    def test_argument_with_type_conversion_float(
        self, app_with_args, assert_success, cmd, value, expected
    ):
        """Test float argument type conversion via primary and alias."""
        assert_success(app_with_args, [cmd, value], f"Result: {expected}")

    def test_optional_argument_with_default(self, app_with_args, assert_success):
        """Test optional argument uses default when omitted."""
        assert_success(app_with_args, ["say"], "Hello")
        assert_success(app_with_args, ["say", "Goodbye"], "Goodbye")
        assert_success(app_with_args, ["s", "Hi there"], "Hi there")  # alias

    def test_required_argument_missing_error(self, app_with_args, assert_failure):
        """Test error when required argument is missing."""
        assert_failure(app_with_args, ["greet"], expected_exit_code=2)


class TestArgumentsInHelp:
    """Tests for argument display in help text."""

    @pytest.mark.parametrize("cmd", ["greet", "hi"])
    def test_help_shows_argument(self, app_with_args, assert_success, cmd):
        """Test help shows argument info via primary command and alias."""
        assert_success(app_with_args, [cmd, "--help"], ["NAME", "Greet someone"])

    def test_help_shows_multiple_arguments(self, app_with_args, assert_success):
        """Test help shows all arguments for multi-argument commands."""
        assert_success(app_with_args, ["cp", "--help"], ["SRC", "DEST", "Copy a file"])


class TestArgumentsWithOptions:
    """Tests for combining arguments and options together."""

    @pytest.mark.parametrize(
        "cmd,flag,expected",
        [
            ("process", None, "Processing 4 items"),
            ("process", "--force", "Force processing 4 items"),
            ("proc", None, "Processing 4 items"),  # alias
            ("proc", "-f", "Force processing 4 items"),  # alias + short flag
        ],
    )
    def test_argument_and_option_together(
        self, app_with_args, assert_success, cmd, flag, expected
    ):
        """Test argument + option combination works via primary and alias."""
        args = [cmd, "4"] + ([flag] if flag else [])
        assert_success(app_with_args, args, expected)

    def test_multiple_arguments_and_options(self, app_with_args, assert_success):
        """Test command with multiple arguments and options."""
        assert_success(
            app_with_args,
            ["copy", "file1.txt", "file2.txt"],
            "Copying file1.txt to file2.txt",
        )
        assert_success(
            app_with_args,
            ["cp", "file1.txt", "file2.txt", "-f", "-b"],
            "Force copying with backup file1.txt to file2.txt",
        )

    def test_help_with_arguments_and_options(self, app_with_args, assert_success):
        """Test help shows all arguments and options."""
        assert_success(
            app_with_args,
            ["process", "--help"],
            ["COUNT", "--force", "Process a number of items"],
        )
