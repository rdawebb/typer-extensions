"""Integration tests for help text formatting with aliases."""

from typer_extensions import ExtendedTyper


class TestHelpAliasDisplay:
    """Tests for alias display in help text."""

    def test_help_shows_aliases_grouped(self, cli_runner, clean_output):
        """Test that help displays aliases grouped with commands."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Check that aliases are shown with commands
        assert "list" in clean_result
        assert "delete" in clean_result
        assert "(ls, l)" in clean_result
        assert "(rm)" in clean_result
        assert "List all items" in clean_result
        assert "Delete an item" in clean_result

    def test_help_respects_show_aliases_config(self, cli_runner, clean_output):
        """Test that show_aliases_in_help config disables display."""
        app = ExtendedTyper(show_aliases_in_help=False)

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Aliases should not be shown
        assert "(ls, l)" not in clean_result

        # But command should still be shown
        assert "list" in clean_result
        assert "List all items" in clean_result

    def test_help_truncates_many_aliases(self, cli_runner, clean_output):
        """Test that many aliases are truncated with +N more."""
        app = ExtendedTyper(max_num_aliases=2)

        @app.command("list", aliases=["a", "b", "c", "d"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show first 2 and +2 more
        assert "list" in clean_result
        assert "(a, b, +2 more)" in clean_result


class TestHelpCustomFormatting:
    """Tests for custom help formatting options."""

    def test_custom_display_format(self, cli_runner, clean_output):
        """Test custom alias display format."""
        app = ExtendedTyper(alias_display_format="[{aliases}]")

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should use brackets instead of parentheses
        assert "list" in clean_result
        assert "[ls]" in clean_result
        assert "(ls)" not in clean_result

    def test_custom_separator(self, cli_runner, clean_output, assert_formatted_cmd):
        """Test custom alias separator."""
        app = ExtendedTyper(alias_separator=" | ")

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should use pipe separator
        assert_formatted_cmd(clean_result, "list", "ls | l")
        assert_formatted_cmd(clean_result, "delete", "rm")

    def test_combined_custom_options(
        self, cli_runner, clean_output, assert_formatted_cmd
    ):
        """Test multiple custom formatting options together."""
        app = ExtendedTyper(
            alias_display_format="| {aliases}",
            alias_separator=", ",
            max_num_aliases=2,
        )

        @app.command("cmd", aliases=["a", "b", "c"])
        def some_command():
            """Do something."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show combined custom options
        assert_formatted_cmd(clean_result, "cmd", "a, b, +1 more")
        assert_formatted_cmd(clean_result, "delete", "rm")


class TestHelpWithMixedCommands:
    """Tests for help with mix of aliased and non-aliased commands."""

    def test_mixed_aliased_and_standard(self, cli_runner, clean_output):
        """Test mix of aliased and non-aliased commands."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""

        @app.command()
        def create():
            """Create item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Aliased command shows aliases
        assert "list" in clean_result
        assert "(ls)" in clean_result

        # Non-aliased command shows normally
        assert "create" in clean_result
        assert "(*)" not in clean_result

    def test_multiple_commands_various_alias_counts(self, cli_runner, clean_output):
        """Test commands with different numbers of aliases."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l", "dir"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete item."""

        @app.command()
        def status():
            """Show status."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Multiple aliases
        assert "list" in clean_result
        assert "(ls, l, dir)" in clean_result

        # Single alias
        assert "delete" in clean_result
        assert "(rm)" in clean_result

        # No aliases
        assert "status" in clean_result
        assert "(*)" not in clean_result


class TestHelpAlignment:
    """Tests for help text alignment with aliases."""

    def test_alignment_preserved(self, cli_runner, clean_output):
        """Test that command descriptions still align properly."""
        app = ExtendedTyper()

        @app.command("short", aliases=["s"])
        def short_cmd():
            """Short command."""

        @app.command("very-long-command-name", aliases=["vlcn"])
        def long_cmd():
            """Long command."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Both commands should be in output
        assert "short" in clean_result
        assert "very-long-command-name" in clean_result
        assert "(s)" in clean_result
        assert "(vlcn)" in clean_result

        # Descriptions should be present
        assert "Short command" in clean_result
        assert "Long command" in clean_result


