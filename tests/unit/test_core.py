"""Unit tests for ExtendedTyper core functionality"""

from unittest.mock import MagicMock, patch

import pytest
import typer
from typer.core import TyperCommand, TyperGroup

from typer_extensions import ExtendedTyper
from typer_extensions._compat import Command
from typer_extensions.core import (
    Context,
    ExtendedGroup,
    _extended_get_group_from_info,
)


def list_items():
    """List items."""


def delete_items():
    """Delete items."""


def group_from_info(app, group):
    """Run _extended_get_group_from_info with Typer's result stubbed to group"""
    with patch(
        "typer_extensions.core._original_get_group_from_info",
        return_value=group,
    ):
        return _extended_get_group_from_info(MagicMock(typer_instance=app))


class TestExtendedTyperinitialisation:
    """Tests for ExtendedTyper initialisation."""

    def test_default_initialisation(self) -> None:
        """Test that ExtendedTyper initialises with default config"""
        app = ExtendedTyper()
        assert app._alias_case_sensitive is True
        assert app.show_aliases_in_help is True
        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_custom_configuration(self) -> None:
        """Test that custom configuration is stored"""
        app = ExtendedTyper(
            alias_case_sensitive=False,
            show_aliases_in_help=False,
        )
        assert app._alias_case_sensitive is False
        assert app.show_aliases_in_help is False


class TestNameNormalisation:
    """Tests for name normalisation based on case sensitivity"""

    def test_normalise_case_sensitive(self) -> None:
        """Test name normalisation with case sensitivity"""
        app = ExtendedTyper(alias_case_sensitive=True)
        assert app._normalise_name("List") == "List"
        assert app._normalise_name("list") == "list"

    def test_normalise_case_insensitive(self) -> None:
        """Test name normalisation without case sensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        assert app._normalise_name("List") == "list"
        assert app._normalise_name("LIST") == "list"


class TestAliasRegistration:
    """Tests for alias registration logic"""

    def test_register_multiple_aliases_same_command(self) -> None:
        """Test registering multiple aliases for same command"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")
        app._register_alias("list", "l")

        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_register_duplicate_alias_raises(self) -> None:
        """Test that duplicate alias raises ValueError"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "ls")

    def test_alias_same_as_primary_raises(self) -> None:
        """Test that alias matching primary name raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="cannot be the same as command name"):
            app._register_alias("list", "list")

    def test_case_insensitive_alias_conflict(self) -> None:
        """Test alias conflict detection with case insensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "LS")  # Case-insensitive, should raise

    def test_case_sensitive_allows_different_case(self) -> None:
        """Test that case-sensitive mode allows different cases"""
        app = ExtendedTyper(alias_case_sensitive=True)
        app._register_alias("list", "ls")
        app._register_alias("delete", "LS")  # Case-sensitive, should work

        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["LS"] == "delete"


class TestAliasResolution:
    """Tests for alias resolution"""

    def test_resolve_existing_alias(self) -> None:
        """Test resolving an existing alias"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        assert app._resolve_alias("ls") == "list"

    def test_resolve_nonexistent_alias(self) -> None:
        """Test resolving a non-existent alias returns None"""
        app = ExtendedTyper()
        assert app._resolve_alias("nonexistent") is None

    def test_resolve_primary_name_returns_none(self) -> None:
        """Test that resolving primary name returns None"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        # Primary name is not an alias, should return None
        assert app._resolve_alias("list") is None

    def test_resolve_case_insensitive(self) -> None:
        """Test alias resolution with case insensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        assert app._resolve_alias("LS") == "list"
        assert app._resolve_alias("Ls") == "list"


class TestCommandWithAliases:
    """Tests for command registration with aliases"""

    def test_register_command_with_multiple_aliases(self) -> None:
        """Test registering command with multiple aliases"""
        app = ExtendedTyper()

        app.add_command(list_items, "list", aliases=["ls", "l", "dir"])

        assert app._command_aliases["list"] == ["ls", "l", "dir"]
        assert all(
            app._alias_to_command[alias] == "list" for alias in ["ls", "l", "dir"]
        )

    @pytest.mark.parametrize("aliases", [None, []])
    def test_register_command_without_aliases(self, aliases) -> None:
        """Test registering command without aliases"""
        app = ExtendedTyper()

        app.add_command(list_items, "list", aliases=aliases)

        assert app._command_aliases == {}
        assert app._alias_to_command == {}


