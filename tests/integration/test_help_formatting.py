"""Integration tests for help text formatting with aliases.

These tests focus on integration-level concerns not covered by unit/test_format.py:
- The show_aliases_in_help configuration flag
- Custom display format, separator, and max_num options (end-to-end)
- Dynamic alias mutations reflected in help output
- Rich markup mode toggle
- Edge cases (no docstring, unicode, very long alias lists)
"""


class TestHelpAliasDisplay:
    """Tests for alias display in help text."""

    def test_help_shows_aliases_grouped(self, app_with_aliases, assert_success):
        """Test that help displays aliases grouped with commands."""

        # Check that aliases are shown with commands
        assert_success(
            app_with_aliases,
            ["--help"],
            ["list", "delete", "(ls, l)", "(rm)", "List all items", "Delete an item"],
        )

    def test_help_respects_show_aliases_config(self, app_with_aliases, assert_success):
        """Test that show_aliases_in_help config disables display."""
        app_with_aliases.show_aliases_in_help = False

        # Should show command help without aliases
        assert_success(
            app_with_aliases,
            ["--help"],
            ["list", "delete", "List all items", "Delete an item"],
            not_expected=["(ls, l)", "(rm)"],
        )

    def test_help_truncates_many_aliases(self, app, assert_success):
        """Test that many aliases are truncated with +N more."""
        app.max_num_aliases = 2

        @app.command("list", aliases=["a", "b", "c", "d"])
        def list_items():
            """List items."""
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

        # Should show first 2 and +2 more
        assert_success(app, ["--help"], ["list", "delete", "(a, b, +2 more)", "(rm)"])


class TestHelpWithMixedCommands:
    """Tests for help with mix of aliased and non-aliased commands."""

    def test_mixed_aliased_and_standard(self, app, assert_success):
        """Test mix of aliased and non-aliased commands."""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command()
        def create():
            """Create item."""
            pass

        # Non-aliased command should show normally
        assert_success(
            app,
            ["--help"],
            ["list", "create", "(ls)", "List items", "Create item"],
            not_expected=["(*)"],
        )

    def test_multiple_commands_various_alias_counts(
        self, app_with_aliases, assert_success
    ):
        """Test commands with different numbers of aliases."""

        @app_with_aliases.command()
        def status():
            """Show status."""
            pass

        # Should show all commands with correct number of aliases
        assert_success(
            app_with_aliases,
            ["--help"],
            ["list", "delete", "status", "(ls, l)", "(rm)"],
            not_expected=["(*)"],
        )


class TestHelpWithDynamicAliases:
    """Tests for help display after dynamic alias changes."""

    def test_help_after_add_alias(self, app_with_commands, assert_success):
        """Test help updates after adding alias dynamically."""

        # Initially no aliases shown
        assert_success(
            app_with_commands,
            ["--help"],
            ["list", "delete"],
            not_expected=["(*)"],
        )

        # Add alias
        app_with_commands.add_alias("list", "ls")

        # Now aliases should appear
        assert_success(app_with_commands, ["--help"], ["list", "delete", "(ls)"])

    def test_help_after_remove_alias(self, app_with_aliases, assert_success):
        """Test help updates after removing alias."""

        # Initially shows both aliases
        assert_success(app_with_aliases, ["--help"], ["list", "delete", "(ls, l)"])

        # Remove one alias
        app_with_aliases.remove_alias("ls")

        # Now should only show remaining alias
        assert_success(
            app_with_aliases,
            ["--help"],
            ["list", "delete", "(l)"],
            not_expected=["(ls)"],
        )

    def test_help_after_remove_all_aliases(self, app_with_aliases, assert_success):
        """Test help after removing all aliases."""

        # Remove all aliases
        app_with_aliases.remove_alias("ls")
        app_with_aliases.remove_alias("l")
        app_with_aliases.remove_alias("rm")

        # Should show command without aliases
        assert_success(
            app_with_aliases,
            ["--help"],
            ["list", "delete"],
            not_expected=["(ls, l)", "(rm)"],
        )


class TestHelpEdgeCases:
    """Tests for edge cases in help formatting."""

    def test_command_without_help_text(self, app, assert_success):
        """Test command without docstring/help text."""

        @app.command("list", aliases=["ls"])
        def list_items():
            pass  # No docstring

        @app.command("delete", aliases=["rm"])
        def delete_items():
            pass  # No docstring

        # Command with aliases should still show
        assert_success(app, ["--help"], ["list", "delete", "(ls)", "(rm)"])

    def test_very_long_alias_list(self, app, assert_success):
        """Test with many aliases beyond truncation limit."""
        app.max_num_aliases = 2

        aliases = [f"alias{i}" for i in range(10)]

        @app.command("cmd", aliases=aliases)
        def some_command():
            """Do something."""
            pass

        @app.command("another", aliases=["an1"])
        def another_command():
            """Show items."""
            pass

        # Should show truncation
        assert_success(app, ["--help"], ["cmd", "another", "+8 more"])

    def test_unicode_in_aliases(self, app, assert_success):
        """Test aliases with unicode characters."""

        @app.command("list", aliases=["列表", "リスト"])
        def list_items():
            """List items."""
            pass

        @app.command("delete", aliases=["削除", "さくじょ"])
        def delete_item():
            """Delete an item."""
            pass

        # Unicode aliases should display correctly
        assert_success(
            app, ["--help"], ["list", "delete", "(列表, リスト)", "(削除, さくじょ)"]
        )


class TestHelpRealWorldScenarios:
    """Tests for real-world help formatting scenarios."""

    def test_git_like_help(self, app, assert_success):
        """Test Git-like CLI help display."""

        @app.command("checkout", aliases=["co"])
        def checkout(branch: str):
            """Switch to a branch."""
            pass

        @app.command("commit", aliases=["ci"])
        def commit():
            """Record changes."""
            pass

        @app.command("status", aliases=["st"])
        def status():
            """Show working tree status."""
            pass

        # All commands with aliases & help texts
        assert_success(
            app,
            ["--help"],
            [
                "checkout",
                "commit",
                "status",
                "(co)",
                "(ci)",
                "(st)",
                "Switch to a branch",
                "Record changes",
                "Show working tree status",
            ],
        )

    def test_package_manager_help(self, app, assert_success):
        """Test package manager-like help display."""

        @app.command("install", aliases=["i", "add"])
        def install(package: str):
            """Install a package."""
            pass

        @app.command("remove", aliases=["rm", "uninstall", "delete"])
        def remove(package: str):
            """Remove a package."""
            pass

        @app.command("list", aliases=["ls", "l"])
        def list_packages():
            """List installed packages."""
            pass

        # Commands with various alias counts
        assert_success(
            app,
            ["--help"],
            [
                "install",
                "remove",
                "list",
                "(i, add)",
                "(rm, uninstall, delete)",
                "(ls, l)",
            ],
        )

    def test_help_without_rich_markup_mode(self, app_with_aliases, assert_success):
        """Test that help works when rich_markup_mode is not enabled."""
        app_with_aliases.rich_markup_mode = None

        # Should show plain text help
        assert_success(app_with_aliases, ["--help"], ["list", "delete"])
