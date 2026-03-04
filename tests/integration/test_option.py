"""Integration tests for Option with command aliases.

This module tests that options work identically whether invoked via the primary
command name or an alias. The alias routing mechanism itself is testedin unit/test_core.py; these tests confirm options pass through correctly end-to-end.
"""

import pytest


class TestOptionsWithAliases:
    """Tests for options working identically with primary commands and aliases."""

    @pytest.mark.parametrize(
        "cmd,extra_args,expected",
        [
            ("process", [], "Processing"),
            ("process", ["--verbose"], "verbose mode"),
            ("proc", ["--verbose"], "verbose mode"),  # alias
            ("proc", ["-v"], "verbose mode"),  # alias + short flag
        ],
    )
    def test_boolean_option_routing(
        self, app_with_options, assert_success, cmd, extra_args, expected
    ):
        """Test boolean option flag routes correctly via primary and alias."""
        assert_success(app_with_options, [cmd] + extra_args, expected)

    @pytest.mark.parametrize(
        "cmd,flag",
        [("process", "--output"), ("proc", "-o")],
    )
    def test_option_with_value_routing(
        self, app_with_options, assert_success, cmd, flag
    ):
        """Test option with value routes correctly via primary and alias."""
        assert_success(
            app_with_options, [cmd, flag, "result.txt"], "output to result.txt"
        )

    def test_option_with_default_value(self, app_with_options, assert_success):
        """Test option uses default value when omitted."""
        assert_success(app_with_options, ["process"], "Processing 1")
        assert_success(app_with_options, ["p", "--count", "4"], "Processing 4")  # alias

    @pytest.mark.parametrize("cmd", ["process", "proc"])
    def test_multiple_options_together(self, app_with_options, assert_success, cmd):
        """Test multiple options together route correctly via primary and alias."""
        assert_success(
            app_with_options,
            [cmd, "-v", "--output", "result.txt", "--count", "4"],
            ["verbose mode", "result.txt", "4"],
        )

    @pytest.mark.parametrize("cmd", ["process", "p"])
    def test_short_flag_routing(self, app_with_options, assert_success, cmd):
        """Test short flag routes correctly via primary and alias."""
        assert_success(app_with_options, [cmd, "-v"], "verbose mode")


class TestOptionsInHelp:
    """Tests for option display in help text."""

    @pytest.mark.parametrize("cmd", ["process", "proc"])
    def test_help_shows_option(self, app_with_options, assert_success, cmd):
        """Test help shows option info via primary command and alias."""
        assert_success(
            app_with_options, [cmd, "--help"], ["--verbose", "Verbose output"]
        )