class TestHelpWithDynamicAliases:
    """Tests for help display after dynamic alias changes."""

    def test_help_after_add_alias(self, cli_runner, clean_output):
        """Test help updates after adding alias dynamically."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        clean_result = clean_output(result.output)

        # Initially no aliases shown
        assert "list (" not in clean_result

        # Add alias
        app.add_alias("list", "ls")

        result = cli_runner.invoke(app, ["--help"])
        clean_result = clean_output(result.output)

        # Now aliases should appear
        assert "list" in clean_result
        assert "(ls)" in clean_result

    def test_help_after_remove_alias(self, cli_runner, clean_output):
        """Test help updates after removing alias."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        clean_result = clean_output(result.output)

        # Initially shows both aliases
        assert "list" in clean_result
        assert "(ls, l)" in clean_result

        # Remove one alias
        app.remove_alias("ls")

        result = cli_runner.invoke(app, ["--help"])
        clean_result = clean_output(result.output)

        # Should show only remaining alias
        assert "(l)" in clean_result
        assert "(ls)" not in clean_result

    def test_help_after_remove_all_aliases(self, cli_runner, clean_output):
        """Test help after removing all aliases."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        # Remove the alias
        app.remove_alias("ls")
        app.remove_alias("rm")

        result = cli_runner.invoke(app, ["--help"])
        clean_result = clean_output(result.output)

        # Should show command without aliases
        assert "list" in clean_result
        assert "delete" in clean_result
        assert "(ls)" not in clean_result
        assert "(rm)" not in clean_result


class TestHelpEdgeCases:
    """Tests for edge cases in help formatting."""

    def test_command_without_help_text(self, cli_runner, clean_output):
        """Test command without docstring/help text."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass  # No docstring

        @app.command("delete", aliases=["rm"])
        def delete_items():
            pass  # No docstring

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Command with aliases should still show
        assert "list" in clean_result
        assert "delete" in clean_result
        assert "(ls)" in clean_result
        assert "(rm)" in clean_result

    def test_very_long_alias_list(self, cli_runner, clean_output):
        """Test with many aliases beyond truncation limit."""
        app = ExtendedTyper(max_num_aliases=2)

        aliases = [f"alias{i}" for i in range(10)]

        @app.command("cmd", aliases=aliases)
        def some_command():
            """Do something."""

        @app.command("another", aliases=["an1"])
        def another_command():
            """Show items."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show truncation
        assert "+8 more" in clean_result

    def test_unicode_in_aliases(self, cli_runner, clean_output):
        """Test aliases with unicode characters."""
        app = ExtendedTyper()

        @app.command("list", aliases=["列表", "リスト"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["削除", "さくじょ"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Unicode aliases should display
        assert "列表" in clean_result
        assert "リスト" in clean_result


class TestHelpRealWorldScenarios:
    """Tests for real-world help formatting scenarios."""

    def test_git_like_help(self, cli_runner, clean_output):
        """Test Git-like CLI help display."""
        app = ExtendedTyper()

        @app.command("checkout", aliases=["co"])
        def checkout(branch: str):
            """Switch to a branch."""

        @app.command("commit", aliases=["ci"])
        def commit():
            """Record changes."""

        @app.command("status", aliases=["st"])
        def status():
            """Show working tree status."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # All commands with aliases
        assert "checkout" in clean_result
        assert "commit" in clean_result
        assert "status" in clean_result
        assert "(co)" in clean_result
        assert "(ci)" in clean_result
        assert "(st)" in clean_result

        # Help texts present
        assert "Switch to a branch" in clean_result
        assert "Record changes" in clean_result
        assert "Show working tree status" in clean_result

    def test_package_manager_help(self, cli_runner, clean_output):
        """Test package manager-like help display."""
        app = ExtendedTyper()

        @app.command("install", aliases=["i", "add"])
        def install(package: str):
            """Install a package."""

        @app.command("remove", aliases=["rm", "uninstall", "delete"])
        def remove(package: str):
            """Remove a package."""

        @app.command("list", aliases=["ls", "l"])
        def list_packages():
            """List installed packages."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Commands with various alias counts
        assert "install" in clean_result
        assert "remove" in clean_result
        assert "list" in clean_result
        assert "(i, add)" in clean_result
        assert "(rm, uninstall, delete)" in clean_result
        assert "(ls, l)" in clean_result

    def test_help_without_rich_markup_mode(self, cli_runner, clean_output):
        """Test that help works when rich_markup_mode is not enabled."""
        app = ExtendedTyper(rich_markup_mode=None)

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items."""

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should still show help text, with aliases formatted
        assert "list" in clean_result
        assert "delete" in clean_result
        assert "(ls)" in clean_result
        assert "(rm)" in clean_result


