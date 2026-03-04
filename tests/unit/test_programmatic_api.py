"""Comprehensive tests for programmatic API methods.

This module tests both the programmatic registration of commands (add_command) and dynamic alias management (add_alias, remove_alias, get_aliases, etc.) along with usage patterns and integration scenarios.
"""

import pytest


# =============================================================================
# Command Registration Tests
# =============================================================================


class TestAddCommand:
    """Tests for add_command() method."""

    def test_add_command(self, app, unreg_commands):
        """Test adding command with aliases programmatically."""

        list_items, _ = unreg_commands

        app.add_command(list_items, "list", aliases=["ls", "l"])

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_add_command_without_aliases(self, app, unreg_commands):
        """Test adding command without aliases."""

        list_items, _ = unreg_commands

        app.add_command(list_items, "list", aliases=None)

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_add_command_inferred_name(self, app, unreg_commands):
        """Test adding command with inferred name."""

        list_items, _ = unreg_commands

        app.add_command(list_items, aliases=["ls"])

        assert "list_items" in app._command_aliases
        assert app._alias_to_command["ls"] == "list_items"

    def test_add_command_with_kwargs(self, app, unreg_commands):
        """Test that kwargs are passed through."""

        list_items, delete_item = unreg_commands

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

    def test_add_multiple_commands(self, app, unreg_commands):
        """Test adding multiple commands programmatically."""

        list_items, delete_item = unreg_commands

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm"])

        assert len(app._command_aliases) == 2
        assert len(app._alias_to_command) == 2


class TestProgrammaticCommandInvocation:
    """Tests for invoking programmatically registered commands."""

    def test_invoke_programmatic_command(
        self, app, clean_output, cli_runner, unreg_commands
    ):
        """Test invoking command registered programmatically."""

        list_items, delete_item = unreg_commands

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


# =============================================================================
# Dynamic Alias Management Tests
# =============================================================================


