"""Unit tests for AliasedTyper core functionality"""

import pytest

from typer_aliases import AliasedTyper


class TestAliasedTyperinitialisation:
    """Tests for AliasedTyper initialisation."""

    def test_default_initialisation(self):
        """Test that AliasedTyper initialises with default config"""
        app = AliasedTyper()
        assert app._alias_case_sensitive is True
        assert app._show_aliases_in_help is True
        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_custom_configuration(self):
        """Test that custom configuration is stored"""
        app = AliasedTyper(
            alias_case_sensitive=False,
            show_aliases_in_help=False,
        )
        assert app._alias_case_sensitive is False
        assert app._show_aliases_in_help is False


class TestNameNormalization:
    """Tests for name normalization based on case sensitivity"""

    def test_normalise_case_sensitive(self):
        """Test name normalization with case sensitivity"""
        app = AliasedTyper(alias_case_sensitive=True)
        assert app._normalise_name("List") == "List"
        assert app._normalise_name("list") == "list"

    def test_normalise_case_insensitive(self):
        """Test name normalization without case sensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        assert app._normalise_name("List") == "list"
        assert app._normalise_name("LIST") == "list"


class TestAliasRegistration:
    """Tests for alias registration logic"""

    def test_register_single_alias(self):
        """Test registering a single alias"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_multiple_aliases_same_command(self):
        """Test registering multiple aliases for same command"""
        app = AliasedTyper()
        app._register_alias("list", "ls")
        app._register_alias("list", "l")

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_register_duplicate_alias_raises(self):
        """Test that duplicate alias raises ValueError"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "ls")

    def test_alias_same_as_primary_raises(self):
        """Test that alias matching primary name raises ValueError"""
        app = AliasedTyper()

        with pytest.raises(ValueError, match="cannot be the same as command name"):
            app._register_alias("list", "list")

    def test_case_insensitive_alias_conflict(self):
        """Test alias conflict detection with case insensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        with pytest.raises(ValueError, match="already registered"):
            app._register_alias("delete", "LS")  # Case-insensitive, should raise

    def test_case_sensitive_allows_different_case(self):
        """Test that case-sensitive mode allows different cases"""
        app = AliasedTyper(alias_case_sensitive=True)
        app._register_alias("list", "ls")
        app._register_alias("delete", "LS")  # Case-sensitive, should work

        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["LS"] == "delete"


class TestAliasResolution:
    """Tests for alias resolution"""

    def test_resolve_existing_alias(self):
        """Test resolving an existing alias"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        assert app._resolve_alias("ls") == "list"

    def test_resolve_nonexistent_alias(self):
        """Test resolving a non-existent alias returns None"""
        app = AliasedTyper()
        assert app._resolve_alias("nonexistent") is None

    def test_resolve_primary_name_returns_none(self):
        """Test that resolving primary name returns None"""
        app = AliasedTyper()
        app._register_alias("list", "ls")

        # Primary name is not an alias, should return None
        assert app._resolve_alias("list") is None

    def test_resolve_case_insensitive(self):
        """Test alias resolution with case insensitivity"""
        app = AliasedTyper(alias_case_sensitive=False)
        app._register_alias("list", "ls")

        assert app._resolve_alias("LS") == "list"
        assert app._resolve_alias("Ls") == "list"


class TestCommandWithAliases:
    """Tests for command registration with aliases"""

    def test_register_command_with_single_alias(self):
        """Test registering command with one alias"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        assert "list" in app._command_aliases
        assert "ls" in app._command_aliases["list"]
        assert app._alias_to_command["ls"] == "list"

    def test_register_command_with_multiple_aliases(self):
        """Test registering command with multiple aliases"""
        app = AliasedTyper()

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
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=None)

        # No aliases should be registered
        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_register_command_empty_alias_list(self):
        """Test registering command with empty alias list"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=[])

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_alias_conflicts_detected_during_registration(self):
        """Test that alias conflicts are detected during command registration"""
        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        def delete_items():
            """Delete items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        with pytest.raises(ValueError, match="conflicts with existing command"):
            app._register_command_with_aliases(delete_items, "delete", aliases=["ls"])


class TestGetCommand:
    """Tests for get_command with alias support"""

    def test_get_command_by_primary_name(self):
        """Test getting command by its primary name"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        # Create a mock context
        ctx = MagicMock()

        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert cmd.name == "list"

    def test_get_command_by_alias(self):
        """Test getting command by alias."""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        # Create a mock context
        ctx = MagicMock()

        cmd = app.get_command(ctx, "ls")
        assert cmd is not None

        # Command should be the same as the primary
        primary_cmd = app.get_command(ctx, "list")
        assert cmd.callback == primary_cmd.callback

    def test_get_command_nonexistent(self):
        """Test getting non-existent command returns None"""
        from unittest.mock import MagicMock

        app = AliasedTyper()

        # Create a mock context
        ctx = MagicMock()

        cmd = app.get_command(ctx, "nonexistent")
        assert cmd is None

    def test_get_command_case_insensitive_alias(self):
        """Test getting command by case-insensitive alias"""
        from unittest.mock import MagicMock

        app = AliasedTyper(alias_case_sensitive=False)

        def list_items():
            """List items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        # Create a mock context
        ctx = MagicMock()

        # Should work with different case
        cmd = app.get_command(ctx, "LS")
        assert cmd is not None
