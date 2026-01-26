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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command()
        def create():
            """Create item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete item."""
            pass

        @app.command()
        def status():
            """Show status."""
            pass

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
            pass

        @app.command("very-long-command-name", aliases=["vlcn"])
        def long_cmd():
            """Long command."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("another", aliases=["an1"])
        def another_command():
            """Show items."""
            pass

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
            pass

        @app.command("delete", aliases=["削除", "さくじょ"])
        def delete_item():
            """Delete an item."""
            pass

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
            pass

        @app.command("commit", aliases=["ci"])
        def commit():
            """Record changes."""
            pass

        @app.command("status", aliases=["st"])
        def status():
            """Show working tree status."""
            pass

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
            pass

        @app.command("remove", aliases=["rm", "uninstall", "delete"])
        def remove(package: str):
            """Remove a package."""
            pass

        @app.command("list", aliases=["ls", "l"])
        def list_packages():
            """List installed packages."""
            pass

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
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should still show help text, though aliases may not be formatted
        assert "list" in clean_result
        assert "delete" in clean_result