class TestGetCommand:
    """Tests for _get_command with alias support"""

    def test__get_command_by_alias_in_multi_command_app(self) -> None:
        """Test getting command by alias in multi-command app"""
        app = ExtendedTyper()
        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_items, "delete", aliases=["del"])
        ctx = MagicMock()

        cmd_ls = app._get_command(ctx, "ls")
        cmd_list = app._get_command(ctx, "list")

        assert cmd_ls is not None
        assert cmd_list is not None
        assert cmd_ls.callback == cmd_list.callback

    def test__get_command_nonexistent_in_multi_command_app(self) -> None:
        """Test getting non-existent command returns None"""
        app = ExtendedTyper()
        app.command("list")(list_items)
        app.command("delete")(delete_items)

        assert app._get_command(MagicMock(), "nonexistent") is None

    def test__get_command_case_insensitive_alias(self) -> None:
        """Test getting command by case-insensitive alias"""
        app = ExtendedTyper(alias_case_sensitive=False)
        app.add_command(list_items, "list", aliases=["ls"])
        app.add_command(delete_items, "delete", aliases=["del"])

        assert app._get_command(MagicMock(), "LS") is not None

    def test__get_command_single_command_app(self) -> None:
        """Test getting command returns the default command"""
        app = ExtendedTyper()
        app.command("list")(list_items)
        ctx = MagicMock()

        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

        # Should not resolve an alias
        assert app._get_command(ctx, "ls") is None

    def test_get_command_with_no_group_or_command_initialised(self) -> None:
        """Test _get_command when the built app has no 'commands' attribute"""
        app = ExtendedTyper()
        app.command("list")(list_items)

        with patch("typer.main.get_command") as mock_get_cmd:
            del mock_get_cmd.return_value.commands

            assert app._get_command(MagicMock(), "unknown") is None


class TestExtendedGroup:
    """Tests for ExtendedGroup get_command"""

    def test__get_command_by_alias(self) -> None:
        """Test ExtendedGroup resolves a command by alias"""
        app = ExtendedTyper()
        app.add_command(list_items, "list", aliases=["ls"])
        group = ExtendedGroup()
        group._extended_typer = app
        ctx = Context(group)

        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        group.add_command(cmd, name="list")

        assert group.get_command(ctx, "ls") is not None

    def test__get_command_with_unknown_command(self) -> None:
        """Test ExtendedGroup returns None for unknown command/alias"""
        group = ExtendedGroup()
        group._extended_typer = ExtendedTyper()

        assert group.get_command(Context(group), "unknown") is None


