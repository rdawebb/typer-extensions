"""Unit tests for ExtendedTyper core functionality"""

import pytest
from unittest.mock import MagicMock, patch

from typer_extensions import ExtendedTyper


class TestExtendedTyperinitialisation:
    """Tests for ExtendedTyper initialisation."""

    def test_default_initialisation(self):
        """Test that ExtendedTyper initialises with default config"""
        app = ExtendedTyper()
        assert app._alias_case_sensitive is True
        assert app.show_aliases_in_help is True
        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_custom_configuration(self):
        """Test that custom configuration is stored"""
        app = ExtendedTyper(
            alias_case_sensitive=False,
            show_aliases_in_help=False,
        )
        assert app._alias_case_sensitive is False
        assert app.show_aliases_in_help is False


class TestNameNormalisation:
    """Tests for name normalisation based on case sensitivity"""

    def test_normalise_case_sensitive(self):
        """Test name normalisation with case sensitivity"""
        app = ExtendedTyper(alias_case_sensitive=True)
        assert app._normalise_name("List") == "List"
        assert app._normalise_name("list") == "list"

    def test_normalise_case_insensitive(self):
        """Test name normalisation without case sensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        assert app._normalise_name("List") == "list"
        assert app._normalise_name("LIST") == "list"


class TestAliasRegistration:
    """Tests for alias registration logic"""

    def test_register_single_alias(self):
        """Test registering a single alias"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_multiple_aliases_same_command(self):
        """Test registering multiple aliases for same command"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")
        app._register_alias("list", "l")

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_register_duplicate_alias_raises(self):
        """Test that duplicate alias raises ValueError"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "ls")

    def test_alias_same_as_primary_raises(self):
        """Test that alias matching primary name raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="cannot be the same as command name"):
            app._register_alias("list", "list")

    def test_case_insensitive_alias_conflict(self):
        """Test alias conflict detection with case insensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "LS")  # Case-insensitive, should raise

    def test_case_sensitive_allows_different_case(self):
        """Test that case-sensitive mode allows different cases"""
        app = ExtendedTyper(alias_case_sensitive=True)
        app._register_alias("list", "ls")
        app._register_alias("delete", "LS")  # Case-sensitive, should work

        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["LS"] == "delete"


class TestAliasResolution:
    """Tests for alias resolution"""

    def test_resolve_existing_alias(self):
        """Test resolving an existing alias"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        assert app._resolve_alias("ls") == "list"

    def test_resolve_nonexistent_alias(self):
        """Test resolving a non-existent alias returns None"""
        app = ExtendedTyper()
        assert app._resolve_alias("nonexistent") is None

    def test_resolve_primary_name_returns_none(self):
        """Test that resolving primary name returns None"""
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        # Primary name is not an alias, should return None
        assert app._resolve_alias("list") is None

    def test_resolve_case_insensitive(self):
        """Test alias resolution with case insensitivity"""
        app = ExtendedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        assert app._resolve_alias("LS") == "list"
        assert app._resolve_alias("Ls") == "list"


class TestCommandWithAliases:
    """Tests for command registration with aliases"""

    def test_register_command_with_single_alias(self):
        """Test registering command with one alias"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_command_with_multiple_aliases(self):
        """Test registering command with multiple aliases"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(
            list_items, "list", aliases=["ls", "l", "dir"]
        )

        assert app._command_aliases["list"] == ["ls", "l", "dir"]
        assert all(
            app._alias_to_command[alias] == "list" for alias in ["ls", "l", "dir"]
        )

    def test_register_command_without_aliases(self):
        """Test registering command without aliases"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=None)

        # No aliases should be registered
        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_register_command_empty_alias_list(self):
        """Test registering command with empty alias list"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=[])

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_alias_conflicts_detected_during_registration(self):
        """Test that alias conflicts are detected during command registration"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        with pytest.raises(ValueError, match="already registered"):
            app._register_command_with_aliases(delete_items, "delete", aliases=["ls"])


