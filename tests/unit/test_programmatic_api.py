"""Unit tests for programmatic API methods."""

import pytest
import typer.main
from typer.core import TyperGroup

from typer_extensions import ExtendedTyper


def list_items():
    """List items."""


def delete_item():
    """Delete items."""


class TestAddAliasedCommand:
    """Tests for add_command() method."""

    def test_add_command(self) -> None:
        """Test adding command with aliases programmatically."""
        app = ExtendedTyper()

        app.add_command(list_items, "list", aliases=["ls", "l"])

        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_add_command_without_aliases(self) -> None:
        """Test adding command without aliases."""
        app = ExtendedTyper()

        app.add_command(list_items, "list", aliases=None)

        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_add_command_inferred_name(self) -> None:
        """Test adding command with inferred name."""
        app = ExtendedTyper()

        app.add_command(list_items, aliases=["ls"])

        # Name should be inferred from function
        assert app._alias_to_command["ls"] == "list_items"

    def test_add_command_with_kwargs(self) -> None:
        """Test that kwargs are passed through."""
        app = ExtendedTyper()

        app.add_command(
            list_items, "list", aliases=["ls"], help="Custom help", deprecated=True
        )
        app.add_command(delete_item, "delete")

        group = typer.main.get_command(app)
        assert isinstance(group, TyperGroup)
        registered_cmd = group.commands["list"]

        assert registered_cmd.deprecated is True
        assert registered_cmd.help == "Custom help"


class TestAddAlias:
    """Tests for add_alias() method."""

    def test_add_alias_to_decorated_command(self, make_app) -> None:
        """Test adding alias to command registered with decorator."""
        app = make_app()

        app.add_alias("list", "dir")

        assert app._command_aliases["list"] == ["ls", "l", "dir"]
        assert app._alias_to_command["dir"] == "list"

    def test_add_alias_nonexistent_command_raises(self, make_app) -> None:
        """Test that adding alias to non-existent command raises error."""
        with pytest.raises(ValueError, match="Command 'nonexistent' does not exist"):
            make_app().add_alias("nonexistent", "ne")


class TestRemoveAlias:
    """Tests for remove_alias() method."""

    def test_remove_nonexistent_alias_returns_false(self, make_app) -> None:
        """Test that removing non-existent alias returns False."""
        assert make_app().remove_alias("nonexistent") is False

    def test_remove_alias_leaves_others(self, make_app) -> None:
        """Test that removing one alias doesn't affect others."""
        app = make_app()

        assert app.remove_alias("l") is True

        assert app._command_aliases["list"] == ["ls"]
        assert app._alias_to_command["ls"] == "list"
        assert "l" not in app._alias_to_command

    def test_remove_last_alias(self, make_app) -> None:
        """Test removing the last alias for a command."""
        app = make_app()

        app.remove_alias("rm")

        # Command should be removed from _command_aliases when no aliases left
        assert "delete" not in app._command_aliases
        assert "rm" not in app._alias_to_command

    @pytest.mark.parametrize(
        ("registered", "removed"),
        [("ls", "ls"), ("ls", "LS"), ("LS", "ls"), ("Ls", "lS")],
    )
    def test_remove_alias_case_insensitive(self, registered, removed) -> None:
        """Test removal matches any case, however the alias was registered."""
        app = ExtendedTyper(alias_case_sensitive=False)
        app.command("list", aliases=[registered, "keep"])(list_items)
        app.command("delete")(delete_item)

        assert app.remove_alias(removed) is True

        assert app.get_aliases("list") == ["keep"]

        # A stale entry would leave the alias listed twice once re-added
        app.add_alias("list", registered)
        assert app.get_aliases("list") == ["keep", registered]

    def test_remove_same_alias_twice(self, make_app) -> None:
        """Test idempotency of remove_alias."""
        app = make_app()

        assert app.remove_alias("ls") is True
        assert app.remove_alias("ls") is False


class TestGetAliases:
    """Tests for get_aliases() method."""

    def test_get_aliases_existing_command(self, make_app) -> None:
        """Test getting aliases for command with aliases."""
        assert make_app().get_aliases("list") == ["ls", "l"]

    def test_get_aliases_no_aliases_returns_empty(self, make_app) -> None:
        """Test that command without aliases returns empty list."""
        assert make_app(aliases=False).get_aliases("list") == []

    def test_get_aliases_nonexistent_command_returns_empty(self) -> None:
        """Test that non-existent command returns empty list."""
        assert ExtendedTyper().get_aliases("nonexistent") == []

    def test_get_aliases_returns_copy(self, make_app) -> None:
        """Test that get_aliases returns a copy, not reference."""
        app = make_app()

        app.get_aliases("list").append("modified")

        assert app.get_aliases("list") == ["ls", "l"]


class TestListCommandsWithAliases:
    """Tests for list_commands_with_aliases() method."""

    def test_list_all_commands_with_aliases(self, make_app) -> None:
        """Test listing all commands that have aliases."""
        mapping = make_app().list_commands_with_aliases()

        assert mapping == {"list": ["ls", "l"], "delete": ["rm"]}

    def test_list_empty_when_no_aliases(self, make_app) -> None:
        """Test that list is empty when no commands have aliases."""
        assert make_app(aliases=False).list_commands_with_aliases() == {}

    def test_list_returns_copy(self, make_app) -> None:
        """Test that list returns a copy of the data."""
        app = make_app()

        mapping = app.list_commands_with_aliases()
        mapping["list"].append("modified")
        mapping["new"] = ["test"]

        # Original should be unchanged
        expected = {"list": ["ls", "l"], "delete": ["rm"]}
        assert app.list_commands_with_aliases() == expected

    def test_list_after_dynamic_changes(self, make_app) -> None:
        """Test listing after dynamically adding/removing aliases."""
        app = make_app()

        app.add_alias("list", "dir")
        assert app.list_commands_with_aliases() == {
            "list": ["ls", "l", "dir"],
            "delete": ["rm"],
        }

        app.remove_alias("rm")
        assert app.list_commands_with_aliases() == {"list": ["ls", "l", "dir"]}
