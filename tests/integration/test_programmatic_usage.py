"""Integration tests for programmatic API methods"""

import pytest
from typer_extensions import ExtendedTyper


class TestProgrammaticCommandInvocation:
    """Tests for invoking programmatically registered commands"""

    def test_invoke_programmatic_command(self, cli_runner):
        """Test invoking command registered programmatically"""
        app = ExtendedTyper()

        def list_items():
            print("Listing items...")

        def delete_item():
            print("Deleting item...")

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm", "del"])

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_after_add_alias(self, cli_runner):
        """Test that newly added alias works for invocation"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Initially, only "list" works
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0

        # Add alias
        app.add_alias("list", "ls")

        # Now "ls" should work
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_fails_after_remove_alias(self, cli_runner):
        """Test that removed alias no longer works"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            print("Listing items...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_items():
            print("Deleting items...")

        # Both aliases work initially
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        # Remove one alias
        app.remove_alias("ls")

        # Removed alias should fail
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        # Other alias still works
        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0


class TestProgrammaticWithArguments:
    """Tests for programmatic commands with arguments and options"""

    def test_programmatic_command_with_argument(self, cli_runner):
        """Test programmatically registered command with argument"""
        app = ExtendedTyper()

        def greet(name: str):
            print(f"Hello, {name}!")

        def farewell(name: str):
            print(f"Goodbye, {name}!")

        app.add_command(greet, "greet", aliases=["hi"])
        app.add_command(farewell, "farewell", aliases=["bye"])

        result = cli_runner.invoke(app, ["greet", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

        result = cli_runner.invoke(app, ["hi", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_programmatic_command_with_option(self, cli_runner):
        """Test programmatically registered command with option"""
        import typer

        app = ExtendedTyper()

        def list_items(verbose: bool = typer.Option(False, "--verbose", "-v")):
            if verbose:
                print("Listing (verbose)...")
            else:
                print("Listing...")

        def delete_item():
            print("Deleting item...")

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm", "del"])

        result = cli_runner.invoke(app, ["ls"])
        assert "Listing..." in result.output
        assert "verbose" not in result.output

        result = cli_runner.invoke(app, ["ls", "--verbose"])
        assert "verbose" in result.output


class TestDynamicAliasManagement:
    """Tests for dynamic alias management workflows."""

    def test_dynamic_alias_workflow(self, cli_runner):
        """Test a complete workflow of dynamic alias management."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Initially no aliases
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        # Add alias dynamically
        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        # Add another alias
        app.add_alias("list", "l")
        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0

        # Remove first alias
        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        # Second alias still works
        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0

    def test_plugin_system_simulation(self, cli_runner):
        """Test simulating a plugin system with dynamic commands"""
        app = ExtendedTyper()

        # Core commands
        @app.command("help")
        def show_help():
            print("Help text")

        @app.command("version")
        def show_version():
            print("Version 1.0")

        # "Install" a plugin by adding commands dynamically
        def plugin_command():
            print("Plugin command executed")

        app.add_command(plugin_command, "plugin-cmd", aliases=["pc", "plugin"])

        # Test plugin command works
        result = cli_runner.invoke(app, ["plugin-cmd"])
        assert result.exit_code == 0
        assert "Plugin command" in result.output

        result = cli_runner.invoke(app, ["pc"])
        assert result.exit_code == 0

        # "Uninstall" plugin by removing aliases
        app.remove_alias("pc")
        app.remove_alias("plugin")

        result = cli_runner.invoke(app, ["pc"])
        assert result.exit_code != 0


class TestMixingDecoratorAndProgrammatic:
    """Tests for mixing decorator and programmatic approaches"""

    def test_both_approaches_coexist(self, cli_runner):
        """Test that both approaches work together"""
        app = ExtendedTyper()

        # Decorator approach
        @app.command("list", aliases=["ls"])
        def list_items():
            print("Listing...")

        # Programmatic approach
        def delete_item():
            print("Deleting...")

        app.add_command(delete_item, "delete", aliases=["rm"])

        # Both work via primary names
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["delete"])
        assert result.exit_code == 0

        # Both work via aliases
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["rm"])
        assert result.exit_code == 0

    def test_add_alias_to_decorated_command(self, cli_runner):
        """Test adding alias to command registered with decorator"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            print("Listing...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        # Add another alias programmatically
        app.add_alias("list", "l")

        # All aliases work
        for cmd in ["list", "ls", "l"]:
            result = cli_runner.invoke(app, [cmd])
            assert result.exit_code == 0
            assert "Listing..." in result.output

    def test_query_mixed_commands(self, cli_runner):
        """Test querying aliases from mixed registration methods"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        def delete_item():
            pass

        app.add_command(delete_item, "delete", aliases=["rm"])

        # Query individual commands
        list_aliases = app.get_aliases("list")
        delete_aliases = app.get_aliases("delete")

        assert list_aliases == ["ls"]
        assert delete_aliases == ["rm"]

        # Query all
        all_aliases = app.list_commands_with_aliases()
        assert all_aliases == {"list": ["ls"], "delete": ["rm"]}


class TestHelpWithProgrammaticAPI:
    """Tests for help display with programmatic API"""

    def test_help_shows_programmatic_commands(self, cli_runner, clean_output):
        """Test that help shows programmatically registered commands"""
        app = ExtendedTyper()

        def list_items():
            """List all items."""
            pass

        app.add_command(
            list_items, "list", aliases=["ls"], help="List items in the system"
        )

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command and description
        assert "list" in clean_result

    def test_command_help_after_add_alias(self, cli_runner, clean_output):
        """Test that command help works after adding alias"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List all items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete an item."""
            pass

        app.add_alias("list", "ls")

        # Help via primary name
        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command description
        assert "List all items" in clean_result

        # Help via newly added alias
        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command description
        assert "List all items" in clean_result


class TestErrorHandling:
    """Tests for error handling in programmatic API."""

    def test_add_alias_nonexistent_command_error(self, cli_runner):
        """Test clear error when adding alias to non-existent command"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List all items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete an item."""
            pass

        try:
            app.add_alias("nonexistent", "ne")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "does not exist" in str(e)
            assert "nonexistent" in str(e)

    def test_duplicate_alias_error(self, cli_runner):
        """Test clear error when alias conflicts"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        app.add_alias("list", "ls")

        try:
            app.add_alias("delete", "ls")
            assert False, "Should have raised ValueError"
        except ValueError as e:
            assert "already registered" in str(e)


class TestRealWorldScenarios:
    """Tests for real-world usage patterns"""

    def test_configuration_based_aliases(self, cli_runner):
        """Test adding aliases based on configuration"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Simulate reading aliases from config
        config_aliases = {"list": ["ls", "l", "dir"]}

        # Add aliases from config
        for cmd, aliases in config_aliases.items():
            for alias in aliases:
                app.add_alias(cmd, alias)

        # All configured aliases work
        for alias in ["ls", "l", "dir"]:
            result = cli_runner.invoke(app, [alias])
            assert result.exit_code == 0

    def test_user_customisation_workflow(self, cli_runner):
        """Test workflow where user customises aliases"""
        app = ExtendedTyper()

        @app.command("checkout", aliases=["co"])
        def checkout(branch: str):
            print(f"Checked out {branch}")

        @app.command("merge", aliases=["m"])
        def merge(branch: str):
            print(f"Merged {branch} into current branch.")

        # User wants shorter alias
        app.add_alias("checkout", "c")

        # User prefers different name, removes default
        app.remove_alias("co")

        # User's preferences work
        result = cli_runner.invoke(app, ["c", "main"])
        assert result.exit_code == 0

        # Old alias doesn't work
        result = cli_runner.invoke(app, ["co", "main"])
        assert result.exit_code != 0

    def test_backwards_compatibility_aliases(self, cli_runner):
        """Test maintaining backwards compatibility with old command names"""
        app = ExtendedTyper()

        @app.command("add")
        def add_item(name: str):
            print(f"Added {name}")

        # New command name
        @app.command("remove")
        def remove_item(name: str):
            print(f"Removed {name}")

        # Add old command name as alias for backwards compatibility
        app.add_alias("remove", "delete")  # Old name
        app.add_alias("remove", "del")  # Even older name

        # All versions work
        for cmd in ["remove", "delete", "del"]:
            result = cli_runner.invoke(app, [cmd, "test"])
            assert result.exit_code == 0
            assert "Removed test" in result.output


class TestAliasReregistration:
    """Tests for re-adding aliases that have been removed"""

    def test_re_add_removed_alias(self, cli_runner):
        """Test that a removed alias can be re-added and work again"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Add alias
        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        # Remove alias
        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        # Re-add the same alias
        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_re_add_removed_alias_to_different_command(self, cli_runner):
        """Test that a removed alias can be added to a different command"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Add alias to "list"
        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        # Remove alias
        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        # Add the same alias to "delete"
        app.add_alias("delete", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Deleting items..." in result.output

    def test_cannot_add_active_alias(self, cli_runner):
        """Test that adding an alias that's currently active raises error"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Add alias to "list"
        app.add_alias("list", "ls")

        # Try to add the same alias to "delete" - should fail
        with pytest.raises(ValueError, match="already registered"):
            app.add_alias("delete", "ls")

    def test_re_add_multiple_times(self, cli_runner):
        """Test that an alias can be removed and re-added multiple times"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        # Add, remove, add, remove, add cycle
        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0


class TestRegularTyperWithMonkeyPatch:
    """Tests for regular Typer instances with the monkey patch applied"""

    def test_regular_typer_still_works(self, cli_runner):
        """Test that regular Typer apps still work after ExtendedTyper import"""
        import typer

        # Regular Typer (not ExtendedTyper)
        app = typer.Typer()

        @app.command("list")
        def list_items():
            """List items."""
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            """Delete items."""
            print("Deleting items...")

        # Should work as normal
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        result = cli_runner.invoke(app, ["delete"])
        assert result.exit_code == 0
        assert "Deleting items..." in result.output

    def test_regular_typer_help_still_works(self, cli_runner):
        """Test that regular Typer help text still works after ExtendedTyper import"""
        import typer

        app = typer.Typer()

        @app.command("list")
        def list_items():
            """List all items in the system."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items from the system."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "delete" in result.output
        assert "List all items" in result.output
