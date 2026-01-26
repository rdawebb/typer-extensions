"""Unit tests for programmatic API methods."""

import pytest
from typer_extensions import ExtendedTyper


class TestAddAliasedCommand:
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

        # Name should be inferred from function
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

        cmd = app.add_command(
            list_items, "list", aliases=["ls"], help="Custom help", deprecated=True
        )

        assert cmd is not None
        assert cmd.deprecated is True

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

        # Add alias after registration
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

        # Add another alias
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

        # Should detect conflict even with different case
        with pytest.raises(ValueError, match="already registered"):
            app.add_alias("delete", "LS")


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

        # Command should be removed from _command_aliases when no aliases left
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

        # Should remove regardless of case
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

        # Original should be unchanged
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

        # Original should be unchanged
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

        # Add alias to list
        app.add_alias("list", "ls")

        mapping = app.list_commands_with_aliases()
        assert mapping == {"list": ["ls"], "delete": ["rm"]}

        # Remove alias from delete
        app.remove_alias("rm")

        mapping = app.list_commands_with_aliases()
        assert mapping == {"list": ["ls"]}


class TestProgrammaticAPIMixedUsage:
    """Tests for mixing programmatic API with decorators."""

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
