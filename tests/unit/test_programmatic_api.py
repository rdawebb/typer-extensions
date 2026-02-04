"""Comprehensive tests for programmatic API methods.

This module tests both the programmatic registration of commands (add_command) and dynamic alias management (add_alias, remove_alias, get_aliases, etc.) along with usage patterns and integration scenarios.
"""

import pytest
from typer_extensions import ExtendedTyper


# =============================================================================
# Command Registration Tests
# =============================================================================


class TestAddCommand:
    """Tests for add_command() method."""

    def test_add_command(self):
        """Test adding command with aliases programmatically."""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            print("listing")

        def delete_item():
            """Delete items."""
            pass

        app.add_command(list_items, "list", aliases=["ls", "l"])

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_add_command_without_aliases(self):
        """Test adding command without aliases."""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_item():
            """Delete items."""
            pass

        app.add_command(list_items, "list", aliases=None)

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_add_command_inferred_name(self):
        """Test adding command with inferred name."""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_item():
            """Delete items."""
            pass

        app.add_command(list_items, aliases=["ls"])

        assert "list_items" in app._command_aliases
        assert app._alias_to_command["ls"] == "list_items"

    def test_add_command_with_kwargs(self):
        """Test that kwargs are passed through."""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_item():
            """Delete items."""
            pass

        app.add_command(
            list_items, "list", aliases=["ls"], help="Custom help", deprecated=True
        )
        app.add_command(delete_item, "delete")

        import typer
        from click import Group

        click_obj = typer.main.get_command(app)
        if isinstance(click_obj, Group):
            registered_cmd = click_obj.commands.get("list")

            assert registered_cmd is not None
            assert registered_cmd.deprecated is True

    def test_add_multiple_commands(self):
        """Test adding multiple commands programmatically."""
        app = ExtendedTyper()

        def list_items():
            pass

        def delete_item():
            pass

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm"])

        assert len(app._command_aliases) == 2
        assert len(app._alias_to_command) == 2