class TestRegisterAliasValidation:
    """Tests for alias registration input validation"""

    @pytest.mark.parametrize(
        "alias", ["", None, 123, "l s", "l\ts", "l@s", "l$s", "x\n"]
    )
    def test_register_invalid_alias_raises(self, alias) -> None:
        """Test that an invalid alias raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Invalid alias"):
            app._register_alias("list", alias)

    @pytest.mark.parametrize("alias", ["list-all", "list_all", "liés"])
    def test_register_valid_alias(self, alias) -> None:
        """Test that dashes, underscores and unicode are valid in aliases"""
        app = ExtendedTyper()
        app._register_alias("list", alias)

        assert app._alias_to_command[alias] == "list"


class TestAddAliasToSingleCommandApp:
    """Tests for add_alias with single-command applications"""

    def test_add_alias_to_single_command_app_raises(self) -> None:
        """Test that adding alias to single-command app raises TypeError"""
        app = ExtendedTyper()
        app.command("main")(list_items)

        with pytest.raises(
            TypeError, match="Cannot add aliases to single-command applications"
        ):
            app.add_alias("main", "m")


class TestRemoveAliasEdgeCases:
    """Tests for edge cases in remove_alias"""

    def test_remove_alias_when_primary_command_has_no_aliases_dict(self) -> None:
        """Test remove_alias when primary command is not in _command_aliases dict"""
        app = ExtendedTyper()
        app.add_command(list_items, "list", aliases=["ls"])

        # Manually add an alias without registering the command
        app._alias_to_command["orphan"] = "delete"

        # Should return True, but not crash when primary isn't in _command_aliases
        assert app.remove_alias("orphan") is True


class TestExtendedGetGroupFromInfo:
    """Tests for _extended_get_group_from_info function and branch coverage"""

    def test_extended_group_preserves_rich_attributes(self) -> None:
        """Reclassing into ExtendedGroup preserves Typer's rich settings in place"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")
        real_group = TyperGroup(
            name="test",
            rich_markup_mode="markdown",
            rich_help_panel="Advanced",
        )

        result = group_from_info(app, real_group)

        # The group is re-classed in place, gaining alias resolution while
        # keeping all of Typer's configuration intact
        assert isinstance(result, ExtendedGroup)
        assert result is real_group
        assert result._extended_typer is app
        assert result.rich_markup_mode == "markdown"
        assert result.rich_help_panel == "Advanced"

    def test_extended_group_preserves_commands(self) -> None:
        """Reclassing into ExtendedGroup preserves the group's existing subcommands"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")
        commands: dict[str, Command] = {"list": TyperCommand("list")}
        real_group = TyperGroup(name="test", commands=commands, no_args_is_help=True)

        result = group_from_info(app, real_group)

        assert isinstance(result, ExtendedGroup)
        assert result is real_group
        assert result.commands == commands
        assert result.no_args_is_help is True

    def test_extended_group_no_aliases_registered(self) -> None:
        """Test that standard group is returned when no aliases are registered"""
        group = MagicMock(spec=TyperGroup)

        assert group_from_info(ExtendedTyper(), group) is group

    def test_standard_typer_returns_standard_group(self) -> None:
        """Test that non-ExtendedTyper instances return standard groups"""
        group = MagicMock(spec=TyperGroup)

        assert group_from_info(typer.Typer(), group) is group


class TestAddTyperWithAliases:
    """Tests for add_typer() with alias support"""

    def test_add_typer_with_explicit_name_and_aliases(self, make_app) -> None:
        """Aliases are registered when name and aliases are both provided"""
        app = ExtendedTyper()

        app.add_typer(make_app(), name="greet", aliases=["g", "gr"])

        assert app._alias_to_command["g"] == "greet"
        assert app._alias_to_command["gr"] == "greet"
        assert app._command_aliases["greet"] == ["g", "gr"]

    def test_add_typer_without_aliases_unchanged(self, make_app) -> None:
        """Calling add_typer without aliases does not touch alias dicts"""
        app = ExtendedTyper()

        app.add_typer(make_app(), name="greet")

        assert app._alias_to_command == {}
        assert app._command_aliases == {}

    def test_add_typer_infers_name_from_callback(self, make_app) -> None:
        """Name is inferred from the sub-typer's registered callback when not explicit"""
        app = ExtendedTyper()
        sub = make_app()

        @sub.callback()
        def my_sub_app():
            """Sub-app."""

        app.add_typer(sub, aliases=["ms"])

        # Typer converts my_sub_app → my-sub-app
        assert app._alias_to_command["ms"] == "my-sub-app"
        assert app._command_aliases["my-sub-app"] == ["ms"]

    def test_add_typer_raises_when_name_unresolvable(self, make_app) -> None:
        """ValueError is raised when no name can be inferred and none provided"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Cannot infer sub-app name"):
            app.add_typer(make_app(), aliases=["x"])

    def test_add_typer_alias_conflict_raises(self, make_app) -> None:
        """Duplicate alias across two sub-apps raises ValueError"""
        app = ExtendedTyper()
        app.add_typer(make_app(), name="greet", aliases=["g"])

        with pytest.raises(ValueError, match="already registered"):
            app.add_typer(make_app(), name="farewell", aliases=["g"])
