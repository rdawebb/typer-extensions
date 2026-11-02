"""Integration tests for help text formatting with aliases."""

import pytest

from typer_extensions import ExtendedTyper


class TestHelpAliasDisplay:
    """Tests for alias display in help text."""

    def test_help_shows_aliases_grouped(self, cli, make_app) -> None:
        """Test that help displays aliases grouped with commands."""
        output = cli(make_app(), "--help")

        assert "list" in output
        assert "delete" in output
        assert "(ls, l)" in output
        assert "(rm)" in output
        assert "List all items" in output
        assert "Delete an item" in output

    def test_help_respects_show_aliases_config(self, cli, make_app) -> None:
        """Test that show_aliases_in_help config disables display."""
        output = cli(make_app(show_aliases_in_help=False), "--help")

        assert "(ls, l)" not in output
        assert "list" in output
        assert "List all items" in output

    def test_help_truncates_many_aliases(self, cli, make_app) -> None:
        """Test that many aliases are truncated with +N more."""
        output = cli(make_app(max_num_aliases=1), "--help")

        assert "(ls, +1 more)" in output


class TestHelpCustomFormatting:
    """Tests for custom help formatting options."""

    def test_custom_display_format(self, cli, make_app) -> None:
        """Test custom alias display format."""
        output = cli(make_app(alias_display_format="[{aliases}]"), "--help")

        assert "[ls, l]" in output
        assert "(ls, l)" not in output

    def test_custom_separator(self, cli, make_app) -> None:
        """Test custom alias separator."""
        output = cli(make_app(alias_separator=" | "), "--help")

        assert "(ls | l)" in output
        assert "(rm)" in output

    def test_combined_custom_options(self, cli, make_app) -> None:
        """Test multiple custom formatting options together."""
        app = make_app(alias_display_format="| {aliases}", max_num_aliases=1)

        output = cli(app, "--help")

        assert "| ls, +1 more" in output
        assert "| rm" in output


class TestHelpWithMixedCommands:
    """Tests for help with mix of aliased and non-aliased commands."""

    def test_multiple_commands_various_alias_counts(self, cli, make_app) -> None:
        """Test commands with different numbers of aliases."""
        app = make_app()

        @app.command()
        def status():
            """Show status."""

        output = cli(app, "--help")

        assert "(ls, l)" in output
        assert "(rm)" in output
        assert "status" in output


class TestHelpWithDynamicAliases:
    """Tests for help display after dynamic alias changes."""

    def test_help_after_add_alias(self, cli, make_app) -> None:
        """Test help updates after adding alias dynamically."""
        app = make_app(aliases=False)
        assert "(ls)" not in cli(app, "--help")

        app.add_alias("list", "ls")

        assert "(ls)" in cli(app, "--help")

    def test_help_after_remove_alias(self, cli, make_app) -> None:
        """Test help updates after removing alias."""
        app = make_app()
        assert "(ls, l)" in cli(app, "--help")

        app.remove_alias("ls")

        output = cli(app, "--help")
        assert "(l)" in output
        assert "(ls" not in output

    def test_help_after_remove_all_aliases(self, cli, make_app) -> None:
        """Test help after removing all aliases."""
        app = make_app()

        for alias in ("ls", "l", "rm"):
            app.remove_alias(alias)

        output = cli(app, "--help")
        assert "list" in output
        assert "delete" in output
        assert "(l" not in output
        assert "(rm)" not in output


