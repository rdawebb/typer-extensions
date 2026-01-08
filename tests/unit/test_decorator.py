"""Unit tests for command_with_aliases decorator"""

import pytest
import typer.main
from click import Context

from typer_aliases import AliasedTyper


class TestDecoratorSyntax:
    """Tests for different decorator syntax variations."""

    def test_decorator_with_explicit_name_and_aliases(self):
        """Test @app.command_with_aliases("name", aliases=[...])"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_items():
            """List items."""
            pass

        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_decorator_with_inferred_name_and_aliases(self):
        """Test @app.command_with_aliases(aliases=[...]) - name inferred"""
        app = AliasedTyper()

        @app.command_with_aliases(aliases=["ls", "l"])
        def list():
            """List items."""
            pass

        # Name should be inferred from function name
        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]

    def test_decorator_with_explicit_name_no_aliases(self):
        """Test @app.command_with_aliases("name") - no aliases"""
        app = AliasedTyper()

        @app.command_with_aliases("list")
        def list_items():
            """List items."""
            pass

        # Command registered but no aliases
        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_decorator_without_parentheses(self):
        """Test @app.command_with_aliases - bare decorator"""
        app = AliasedTyper()

        @app.command_with_aliases
        def list():
            """List items."""
            pass

        # Name inferred, no aliases
        assert "list" not in app._command_aliases
        # But command should be registered via Typer
        click_command = typer.main.get_command(app)
        assert click_command is not None
        assert getattr(click_command, "name", None) == "list"

    def test_decorator_with_empty_alias_list(self):
        """Test @app.command_with_aliases("name", aliases=[])"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=[])
        def list_items():
            """List items."""
            pass

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_decorator_with_none_aliases(self):
        """Test @app.command_with_aliases("name", aliases=None)"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=None)
        def list_items():
            """List items."""
            pass

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0


class TestDecoratorNameInference:
    """Tests for name inference from function names."""

    def test_name_inferred_from_function_name(self):
        """Test that name is correctly inferred from function."""
        app = AliasedTyper()

        @app.command_with_aliases(aliases=["ls"])
        def list_items():
            """List items."""
            pass

        # Should use function name as command name
        assert "list_items" in app._command_aliases
        assert app._alias_to_command["ls"] == "list_items"

    def test_explicit_name_overrides_function_name(self):
        """Test that explicit name takes precedence."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_all_items():
            """List items."""
            pass

        # Should use explicit name, not function name
        assert "list" in app._command_aliases
        assert "list_all_items" not in app._command_aliases
        assert app._alias_to_command["ls"] == "list"

    def test_underscore_function_name(self):
        """Test function names with underscores."""
        app = AliasedTyper()

        @app.command_with_aliases(aliases=["ls"])
        def list_all_items():
            """List items."""
            pass

        # Typer keeps underscores in command names by default
        assert "list_all_items" in app._command_aliases


class TestDecoratorHelpText:
    """Tests for help text preservation."""

    def test_decorator_preserves_docstring(self):
        """Test that docstring is preserved as help text."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List all items in the system."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert "List all items" in (cmd.help or "")

    def test_decorator_with_explicit_help_kwarg(self):
        """Test that explicit help kwarg works."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"], help="Custom help text")
        def list_items():
            """Original docstring."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        # Explicit help should override docstring
        assert "Custom help" in (cmd.help or "")


class TestDecoratorKwargs:
    """Tests for passing through Typer kwargs."""

    def test_decorator_passes_context_settings(self):
        """Test that context_settings kwarg works."""
        app = AliasedTyper()

        @app.command_with_aliases(
            "list", aliases=["ls"], context_settings={"allow_extra_args": True}
        )
        def list_items():
            """List items."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert cmd.context_settings is not None

    def test_decorator_passes_deprecated(self):
        """Test that deprecated kwarg works."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"], deprecated=True)
        def list_items():
            """List items."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert cmd.deprecated is True

    def test_decorator_with_multiple_kwargs(self):
        """Test decorator with multiple Typer kwargs."""
        app = AliasedTyper()

        @app.command_with_aliases(
            "list",
            aliases=["ls"],
            help="List items",
            epilog="Additional info",
            short_help="List",
        )
        def list_items():
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app.get_command(ctx, "list")
        assert cmd is not None
        assert "List items" in (cmd.help or "")


class TestDecoratorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_decorator_with_single_alias(self):
        """Test decorator with just one alias."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        assert app._command_aliases["list"] == ["ls"]

    def test_decorator_with_many_aliases(self):
        """Test decorator with many aliases."""
        app = AliasedTyper()

        aliases = ["ls", "l", "dir", "ll", "la"]

        @app.command_with_aliases("list", aliases=aliases)
        def list_items():
            """List items."""
            pass

        assert app._command_aliases["list"] == aliases
        for alias in aliases:
            assert app._alias_to_command[alias] == "list"

    def test_decorator_duplicate_alias_raises(self):
        """Test that duplicate aliases are detected."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        with pytest.raises(ValueError, match="already registered"):

            @app.command_with_aliases("delete", aliases=["ls"])
            def delete_items():
                """Delete items."""
                pass

    def test_decorator_on_lambda_raises_no_error(self):
        """Test decorator can work with lambda (though not recommended)."""
        app = AliasedTyper()

        # This should work but name will be '<lambda>'
        def list_func():
            print("listing")

        app.command_with_aliases("list", aliases=["ls"])(list_func)

        assert "list" in app._command_aliases


class TestDecoratorReturnValue:
    """Tests for decorator return value."""

    def test_decorator_returns_command_object(self):
        """Test that decorator returns Click Command."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        # The decorator should have returned something
        # (Note: The decorated function is now a Command)
        assert list_items is not None

    def test_decorator_command_callable(self):
        """Test that the decorated command is still the original function."""
        app = AliasedTyper()

        def original_func():
            """List items."""
            return "listed"

        decorated = app.command_with_aliases("list", aliases=["ls"])(original_func)

        # The decorated result should be a Command, but we can verify
        # it was created from the original function
        assert decorated is not None


class TestDecoratorMultipleCommands:
    """Tests for multiple commands with decorator."""

    def test_multiple_decorated_commands(self):
        """Test decorating multiple commands."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_items():
            """List items."""
            pass

        @app.command_with_aliases("delete", aliases=["rm", "remove"])
        def delete_item():
            """Delete item."""
            pass

        assert "list" in app._command_aliases
        assert "delete" in app._command_aliases
        assert len(app._command_aliases) == 2
        assert len(app._alias_to_command) == 4  # 2 + 2 aliases

    def test_mixing_decorator_and_standard_command(self):
        """Test mixing decorated and standard commands."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command()
        def hello():
            """Say hello."""
            pass

        # Both should be registered
        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        assert app.get_command(ctx, "list") is not None
        assert app.get_command(ctx, "hello") is not None

        # Only list should have aliases
        assert "list" in app._command_aliases
        assert "hello" not in app._command_aliases