class TestAddAlias:
    """Tests for add_alias() method."""

    def test_add_alias_to_existing_command(self, app_with_commands):
        """Test adding alias to command registered with standard decorator."""

        app_with_commands.add_alias("list", "ls")

        assert "list" in app_with_commands._command_aliases
        assert "ls" in app_with_commands._command_aliases["list"]
        assert app_with_commands._alias_to_command["ls"] == "list"

    def test_add_alias_to_decorated_command(self, app_with_aliases):
        """Test adding alias to command registered with decorator."""

        app_with_aliases.add_alias("list", "lst")

        assert app_with_aliases._command_aliases["list"] == ["ls", "l", "lst"]
        assert app_with_aliases._alias_to_command["lst"] == "list"

    def test_add_multiple_aliases(self, app_with_commands):
        """Test adding multiple aliases one at a time."""

        app_with_commands.add_alias("list", "ls")
        app_with_commands.add_alias("list", "l")
        app_with_commands.add_alias("list", "dir")

        assert app_with_commands._command_aliases["list"] == ["ls", "l", "dir"]
        assert all(
            app_with_commands._alias_to_command[a] == "list" for a in ["ls", "l", "dir"]
        )

    def test_add_alias_nonexistent_command_raises(self, app_with_commands):
        """Test that adding alias to non-existent command raises error."""

        with pytest.raises(ValueError, match="Command 'nonexistent' does not exist"):
            app_with_commands.add_alias("nonexistent", "ne")

    def test_add_duplicate_alias_raises(self, app_with_commands):
        """Test that adding duplicate alias raises error."""

        app_with_commands.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app_with_commands.add_alias("delete", "ls")

    def test_add_alias_case_insensitive(self, app_case_insensitive):
        """Test adding alias with case insensitivity."""

        @app_case_insensitive.command("list")
        def list_items():
            pass

        @app_case_insensitive.command("delete")
        def delete_items():
            pass

        app_case_insensitive.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app_case_insensitive.add_alias("delete", "LS")

    def test_invoke_after_add_alias(self, app_with_commands, clean_output, cli_runner):
        """Test that newly added alias works for invocation."""

        result = cli_runner.invoke(app_with_commands, ["list"])
        assert result.exit_code == 0

        app_with_commands.add_alias("list", "ls")

        result = cli_runner.invoke(app_with_commands, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result


class TestRemoveAlias:
    """Tests for remove_alias() method."""

    def test_remove_existing_alias(self, app_with_aliases):
        """Test removing an existing alias."""

        result = app_with_aliases.remove_alias("ls")

        assert result is True
        assert "ls" not in app_with_aliases._alias_to_command
        assert app_with_aliases._command_aliases["list"] == ["l"]

    def test_remove_nonexistent_alias_returns_false(self, app_with_commands):
        """Test that removing non-existent alias returns False."""

        result = app_with_commands.remove_alias("nonexistent")

        assert result is False

    def test_remove_alias_leaves_others(self, app_with_aliases):
        """Test that removing one alias doesn't affect others."""

        app_with_aliases.remove_alias("l")

        assert app_with_aliases._command_aliases["list"] == ["ls"]
        assert app_with_aliases._alias_to_command["ls"] == "list"
        assert "l" not in app_with_aliases._alias_to_command

    def test_remove_last_alias(self, app_with_aliases):
        """Test removing the last alias for a command."""

        app_with_aliases.remove_alias("ls")
        app_with_aliases.remove_alias("l")

        assert "list" not in app_with_aliases._command_aliases
        assert "ls" not in app_with_aliases._alias_to_command
        assert "l" not in app_with_aliases._alias_to_command

    def test_remove_alias_case_insensitive(self, app_case_insensitive):
        """Test removing alias with case insensitivity."""

        @app_case_insensitive.command("list", aliases=["ls"])
        def list_items():
            pass

        @app_case_insensitive.command("delete", aliases=["rm"])
        def delete_item():
            pass

        result = app_case_insensitive.remove_alias("LS")

        assert result is True
        assert "ls" not in app_case_insensitive._alias_to_command

    def test_remove_same_alias_twice(self, app_with_aliases):
        """Test idempotency of remove_alias."""

        result1 = app_with_aliases.remove_alias("ls")
        result2 = app_with_aliases.remove_alias("ls")

        assert result1 is True
        assert result2 is False

    def test_invoke_fails_after_remove_alias(self, app_with_aliases, cli_runner):
        """Test that removed alias no longer works."""

        result = cli_runner.invoke(app_with_aliases, ["ls"])
        assert result.exit_code == 0

        app_with_aliases.remove_alias("ls")

        result = cli_runner.invoke(app_with_aliases, ["ls"])
        assert result.exit_code != 0

        result = cli_runner.invoke(app_with_aliases, ["l"])
        assert result.exit_code == 0


class TestGetAliases:
    """Tests for get_aliases() method."""

    def test_get_aliases_existing_command(self, app_with_aliases):
        """Test getting aliases for command with aliases."""

        aliases = app_with_aliases.get_aliases("list")

        assert aliases == ["ls", "l"]

    def test_get_aliases_no_aliases_returns_empty(self, app_with_commands):
        """Test that command without aliases returns empty list."""

        aliases = app_with_commands.get_aliases("list")

        assert aliases == []

    def test_get_aliases_nonexistent_command_returns_empty(self, app):
        """Test that non-existent command returns empty list."""

        aliases = app.get_aliases("nonexistent")

        assert aliases == []

    def test_get_aliases_returns_copy(self, app_with_aliases):
        """Test that get_aliases returns a copy, not reference."""

        aliases = app_with_aliases.get_aliases("list")
        aliases.append("modified")

        original_aliases = app_with_aliases.get_aliases("list")
        assert original_aliases == ["ls", "l"]
        assert "modified" not in original_aliases

    def test_get_aliases_after_add(self, app_with_commands):
        """Test getting aliases after dynamically adding one."""

        app_with_commands.add_alias("list", "ls")
        app_with_commands.add_alias("list", "l")

        aliases = app_with_commands.get_aliases("list")
        assert aliases == ["ls", "l"]

    def test_get_aliases_after_remove(self, app_with_aliases):
        """Test getting aliases after removing one."""

        app_with_aliases.remove_alias("l")

        aliases = app_with_aliases.get_aliases("list")
        assert aliases == ["ls"]


class TestListCommandsWithAliases:
    """Tests for list_commands_with_aliases() method."""

    def test_list_all_commands_with_aliases(self, app_with_aliases):
        """Test listing all commands that have aliases."""

        mapping = app_with_aliases.list_commands_with_aliases()

        assert mapping == {"list": ["ls", "l"], "delete": ["rm"]}

    def test_list_empty_when_no_aliases(self, app_with_commands):
        """Test that list is empty when no commands have aliases."""

        mapping = app_with_commands.list_commands_with_aliases()

        assert mapping == {}

    def test_list_returns_copy(self, app_with_aliases):
        """Test that list returns a copy of the data."""

        mapping = app_with_aliases.list_commands_with_aliases()
        mapping["list"].append("modified")
        mapping["new"] = ["test"]

        original_mapping = app_with_aliases.list_commands_with_aliases()
        assert original_mapping == {"list": ["ls", "l"], "delete": ["rm"]}

    def test_list_excludes_commands_without_aliases(self, app):
        """Test that commands without aliases are excluded."""

        @app.command("list", aliases=["ls"])
        def list_items():
            pass

        @app.command("hello")
        def say_hello():
            pass

        mapping = app.list_commands_with_aliases()

        assert "list" in mapping
        assert "hello" not in mapping

    def test_list_after_dynamic_changes(self, app):
        """Test listing after dynamically adding/removing aliases."""

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

    def test_dynamic_alias_workflow(self, app_with_commands, cli_runner):
        """Test a complete workflow of dynamic alias management."""

        result = cli_runner.invoke(app_with_commands, ["ls"])
        assert result.exit_code != 0

        app_with_commands.add_alias("list", "ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        assert result.exit_code == 0

        app_with_commands.add_alias("list", "l")
        result = cli_runner.invoke(app_with_commands, ["l"])
        assert result.exit_code == 0

        app_with_commands.remove_alias("ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        assert result.exit_code != 0

        result = cli_runner.invoke(app_with_commands, ["l"])
        assert result.exit_code == 0

    def test_plugin_system_simulation(
        self, app_with_commands, clean_output, cli_runner
    ):
        """Test simulating a plugin system with dynamic commands."""

        def plugin_command():
            print("Plugin command executed")

        app_with_commands.add_command(
            plugin_command, "plugin-cmd", aliases=["pc", "plugin"]
        )

        result = cli_runner.invoke(app_with_commands, ["plugin-cmd"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Plugin command" in clean_result

        result = cli_runner.invoke(app_with_commands, ["pc"])
        assert result.exit_code == 0

        app_with_commands.remove_alias("pc")
        app_with_commands.remove_alias("plugin")

        result = cli_runner.invoke(app_with_commands, ["pc"])
        assert result.exit_code != 0


class TestAliasReregistration:
    """Tests for re-adding aliases that have been removed."""

    def test_re_add_removed_alias(self, app_with_commands, clean_output, cli_runner):
        """Test that a removed alias can be re-added and work again."""

        app_with_commands.add_alias("list", "ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

        app_with_commands.remove_alias("ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        assert result.exit_code != 0

        app_with_commands.add_alias("list", "ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

    def test_re_add_removed_alias_to_different_command(
        self, app_with_commands, clean_output, cli_runner
    ):
        """Test that a removed alias can be added to a different command."""

        app_with_commands.add_alias("list", "ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items..." in clean_result

        app_with_commands.remove_alias("ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        assert result.exit_code != 0

        app_with_commands.add_alias("delete", "ls")
        result = cli_runner.invoke(app_with_commands, ["ls"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Deleting item..." in clean_result

    def test_cannot_add_active_alias(self, app_with_commands):
        """Test that adding an alias that's currently active raises error."""

        app_with_commands.add_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app_with_commands.add_alias("delete", "ls")

    def test_re_add_multiple_times(self, app_with_commands, cli_runner):
        """Test that an alias can be removed and re-added multiple times."""

        for _ in range(3):
            app_with_commands.add_alias("list", "ls")
            result = cli_runner.invoke(app_with_commands, ["ls"])
            assert result.exit_code == 0

            app_with_commands.remove_alias("ls")
            result = cli_runner.invoke(app_with_commands, ["ls"])
            assert result.exit_code != 0


# =============================================================================
# Mixed Usage Tests
# =============================================================================


class TestMixingDecoratorAndProgrammatic:
    """Tests for mixing decorator and programmatic approaches."""

    def test_both_approaches_coexist(self, app, cli_runner):
        """Test that both approaches work together."""

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

    def test_add_alias_to_decorated_command(
        self, app_with_aliases, clean_output, cli_runner
    ):
        """Test adding alias to command registered with decorator."""

        app_with_aliases.add_alias("list", "lst")

        for cmd in ["list", "ls", "l", "lst"]:
            result = cli_runner.invoke(app_with_aliases, [cmd])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Listing items..." in clean_result

    def test_add_alias_to_programmatic_command(self, app, unreg_commands):
        """Test adding alias to programmatically registered command."""

        list_items, delete_item = unreg_commands

        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_item, "delete", aliases=["rm"])
        app.add_alias("list", "l")

        aliases = app.get_aliases("list")
        assert aliases == ["ls", "l"]

    def test_remove_alias_from_decorated_command(self, app_with_aliases):
        """Test removing alias from decorated command."""

        result = app_with_aliases.remove_alias("ls")

        assert result is True
        assert app_with_aliases.get_aliases("list") == ["l"]

    def test_query_mixed_commands(self, app):
        """Test querying aliases from mixed registration methods."""

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

    def test_query_after_mixed_operations(self, app):
        """Test querying after mix of decorator and programmatic."""

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

    def test_help_shows_programmatic_commands(
        self, app, clean_output, cli_runner, unreg_commands
    ):
        """Test that help shows programmatically registered commands."""

        list_items, _ = unreg_commands

        app.add_command(
            list_items, "list", aliases=["ls"], help="List items in the system"
        )

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "list" in clean_result

    def test_command_help_after_add_alias(
        self, app_with_commands, clean_output, cli_runner
    ):
        """Test that command help works after adding alias."""

        app_with_commands.add_alias("list", "ls")

        result = cli_runner.invoke(app_with_commands, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "List all items" in clean_result

        result = cli_runner.invoke(app_with_commands, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "List all items" in clean_result


# =============================================================================
# Real-World Usage Patterns Tests
# =============================================================================


class TestRealWorldUsagePatterns:
    """Tests for real-world usage patterns."""

    def test_configuration_based_aliases(self, app_with_commands, cli_runner):
        """Test adding aliases based on configuration."""

        config_aliases = {"list": ["ls", "l", "dir"]}

        for cmd, aliases in config_aliases.items():
            for alias in aliases:
                app_with_commands.add_alias(cmd, alias)

        for alias in ["ls", "l", "dir"]:
            result = cli_runner.invoke(app_with_commands, [alias])
            assert result.exit_code == 0

    def test_user_customisation_workflow(self, app_with_aliases, cli_runner):
        """Test workflow where user customises aliases."""

        app_with_aliases.add_alias("list", "lst")
        app_with_aliases.remove_alias("ls")

        result = cli_runner.invoke(app_with_aliases, ["lst"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app_with_aliases, ["ls"])
        assert result.exit_code != 0

    def test_backwards_compatibility_aliases(
        self, app_with_commands, clean_output, cli_runner
    ):
        """Test maintaining backwards compatibility with old command names."""

        app_with_commands.add_alias("delete", "remove")
        app_with_commands.add_alias("delete", "del")

        for cmd in ["delete", "remove", "del"]:
            result = cli_runner.invoke(app_with_commands, [cmd])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Deleting item..." in clean_result