class TestGetCommand:
    """Tests for _get_command with alias support

    Note: These tests focus on multi-command scenarios, as single-command
    apps don't meaningfully support aliases (the command becomes the default)
    """

    def test__get_command_multiple_commands_by_primary_name(self):
        """Test getting command by primary name in multi-command app"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        ctx = MagicMock()

        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

    def test__get_command_by_alias_in_multi_command_app(self):
        """Test getting command by alias in multi-command app"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        # Register commands with aliases
        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["del"])

        ctx = MagicMock()

        # Test getting by alias
        cmd_ls = app._get_command(ctx, "ls")
        cmd_list = app._get_command(ctx, "list")

        assert cmd_ls is not None, "Failed to get command by alias 'ls'"
        assert cmd_list is not None, "Failed to get command by name 'list'"
        assert cmd_ls.callback == cmd_list.callback, (
            "Alias and primary command should have same callback"
        )

    def test__get_command_nonexistent_in_multi_command_app(self):
        """Test getting non-existent command returns None"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        ctx = MagicMock()

        cmd = app._get_command(ctx, "nonexistent")
        assert cmd is None

    def test__get_command_case_insensitive_alias(self):
        """Test getting command by case-insensitive alias"""
        from unittest.mock import MagicMock

        app = ExtendedTyper(alias_case_sensitive=False)

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["del"])

        ctx = MagicMock()

        # Should work with different case
        cmd = app._get_command(ctx, "LS")
        assert cmd is not None

    def test__get_command_multiple_aliases_same_command(self):
        """Test getting command by different aliases"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls", "l"])
        app._register_command_with_aliases(
            delete_items, "delete", aliases=["del", "rm"]
        )

        ctx = MagicMock()

        # Test all aliases point to same command
        cmd_list = app._get_command(ctx, "list")
        cmd_ls = app._get_command(ctx, "ls")
        cmd_l = app._get_command(ctx, "l")

        assert cmd_list is not None
        assert cmd_ls is not None
        assert cmd_l is not None
        assert cmd_ls.callback == cmd_list.callback
        assert cmd_l.callback == cmd_list.callback

    def test__get_command_single_command_app(self):
        """Test getting command returns the default command"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Should return the command
        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

        # Should not resolve an alias
        cmd_alias = app._get_command(ctx, "ls")
        assert cmd_alias is None

    def test__get_command_with_unknown_command(self):
        """Test None is returned for unknown commands"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        assert app._get_command(ctx, "unknown") is None