class TestProgrammaticCommandInvocation:
    """Tests for invoking programmatically registered commands."""

    def test_invoke_programmatic_command(self, cli_runner, clean_output):
        """Test invoking command registered programmatically."""
        app = ExtendedTyper()

        def list_items():
            print("Listing items...")

        def delete_item():
            print("Deleting item...")

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm", "del"])

        result = cli_runner.invoke(app, ["list"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result


class TestProgrammaticWithArguments:
    """Tests for programmatic commands with arguments and options."""

    def test_programmatic_command_with_argument(self, cli_runner, clean_output):
        """Test programmatically registered command with argument."""
        app = ExtendedTyper()

        def greet(name: str):
            print(f"Hello, {name}!")

        def farewell(name: str):
            print(f"Goodbye, {name}!")

        app.add_command(greet, "greet", aliases=["hi"])
        app.add_command(farewell, "farewell", aliases=["bye"])

        result = cli_runner.invoke(app, ["greet", "World"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Hello, World!" in clean_result

        result = cli_runner.invoke(app, ["hi", "Alice"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Hello, Alice!" in clean_result

    def test_programmatic_command_with_option(self, cli_runner, clean_output):
        """Test programmatically registered command with option."""
        app = ExtendedTyper()

        def list_items(verbose: bool = app.Option(False, "--verbose", "-v")):
            if verbose:
                print("Listing (verbose)...")
            else:
                print("Listing...")

        def delete_item():
            print("Deleting item...")

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm", "del"])

        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert "Listing..." in clean_result
        assert "verbose" not in clean_result

        result = cli_runner.invoke(app, ["ls", "--verbose"])
        clean_result = clean_output(result.output)

        assert "verbose" in clean_result


# =============================================================================
# Dynamic Alias Management Tests
# =============================================================================


class TestAddAlias:
    """Tests for add_alias() method."""

    def test_add_alias_to_existing_command(self):
        """Test adding alias to command registered with standard decorator."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        app.add_alias("list", "ls")

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_add_alias_to_decorated_command(self):
        """Test adding alias to command registered with decorator."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete items."""
            pass

        app.add_alias("list", "l")

        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["l"] == "list"

    def test_add_multiple_aliases(self):
        """Test adding multiple aliases one at a time."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        app.add_alias("list", "ls")
        app.add_alias("list", "l")
        app.add_alias("list", "dir")

        assert app._command_aliases["list"] == ["ls", "l", "dir"]
        assert all(app._alias_to_command[a] == "list" for a in ["ls", "l", "dir"])

    def test_add_alias_nonexistent_command_raises(self):
        """Test that adding alias to non-existent command raises error."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        with pytest.raises(ValueError, match="Command 'nonexistent' does not exist"):
            app.add_alias("nonexistent", "ne")

    def test_add_duplicate_alias_raises(self):
        """Test that adding duplicate alias raises error."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        app.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app.add_alias("delete", "ls")

    def test_add_alias_case_insensitive(self):
        """Test adding alias with case insensitivity."""
        app = ExtendedTyper(alias_case_sensitive=False)

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        app.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app.add_alias("delete", "LS")

    def test_invoke_after_add_alias(self, cli_runner, clean_output):
        """Test that newly added alias works for invocation."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0

        app.add_alias("list", "ls")

        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result


class TestRemoveAlias:
    """Tests for remove_alias() method."""

    def test_remove_existing_alias(self):
        """Test removing an existing alias."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        result = app.remove_alias("ls")

        assert result is True
        assert "ls" not in app._alias_to_command
        assert app._command_aliases["list"] == ["l"]

    def test_remove_nonexistent_alias_returns_false(self):
        """Test that removing non-existent alias returns False."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        result = app.remove_alias("nonexistent")

        assert result is False

    def test_remove_alias_leaves_others(self):
        """Test that removing one alias doesn't affect others."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l", "dir"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        app.remove_alias("l")

        assert app._command_aliases["list"] == ["ls", "dir"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["dir"] == "list"
        assert "l" not in app._alias_to_command

    def test_remove_last_alias(self):
        """Test removing the last alias for a command."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        app.remove_alias("ls")

        assert "list" not in app._command_aliases
        assert "ls" not in app._alias_to_command

    def test_remove_alias_case_insensitive(self):
        """Test removing alias with case insensitivity."""
        app = ExtendedTyper(alias_case_sensitive=False)

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        result = app.remove_alias("LS")

        assert result is True
        assert "ls" not in app._alias_to_command

    def test_remove_same_alias_twice(self):
        """Test idempotency of remove_alias."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        result1 = app.remove_alias("ls")
        result2 = app.remove_alias("ls")

        assert result1 is True
        assert result2 is False

    def test_invoke_fails_after_remove_alias(self, cli_runner):
        """Test that removed alias no longer works."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            print("Listing items...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_items():
            print("Deleting items...")

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        app.remove_alias("ls")

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0


class TestGetAliases:
    """Tests for get_aliases() method."""

    def test_get_aliases_existing_command(self):
        """Test getting aliases for command with aliases."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l", "dir"])
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        aliases = app.get_aliases("list")

        assert aliases == ["ls", "l", "dir"]

    def test_get_aliases_no_aliases_returns_empty(self):
        """Test that command without aliases returns empty list."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        aliases = app.get_aliases("list")

        assert aliases == []

    def test_get_aliases_nonexistent_command_returns_empty(self):
        """Test that non-existent command returns empty list."""
        app = ExtendedTyper()

        aliases = app.get_aliases("nonexistent")

        assert aliases == []

    def test_get_aliases_returns_copy(self):
        """Test that get_aliases returns a copy, not reference."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        aliases = app.get_aliases("list")
        aliases.append("modified")

        original_aliases = app.get_aliases("list")
        assert original_aliases == ["ls", "l"]
        assert "modified" not in original_aliases

    def test_get_aliases_after_add(self):
        """Test getting aliases after dynamically adding one."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_items():
            pass

        app.add_alias("list", "ls")
        app.add_alias("list", "l")

        aliases = app.get_aliases("list")
        assert aliases == ["ls", "l"]

    def test_get_aliases_after_remove(self):
        """Test getting aliases after removing one."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l", "dir"])
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        app.remove_alias("l")

        aliases = app.get_aliases("list")
        assert aliases == ["ls", "dir"]


class TestListCommandsWithAliases:
    """Tests for list_commands_with_aliases() method."""

    def test_list_all_commands_with_aliases(self):
        """Test listing all commands that have aliases."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        mapping = app.list_commands_with_aliases()

        assert mapping == {"list": ["ls", "l"], "delete": ["rm"]}

    def test_list_empty_when_no_aliases(self):
        """Test that list is empty when no commands have aliases."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete")
        def delete_item():
            pass

        mapping = app.list_commands_with_aliases()

        assert mapping == {}

    def test_list_returns_copy(self):
        """Test that list returns a copy of the data."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        mapping = app.list_commands_with_aliases()
        mapping["list"].append("modified")
        mapping["new"] = ["test"]

        original_mapping = app.list_commands_with_aliases()
        assert original_mapping == {"list": ["ls"], "delete": ["rm"]}

    def test_list_excludes_commands_without_aliases(self):
        """Test that commands without aliases are excluded."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("hello")
        def say_hello():
            pass

        mapping = app.list_commands_with_aliases()

        assert "list" in mapping
        assert "hello" not in mapping

    def test_list_after_dynamic_changes(self):
        """Test listing after dynamically adding/removing aliases."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        app.add_alias("list", "ls")

        mapping = app.list_commands_with_aliases()
        assert mapping == {"list": ["ls"], "delete": ["rm"]}

        app.remove_alias("rm")

        mapping = app.list_commands_with_aliases()
        assert mapping == {"list": ["ls"]}


# =============================================================================
# Dynamic Alias Workflow Tests
# =============================================================================


class TestDynamicAliasWorkflows:
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

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        app.add_alias("list", "l")
        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0

        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0

    def test_plugin_system_simulation(self, cli_runner, clean_output):
        """Test simulating a plugin system with dynamic commands."""
        app = ExtendedTyper()

        @app.command("help")
        def show_help():
            print("Help text")

        @app.command("version")
        def show_version():
            print("Version 1.0")

        def plugin_command():
            print("Plugin command executed")

        app.add_command(plugin_command, "plugin-cmd", aliases=["pc", "plugin"])

        result = cli_runner.invoke(app, ["plugin-cmd"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Plugin command" in clean_result

        result = cli_runner.invoke(app, ["pc"])
        assert result.exit_code == 0

        app.remove_alias("pc")
        app.remove_alias("plugin")

        result = cli_runner.invoke(app, ["pc"])
        assert result.exit_code != 0


class TestAliasReregistration:
    """Tests for re-adding aliases that have been removed."""

    def test_re_add_removed_alias(self, cli_runner, clean_output):
        """Test that a removed alias can be re-added and work again."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

    def test_re_add_removed_alias_to_different_command(self, cli_runner, clean_output):
        """Test that a removed alias can be added to a different command."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        app.add_alias("list", "ls")
        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

        app.remove_alias("ls")
        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code != 0

        app.add_alias("delete", "ls")
        result = cli_runner.invoke(app, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Deleting items..." in clean_result

    def test_cannot_add_active_alias(self, cli_runner):
        """Test that adding an alias that's currently active raises error."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        app.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app.add_alias("delete", "ls")

    def test_re_add_multiple_times(self, cli_runner):
        """Test that an alias can be removed and re-added multiple times."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        for _ in range(3):
            app.add_alias("list", "ls")
            result = cli_runner.invoke(app, ["ls"])
            assert result.exit_code == 0

            app.remove_alias("ls")
            result = cli_runner.invoke(app, ["ls"])
            assert result.exit_code != 0


# =============================================================================
# Mixed Usage Tests
# =============================================================================


class TestMixingDecoratorAndProgrammatic:
    """Tests for mixing decorator and programmatic approaches."""

    def test_both_approaches_coexist(self, cli_runner):
        """Test that both approaches work together."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            print("Listing...")

        def delete_item():
            print("Deleting...")

        app.add_command(delete_item, "delete", aliases=["rm"])

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["delete"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["rm"])
        assert result.exit_code == 0

    def test_add_alias_to_decorated_command(self, cli_runner, clean_output):
        """Test adding alias to command registered with decorator."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            print("Listing...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        app.add_alias("list", "l")

        for cmd in ["list", "ls", "l"]:
            result = cli_runner.invoke(app, [cmd])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Listing..." in clean_result

    def test_add_alias_to_programmatic_command(self):
        """Test adding alias to programmatically registered command."""
        app = ExtendedTyper()

        def list_items():
            pass

        def delete_item():
            pass

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm"])
        app.add_alias("list", "l")

        aliases = app.get_aliases("list")
        assert aliases == ["ls", "l"]

    def test_remove_alias_from_decorated_command(self):
        """Test removing alias from decorated command."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            pass

        result = app.remove_alias("ls")

        assert result is True
        assert app.get_aliases("list") == ["l"]

    def test_query_mixed_commands(self):
        """Test querying aliases from mixed registration methods."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        def delete_item():
            pass

        app.add_command(delete_item, "delete", aliases=["rm"])

        list_aliases = app.get_aliases("list")
        delete_aliases = app.get_aliases("delete")

        assert list_aliases == ["ls"]
        assert delete_aliases == ["rm"]

        all_aliases = app.list_commands_with_aliases()
        assert all_aliases == {"list": ["ls"], "delete": ["rm"]}

    def test_query_after_mixed_operations(self):
        """Test querying after mix of decorator and programmatic."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        def delete_item():
            pass

        app.add_command(delete_item, "delete", aliases=["rm"])
        app.add_alias("list", "l")

        mapping = app.list_commands_with_aliases()
        assert mapping == {"list": ["ls", "l"], "delete": ["rm"]}


# =============================================================================
# Help Display Tests
# =============================================================================


class TestHelpWithProgrammaticAPI:
    """Tests for help display with programmatic API."""

    def test_help_shows_programmatic_commands(self, cli_runner, clean_output):
        """Test that help shows programmatically registered commands."""
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

        assert "list" in clean_result

    def test_command_help_after_add_alias(self, cli_runner, clean_output):
        """Test that command help works after adding alias."""
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

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "List all items" in clean_result

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "List all items" in clean_result


# =============================================================================
# Real-World Usage Patterns Tests
# =============================================================================


class TestRealWorldUsagePatterns:
    """Tests for real-world usage patterns."""

    def test_configuration_based_aliases(self, cli_runner):
        """Test adding aliases based on configuration."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            print("Listing...")

        @app.command("delete")
        def delete_items():
            print("Deleting items...")

        config_aliases = {"list": ["ls", "l", "dir"]}

        for cmd, aliases in config_aliases.items():
            for alias in aliases:
                app.add_alias(cmd, alias)

        for alias in ["ls", "l", "dir"]:
            result = cli_runner.invoke(app, [alias])
            assert result.exit_code == 0

    def test_user_customisation_workflow(self, cli_runner):
        """Test workflow where user customises aliases."""
        app = ExtendedTyper()

        @app.command("checkout", aliases=["co"])
        def checkout(branch: str):
            print(f"Checked out {branch}")

        @app.command("merge", aliases=["m"])
        def merge(branch: str):
            print(f"Merged {branch} into current branch.")

        app.add_alias("checkout", "c")
        app.remove_alias("co")

        result = cli_runner.invoke(app, ["c", "main"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["co", "main"])
        assert result.exit_code != 0

    def test_backwards_compatibility_aliases(self, cli_runner, clean_output):
        """Test maintaining backwards compatibility with old command names."""
        app = ExtendedTyper()

        @app.command("add")
        def add_item(name: str):
            print(f"Added {name}")

        @app.command("remove")
        def remove_item(name: str):
            print(f"Removed {name}")

        app.add_alias("remove", "delete")
        app.add_alias("remove", "del")

        for cmd in ["remove", "delete", "del"]:
            result = cli_runner.invoke(app, [cmd, "test"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Removed test" in clean_result