class TestHelpEdgeCases:
    """Tests for edge cases in help formatting."""

    def test_command_without_help_text(self, cli) -> None:
        """Test command without docstring/help text."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass  # No docstring

        @app.command("delete", aliases=["rm"])
        def delete_items():
            pass  # No docstring

        output = cli(app, "--help")

        assert "(ls)" in output
        assert "(rm)" in output

    def test_unicode_in_aliases(self, cli) -> None:
        """Test aliases with unicode characters."""
        app = ExtendedTyper()

        @app.command("list", aliases=["列表", "リスト"])
        def list_items():
            """List items."""

        @app.command("delete", aliases=["削除", "さくじょ"])
        def delete_item():
            """Delete an item."""

        output = cli(app, "--help")

        assert "列表" in output
        assert "リスト" in output


class TestPlainHelpAliasDisplay:
    """Tests for alias display in plain (non-Rich) help.

    Typer renders help through Click's formatter whenever Rich is inactive,
    bypassing rich_utils entirely, so the alias column is produced by
    ExtendedGroup.format_commands instead.
    """

    @pytest.fixture
    def plain_app(self, make_app):
        """Fixture to build an app that renders help through Click's formatter."""

        def build(**kwargs) -> ExtendedTyper:
            """Build the app, adding deprecated, unaliased and hidden commands."""
            app = make_app(rich_markup_mode=None, **kwargs)

            @app.command("old", aliases=["o"], deprecated=True)
            def old():
                """Old command."""

            @app.command("status")
            def status():
                """Show status."""

            @app.command("secret", aliases=["s"], hidden=True)
            def secret():
                """Hidden command."""

            return app

        return build

    def test_plain_help_shows_aliases(self, cli, plain_app) -> None:
        """Test that aliases appear alongside commands in plain help."""
        output = cli(plain_app(), "--help")

        # Rich panels would draw a box, so confirm this really is plain help
        assert "╭" not in output

        assert "(ls, l)" in output
        assert "(rm)" in output
        assert "List all items" in output

    def test_plain_help_keeps_unaliased_commands(self, cli, plain_app) -> None:
        """Test that commands without aliases are still listed, without a marker."""
        output = cli(plain_app(), "--help")

        assert "status" in output
        assert "Show status" in output

    def test_plain_help_omits_hidden_commands(self, cli, plain_app) -> None:
        """Test that hidden commands stay hidden, along with their aliases."""
        output = cli(plain_app(), "--help")

        assert "secret" not in output
        assert "(s)" not in output

    def test_plain_help_omits_empty_command_section(self, cli) -> None:
        """Test that an all-hidden group writes no Commands section at all."""
        app = ExtendedTyper(rich_markup_mode=None)

        @app.command("list", aliases=["ls"], hidden=True)
        def list_items():
            """List all items."""

        @app.command("status", hidden=True)
        def status():
            """Show status."""

        assert "Commands:" not in cli(app, "--help")

    def test_plain_help_marks_deprecated_commands(self, cli, plain_app) -> None:
        """Test that Click's deprecation marker survives alias formatting."""
        assert "DEPRECATED" in cli(plain_app(), "--help")

    def test_plain_help_respects_show_aliases_config(self, cli, plain_app) -> None:
        """Test that show_aliases_in_help=False disables display in plain help too."""
        output = cli(plain_app(show_aliases_in_help=False), "--help")

        assert "(ls, l)" not in output
        assert "list" in output
        assert "List all items" in output

    def test_plain_help_respects_custom_format(self, cli, plain_app) -> None:
        """Test that plain help honours the alias display settings."""
        app = plain_app(
            alias_display_format="[{aliases}]",
            alias_separator=" | ",
            max_num_aliases=1,
        )

        assert "[ls | +1 more]" in cli(app, "--help")

    def test_plain_help_without_aliases_is_unchanged(self, cli, make_app) -> None:
        """Test that an app with no aliases falls through to Typer's own output."""
        app = make_app(aliases=False, rich_markup_mode=None)

        output = cli(app, "--help")

        assert "Commands:" in output
        assert "list" in output
        assert "(" not in output.split("Commands:")[1]

    def test_plain_help_shows_aliases_without_rich(
        self, cli, make_app, monkeypatch
    ) -> None:
        """Test the alias column when Rich is switched off with TYPER_USE_RICH=0.

        Typer reads the variable at import time into HAS_RICH, so patch that.
        """
        monkeypatch.setattr("typer.core.HAS_RICH", False)

        output = cli(make_app(), "--help")

        assert "╭" not in output
        assert "(ls, l)" in output
        assert "List all items" in output

    def test_plain_help_survives_formatting_failure(self, cli, plain_app) -> None:
        """Test that a broken alias format still renders usable help."""
        # An unknown placeholder makes str.format raise inside the formatter
        output = cli(plain_app(alias_display_format="({unknown})"), "--help")

        assert "list" in output
        assert "List all items" in output