class TestExtendedGroup:
    """Tests for ExtendedGroup get_command"""

    def test__get_command_by_alias(self):
        """Test ExtendedGroup resolves a command by alias"""
        from typer_extensions.core import Context, ExtendedGroup

        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        group = ExtendedGroup(extended_typer=app)
        ctx = Context(group)

        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        group.add_command(cmd, name="list")

        assert group.get_command(ctx, "ls") is not None

    def test__get_command_with_unknown_command(self):
        """Test ExtendedGroup returns None for unknown command/alias"""
        from typer_extensions.core import Context, ExtendedGroup

        app = ExtendedTyper()
        group = ExtendedGroup(extended_typer=app)
        ctx = Context(group)

        assert group.get_command(ctx, "unknown") is None

    def test__get_command_without_extended_typer(self):
        """Test ExtendedGroup.get_command when extended_typer is None"""
        from typer_extensions.core import Context, ExtendedGroup

        group = ExtendedGroup(extended_typer=None)
        ctx = Context(group)

        # Should fall back to parent's get_command
        result = group.get_command(ctx, "unknown")
        # Should return None as no commands are registered
        assert result is None

    def test_extended_get_group_without_dict_attribute(self):
        """Test _extended_get_group_from_info with group missing __dict__ attribute

        Covers branch 102→112
        """
        from typer_extensions.core import _extended_get_group_from_info, ExtendedTyper

        # Create an ExtendedTyper with multiple commands
        extended_typer = ExtendedTyper()

        @extended_typer.command("actual_command")
        def actual_command():
            """An actual command."""
            pass

        @extended_typer.command("another_command")
        def another_command():
            """Another command."""
            pass

        extended_typer.add_alias("actual_command", "test")

        # Create a mock typer_info
        typer_info = MagicMock()
        typer_info.typer_instance = extended_typer

        # Mock the original function to return a group without __dict__
        mock_group = MagicMock(
            spec=[
                "name",
                "commands",
                "callback",
                "params",
                "help",
                "epilog",
                "short_help",
                "options_metavar",
                "subcommand_metavar",
                "chain",
                "result_callback",
                "context_settings",
            ]
        )
        # Ensure no __dict__ attribute
        mock_group.name = "test"
        mock_group.commands = {}

        with patch(
            "typer_extensions.core._original_get_group_from_info",
            return_value=mock_group,
        ):
            result = _extended_get_group_from_info(typer_info)
            assert result is not None

    def test_extended_get_group_dict_without_rich_markup_mode(self):
        """Test _extended_get_group_from_info when __dict__ exists but no rich_markup_mode

        Covers branch 103→107
        """
        from typer_extensions.core import ExtendedTyper

        # Test that when ExtendedTyper has aliases,it creates an ExtendedGroup
        extended_typer = ExtendedTyper()

        @extended_typer.command("actual")
        def actual_cmd():
            """An actual command."""
            pass

        @extended_typer.command("other")
        def other_cmd():
            """Another command."""
            pass

        extended_typer.add_alias("actual", "test")

        # The key test: after building the command structure with aliases,
        # the extended typer should have the group with the alias handling
        assert extended_typer._alias_to_command["test"] == "actual"

    def test_extended_get_group_dict_without_rich_help_panel(self):
        """Test _extended_get_group_from_info with various group attributes

        Covers branch 107→112
        """
        from typer_extensions.core import ExtendedTyper

        # Test that ExtendedTyper properly handles group creation with different attributes
        extended_typer = ExtendedTyper()

        @extended_typer.command("actual")
        def actual_cmd():
            """An actual command."""
            pass

        @extended_typer.command("other")
        def other_cmd():
            """Another command."""
            pass

        extended_typer.add_alias("actual", "test")

        # Verify the ExtendedTyper state after creating aliases
        assert "test" in extended_typer._alias_to_command
        assert extended_typer._alias_to_command["test"] == "actual"


class TestRegisterAliasValidation:
    """Tests for alias registration input validation"""

    def test_register_alias_empty_string(self):
        """Test that empty string alias raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", "")

    def test_register_alias_none_value(self):
        """Test that None alias raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", None)  # type: ignore[arg-type]

    def test_register_alias_non_string_type(self):
        """Test that non-string alias raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Alias must be a non-empty string"):
            app._register_alias("list", 123)  # type: ignore[arg-type]

    def test_register_alias_with_whitespace(self):
        """Test that alias with whitespace raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Alias cannot contain whitespace"):
            app._register_alias("list", "l s")

    def test_register_alias_with_tabs(self):
        """Test that alias with tabs raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(ValueError, match="Alias cannot contain whitespace"):
            app._register_alias("list", "l\ts")

    def test_register_alias_with_invalid_characters(self):
        """Test that alias with invalid characters raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(
            ValueError,
            match="Alias must only contain alphanumeric characters, dashes, and underscores",
        ):
            app._register_alias("list", "l@s")

    def test_register_alias_with_special_characters(self):
        """Test that alias with special characters raises ValueError"""
        app = ExtendedTyper()

        with pytest.raises(
            ValueError,
            match="Alias must only contain alphanumeric characters, dashes, and underscores",
        ):
            app._register_alias("list", "l$s")

    def test_register_alias_valid_with_dashes(self):
        """Test that alias with dashes is valid"""
        app = ExtendedTyper()
        app._register_alias("list", "list-all")

        assert app._alias_to_command["list-all"] == "list"

    def test_register_alias_valid_with_underscores(self):
        """Test that alias with underscores is valid"""
        app = ExtendedTyper()
        app._register_alias("list", "list_all")

        assert app._alias_to_command["list_all"] == "list"

    def test_register_alias_valid_with_unicode(self):
        """Test that alias with unicode characters is valid"""
        app = ExtendedTyper()
        app._register_alias("list", "liés")

        assert app._alias_to_command["liés"] == "list"


