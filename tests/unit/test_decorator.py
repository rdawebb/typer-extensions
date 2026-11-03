"""Unit tests for command decorator"""

import pytest
import typer.main

from typer_extensions import Context, ExtendedTyper


def lookup(app, name):
    """Retrieve a registered command by name, failing if it is missing"""
    cmd = app._get_command(Context(typer.main.get_command(app)), name)
    assert cmd is not None
    return cmd


class TestDecoratorSyntax:
    """Tests for different decorator syntax variations."""

    def test_decorator_with_explicit_name_and_aliases(self) -> None:
        """Test @app.command("name", aliases=[...])"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List items."""

        assert app._command_aliases["list"] == ["ls", "l"]
        assert app._alias_to_command["ls"] == "list"
        assert app._alias_to_command["l"] == "list"

    def test_decorator_with_inferred_name_and_aliases(self) -> None:
        """Test @app.command(aliases=[...]) - name inferred"""
        app = ExtendedTyper()

        @app.command(aliases=["ls", "l"])
        def list():
            """List items."""

        # Name should be inferred from function name
        assert app._command_aliases["list"] == ["ls", "l"]

    @pytest.mark.parametrize("kwargs", [{}, {"aliases": None}, {"aliases": []}])
    def test_decorator_without_aliases(self, kwargs) -> None:
        """Test @app.command("name") with no, None and empty aliases"""
        app = ExtendedTyper()

        @app.command("list", **kwargs)
        def list_items():
            """List items."""

        assert app._command_aliases == {}
        assert app._alias_to_command == {}

    def test_decorator_without_parentheses(self) -> None:
        """Test @app.command - bare decorator"""
        app = ExtendedTyper()

        @app.command
        def list():
            """List items."""

        # Name inferred, no aliases
        assert "list" not in app._command_aliases
        # But command should be registered via Typer
        typer_command = typer.main.get_command(app)
        assert getattr(typer_command, "name", None) == "list"

    def test_direct_call_keeps_aliases(self) -> None:
        """Test app.command(func, aliases=[...]) registers the aliases"""
        app = ExtendedTyper()

        def quit():
            """Quit."""

        app.command(quit, aliases=["q"])

        assert app.get_aliases("quit") == ["q"]


class TestDecoratorNameInference:
    """Tests for name inference from function names."""

    def test_explicit_name_overrides_function_name(self) -> None:
        """Test that explicit name takes precedence."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_all_items():
            """List items."""

        # Should use explicit name, not function name
        assert "list_all_items" not in app._command_aliases
        assert app._alias_to_command["ls"] == "list"


class TestDecoratorHelpText:
    """Tests for help text preservation."""

    def test_decorator_preserves_docstring(self) -> None:
        """Test that docstring is preserved as help text."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items in the system."""

        assert "List all items" in (lookup(app, "list").help or "")

    def test_decorator_with_explicit_help_kwarg(self) -> None:
        """Test that explicit help overrides the docstring."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"], help="Custom help text")
        def list_items():
            """Original docstring."""

        assert "Custom help" in (lookup(app, "list").help or "")


class TestDecoratorKwargs:
    """Tests for passing through Typer kwargs."""

    def test_decorator_passes_deprecated(self) -> None:
        """Test that deprecated kwarg works."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"], deprecated=True)
        def list_items():
            """List items."""

        assert lookup(app, "list").deprecated is True


class TestDecoratorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_decorator_duplicate_alias_raises(self) -> None:
        """Test that duplicate aliases are detected."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""

        with pytest.raises(ValueError, match="already registered"):

            @app.command("delete", aliases=["ls"])
            def delete_items():
                """Delete items."""


class TestDecoratorReturnValue:
    """Tests for decorator return value."""

    def test_decorator_returns_original_function(self) -> None:
        """Test that the decorated command is still the original function."""
        app = ExtendedTyper()

        def original_func():
            """List items."""

        assert app.command("list", aliases=["ls"])(original_func) is original_func


class TestDecoratorMultipleCommands:
    """Tests for multiple commands with decorator."""

    def test_mixing_decorator_and_standard_command(self) -> None:
        """Test mixing decorated and standard commands."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""

        @app.command()
        def hello():
            """Say hello."""

        # Both should be registered
        assert lookup(app, "list").name == "list"
        assert lookup(app, "hello").name == "hello"

        # Only list should have aliases
        assert list(app._command_aliases) == ["list"]