class TestPlainHelpAliasDisplay:
    """Tests for alias display in plain (non-Rich) help.

    Typer renders help through Click's formatter whenever Rich is inactive,
    bypassing rich_utils entirely, so the alias column is produced by
    ExtendedGroup.format_commands instead.
    """

    @staticmethod
    def _plain_app(**kwargs) -> ExtendedTyper:
        """Build an app that renders help through Click's plain formatter."""
        app = ExtendedTyper(rich_markup_mode=None, **kwargs)

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""

        @app.command("delete", aliases=["rm"], deprecated=True)
        def delete_item():
            """Delete an item."""

        @app.command("status")
        def status():
            """Show status."""

        @app.command("secret", aliases=["s"], hidden=True)
        def secret():
            """Hidden command."""

        return app

    def test_plain_help_shows_aliases(self, cli_runner, clean_output):
        """Test that aliases appear alongside commands in plain help."""
        result = cli_runner.invoke(self._plain_app(), ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Rich panels would draw a box, so confirm this really is plain help
        assert "╭" not in clean_result

        assert "(ls, l)" in clean_result
        assert "(rm)" in clean_result
        assert "List all items" in clean_result

    def test_plain_help_keeps_unaliased_commands(self, cli_runner, clean_output):
        """Test that commands without aliases are still listed, without a marker."""
        result = cli_runner.invoke(self._plain_app(), ["--help"])
        clean_result = clean_output(result.output)

        assert "status" in clean_result
        assert "Show status" in clean_result

    def test_plain_help_omits_hidden_commands(self, cli_runner, clean_output):
        """Test that hidden commands stay hidden, along with their aliases."""
        result = cli_runner.invoke(self._plain_app(), ["--help"])
        clean_result = clean_output(result.output)

        assert "secret" not in clean_result
        assert "(s)" not in clean_result

    def test_plain_help_omits_empty_command_section(self, cli_runner, clean_output):
        """Test that an all-hidden group writes no Commands section at all."""
        app = ExtendedTyper(rich_markup_mode=None)

        @app.command("list", aliases=["ls"], hidden=True)
        def list_items():
            """List all items."""

        @app.command("status", hidden=True)
        def status():
            """Show status."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "Commands:" not in clean_result

    def test_plain_help_marks_deprecated_commands(self, cli_runner, clean_output):
        """Test that Click's deprecation marker survives alias formatting."""
        result = cli_runner.invoke(self._plain_app(), ["--help"])
        clean_result = clean_output(result.output)

        assert "DEPRECATED" in clean_result

    def test_plain_help_respects_show_aliases_config(self, cli_runner, clean_output):
        """Test that show_aliases_in_help=False disables display in plain help too."""
        app = self._plain_app(show_aliases_in_help=False)

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "(ls, l)" not in clean_result
        assert "list" in clean_result
        assert "List all items" in clean_result

    def test_plain_help_respects_custom_format(self, cli_runner, clean_output):
        """Test that plain help honours the alias display settings."""
        app = self._plain_app(
            alias_display_format="[{aliases}]",
            alias_separator=" | ",
            max_num_aliases=1,
        )

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "[ls | +1 more]" in clean_result

    def test_plain_help_without_aliases_is_unchanged(self, cli_runner, clean_output):
        """Test that an app with no aliases falls through to Typer's own output."""
        app = ExtendedTyper(rich_markup_mode=None)

        @app.command("list")
        def list_items():
            """List all items."""

        @app.command("status")
        def status():
            """Show status."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "Commands:" in clean_result
        assert "list" in clean_result
        assert "(" not in clean_result.split("Commands:")[1]

    def test_plain_help_shows_aliases_without_rich(self, subprocess_runner):
        """Test the alias column when Rich is genuinely unavailable.

        This path reaches Click's formatter through rich_format_help's fallback
        rather than Typer's, so it needs a subprocess where 'rich' cannot import.
        """
        code = """
import builtins

real_import = builtins.__import__

def fake_import(name, *args, **kwargs):
    if name.startswith("rich"):
        raise ImportError("No module named 'rich'")
    return real_import(name, *args, **kwargs)

builtins.__import__ = fake_import

from typer.testing import CliRunner
from typer_extensions import ExtendedTyper
from typer_extensions._rich_utils import RICH_AVAILABLE

assert RICH_AVAILABLE is False, "Rich should be unavailable in this subprocess"

app = ExtendedTyper()

@app.command("list", aliases=["ls", "l"])
def list_items():
    \"\"\"List all items.\"\"\"

@app.command("status")
def status():
    \"\"\"Show status.\"\"\"

builtins.__import__ = real_import

result = CliRunner().invoke(app, ["--help"])
print(result.output)
"""
        result = subprocess_runner(code)
        assert result.returncode == 0, result.stderr
        assert "(ls, l)" in result.stdout
        assert "List all items" in result.stdout
        assert "status" in result.stdout

    def test_plain_help_survives_formatting_failure(self, cli_runner, clean_output):
        """Test that a broken alias format still renders usable help."""
        # An unknown placeholder makes str.format raise inside the formatter
        app = self._plain_app(alias_display_format="({unknown})")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "list" in clean_result
        assert "List all items" in clean_result