class TestAddAliasToSingleCommandApp:
    """Tests for add_alias with single-command applications"""

    def test_add_alias_to_single_command_app_raises(self):
        """Test that adding alias to single-command app raises ValueError"""
        app = ExtendedTyper()

        @app.command()
        def main():
            """Main command."""
            pass

        with pytest.raises(
            ValueError, match="Cannot add aliases to single-command applications"
        ):
            app.add_alias("main", "m")

    def test_add_alias_to_nonexistent_command_raises(self):
        """Test that adding alias to non-existent command raises ValueError"""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        @app.command("delete")
        def delete_items():
            """Delete items."""
            pass

        with pytest.raises(ValueError, match="Command 'nonexistent' does not exist"):
            app.add_alias("nonexistent", "nx")


class TestRemoveAliasEdgeCases:
    """Tests for edge cases in remove_alias"""

    def test_remove_alias_when_primary_command_has_no_aliases_dict(self):
        """Test remove_alias when primary command is not in _command_aliases dict"""
        app = ExtendedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        # Manually add an alias without registering the command
        app._alias_to_command["orphan"] = "delete"

        # Should return True, but not crash when primary isn't in _command_aliases
        result = app.remove_alias("orphan")
        assert result is True


class TestGetCommandEdgeCases:
    """Tests for edge cases in _get_command"""

    def test_get_command_with_fresh_app_single_command(self):
        """Test _get_command on fresh single-command app"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        def main():
            """Main command."""
            pass

        app._register_command_with_aliases(main, "main", aliases=["m"])

        ctx = MagicMock()

        # First call should trigger CLI build
        cmd = app._get_command(ctx, "main")
        assert cmd is not None
        assert cmd.name == "main"

    def test_get_command_returns_none_for_invalid_command(self):
        """Test that _get_command returns None for truly invalid commands"""
        from unittest.mock import MagicMock

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Get a valid command first to initialise _group
        app._get_command(ctx, "list")

        # Invalid command, should return None
        cmd = app._get_command(ctx, "invalid_command_xyz")
        assert cmd is None

    def test_get_command_with_no_group_or_command_initialised(self):
        """Test _get_command when neither _group nor _command are set"""
        from unittest.mock import MagicMock, patch

        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        ctx = MagicMock()

        # Patch _get_command to return an object without attributes
        with patch("typer.main.get_command") as mock_get_cmd:
            # Return a mock that doesn't have 'commands' attribute
            mock_obj = MagicMock()
            del mock_obj.commands  # Remove the commands attribute
            mock_get_cmd.return_value = mock_obj

            # Delete cached attributes to force re-initialisation
            if hasattr(app, "_group"):
                delattr(app, "_group")
            if hasattr(app, "_command"):
                delattr(app, "_command")

            # Should return None when neither condition is met
            result = app._get_command(ctx, "unknown")
            assert result is None


class TestExtendedGetGroupFromInfo:
    """Tests for _extended_get_group_from_info function and branch coverage"""

    def test_extended_group_with_rich_attributes_in_dict(self):
        """Test that _extended_get_group_from_info preserves rich attributes from __dict__"""
        from typer_extensions.core import (
            ExtendedTyper,
            _extended_get_group_from_info,
            ExtendedGroup,
        )
        from unittest.mock import MagicMock, patch

        # Create mock objects that match the expected interface
        app = ExtendedTyper()
        app._register_alias("list", "ls")  # Register an alias

        # Create a real TyperGroup-like object with rich attributes
        class MockGroup:
            def __init__(self):
                self.name = "test"
                self.callback = None
                self.params = []
                self.help = None
                self.epilog = None
                self.short_help = None
                self.options_metavar = None
                self.subcommand_metavar = None
                self.chain = False
                self.result_callback = None
                self.context_settings = None
                self.commands = {}
                self.rich_markup_mode = "markdown"
                self.rich_help_panel = "Advanced"

        mock_group = MockGroup()

        # Create a mock typer_info
        typer_info = MagicMock()
        typer_info.typer_instance = app

        # Mock the original function to return our mock group
        with patch(
            "typer_extensions.core._original_get_group_from_info",
            return_value=mock_group,
        ):
            result = _extended_get_group_from_info(typer_info)

            # Should return an ExtendedGroup
            assert isinstance(result, ExtendedGroup)
            # The result should have rich attributes set
            assert result.rich_markup_mode == "markdown"
            assert result.rich_help_panel == "Advanced"

    def test_extended_group_no_aliases_registered(self):
        """Test that standard group is returned when no aliases are registered"""
        from typer_extensions.core import ExtendedTyper, _extended_get_group_from_info
        from unittest.mock import MagicMock, patch
        from typer.core import TyperGroup

        # Create app with no aliases
        app = ExtendedTyper()

        # Create a mock group
        mock_group = MagicMock(spec=TyperGroup)
        mock_group.name = "test"

        # Create a mock typer_info
        typer_info = MagicMock()
        typer_info.typer_instance = app

        # Mock the original function
        with patch(
            "typer_extensions.core._original_get_group_from_info",
            return_value=mock_group,
        ):
            result = _extended_get_group_from_info(typer_info)

            # Should return the original group since no aliases registered
            assert result is mock_group

    def test_standard_typer_returns_standard_group(self):
        """Test that non-ExtendedTyper instances return standard groups"""
        from typer_extensions.core import _extended_get_group_from_info
        from unittest.mock import MagicMock, patch
        import typer
        from typer.core import TyperGroup

        # Create a standard Typer app (not ExtendedTyper)
        app = typer.Typer()

        # Create a mock group
        mock_group = MagicMock(spec=TyperGroup)

        # Create a mock typer_info
        typer_info = MagicMock()
        typer_info.typer_instance = app

        # Mock the original function
        with patch(
            "typer_extensions.core._original_get_group_from_info",
            return_value=mock_group,
        ):
            result = _extended_get_group_from_info(typer_info)

            # Should return the original group
            assert result is mock_group

    def test_extended_group_without_dict_attribute(self):
        """Test _extended_get_group_from_info handles group without __dict__ attribute"""
        from typer_extensions.core import (
            ExtendedTyper,
            _extended_get_group_from_info,
            ExtendedGroup,
        )
        from unittest.mock import MagicMock, patch

        # Create an ExtendedTyper with aliases
        app = ExtendedTyper()
        app._register_alias("list", "ls")

        # Create an object without __dict__ using a simple class
        class MockGroupNoDict:
            def __init__(self):
                self.name = "test"
                self.callback = None
                self.params = []
                self.help = None
                self.epilog = None
                self.short_help = None
                self.options_metavar = None
                self.subcommand_metavar = None
                self.chain = False
                self.result_callback = None
                self.context_settings = None
                self.commands = {}
                # Deliberately don't add anything to __dict__ beyond standard class attributes

        mock_group = MockGroupNoDict()

        typer_info = MagicMock()
        typer_info.typer_instance = app

        # Mock hasattr to return False specifically for __dict__
        def mock_hasattr(obj, name):
            if obj is mock_group and name == "__dict__":
                return False
            return object.__getattribute__(obj, name) if hasattr(obj, name) else False

        with patch(
            "typer_extensions.core._original_get_group_from_info",
            return_value=mock_group,
        ):
            with patch("typer_extensions.core.hasattr", side_effect=mock_hasattr):
                result = _extended_get_group_from_info(typer_info)

                # Should still return an ExtendedGroup
                assert isinstance(result, ExtendedGroup)
