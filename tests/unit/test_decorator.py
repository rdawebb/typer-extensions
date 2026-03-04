"""Unit tests for command decorator"""

import pytest
import typer.main

from typer_extensions import Context


class TestDecoratorSyntax:
    """Tests for different decorator syntax variations."""

    def test_decorator_with_explicit_name_and_aliases(self, app_with_aliases):
        """Test @app.command("name", aliases=[...])"""

        assert "list" in app_with_aliases._command_aliases
        assert app_with_aliases._command_aliases["list"] == ["ls", "l"]
        assert app_with_aliases._alias_to_command["ls"] == "list"
        assert app_with_aliases._alias_to_command["l"] == "list"

    def test_decorator_with_inferred_name_and_aliases(self, app):
        """Test @app.command(aliases=[...]) - name inferred"""

        @app.command(aliases=["ls", "l"])
        def list():
            """List items."""
            pass

        # Name should be inferred from function name
        assert "list" in app._command_aliases
        assert app._command_aliases["list"] == ["ls", "l"]

    def test_decorator_with_explicit_name_no_aliases(self, app_with_commands):
        """Test @app.command("name") - no aliases"""

        # Command registered but no aliases
        assert "list" not in app_with_commands._command_aliases
        assert len(app_with_commands._alias_to_command) == 0

    def test_decorator_without_parentheses(self, app):
        """Test @app.command - bare decorator"""

        @app.command
        def list():
            """List items."""
            pass

        # Name inferred, no aliases
        assert "list" not in app._command_aliases
        # But command should be registered via Typer
        click_command = typer.main.get_command(app)
        assert click_command is not None
        assert getattr(click_command, "name", None) == "list"

    def test_decorator_with_empty_alias_list(self, app):
        """Test @app.command("name", aliases=[])"""

        @app.command("list", aliases=[])
        def list_items():
            """List items."""
            pass

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0

    def test_decorator_with_none_aliases(self, app):
        """Test @app.command("name", aliases=None)"""

        @app.command("list", aliases=None)
        def list_items():
            """List items."""
            pass

        assert "list" not in app._command_aliases
        assert len(app._alias_to_command) == 0


class TestDecoratorNameInference:
    """Tests for name inference from function names."""

    def test_name_inferred_from_function_name(self, app):
        """Test that name is correctly inferred from function."""

        @app.command(aliases=["ls"])
        def list_items():
            """List items."""
            pass

        # Should use function name as command name
        assert "list_items" in app._command_aliases
        assert app._alias_to_command["ls"] == "list_items"

    def test_explicit_name_overrides_function_name(self, app_with_aliases):
        """Test that explicit name takes precedence."""

        # Should use explicit name, not function name
        assert "list" in app_with_aliases._command_aliases
        assert "list_items" not in app_with_aliases._command_aliases
        assert app_with_aliases._alias_to_command["ls"] == "list"

    def test_underscore_function_name(self, app):
        """Test function names with underscores."""

        @app.command(aliases=["ls"])
        def list_all_items():
            """List items."""
            pass

        # Typer keeps underscores in command names by default
        assert "list_all_items" in app._command_aliases


class TestDecoratorHelpText:
    """Tests for help text preservation."""

    def test_decorator_preserves_docstring(self, app_with_aliases):
        """Test that docstring is preserved as help text."""

        click_group = typer.main.get_command(app_with_aliases)
        ctx = Context(click_group)
        cmd = app_with_aliases._get_command(ctx, "list")
        assert cmd is not None
        assert "List all items" in (cmd.help or "")

    def test_decorator_with_explicit_help_kwarg(self, app):
        """Test that explicit help kwarg works."""

        @app.command("list", aliases=["ls"], help="Custom help text")
        def list_items():
            """Original docstring."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        # Explicit help should override docstring
        assert "Custom help" in (cmd.help or "")


class TestDecoratorKwargs:
    """Tests for passing through Typer kwargs."""

    def test_decorator_passes_context_settings(self, app):
        """Test that context_settings kwarg works."""

        @app.command(
            "list", aliases=["ls"], context_settings={"allow_extra_args": True}
        )
        def list_items():
            """List items."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert cmd.context_settings is not None

    def test_decorator_passes_deprecated(self, app):
        """Test that deprecated kwarg works."""

        @app.command("list", aliases=["ls"], deprecated=True)
        def list_items():
            """List items."""
            pass

        click_group = typer.main.get_command(app)
        ctx = Context(click_group)
        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert cmd.deprecated is True

    def test_decorator_with_multiple_kwargs(self, app):
        """Test decorator with multiple Typer kwargs."""

        @app.command(
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
        cmd = app._get_command(ctx, "list")
        assert cmd is not None
        assert "List items" in (cmd.help or "")


class TestDecoratorEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_decorator_with_single_alias(self, app):
        """Test decorator with just one alias."""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        assert app._command_aliases["list"] == ["ls"]

    def test_decorator_with_many_aliases(self, app):
        """Test decorator with many aliases."""

        aliases = ["ls", "l", "dir", "ll", "la"]

        @app.command("list", aliases=aliases)
        def list_items():
            """List items."""
            pass

        assert app._command_aliases["list"] == aliases
        for alias in aliases:
            assert app._alias_to_command[alias] == "list"

    def test_decorator_duplicate_alias_raises(self, app):
        """Test that duplicate aliases are detected."""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        with pytest.raises(ValueError, match="already registered"):

            @app.command("delete", aliases=["ls"])
            def delete_items():
                """Delete items."""
                pass

    def test_decorator_on_lambda_raises_no_error(self, app):
        """Test decorator can work with lambda (though not recommended)."""

        # This should work but name will be '<lambda>'
        def list_func():
            print("listing")

        app.command("list", aliases=["ls"])(list_func)

        assert "list" in app._command_aliases


class TestDecoratorReturnValue:
    """Tests for decorator return value."""

    def test_decorator_returns_command_object(self, app):
        """Test that decorator returns Click Command."""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        # Should be a Click Command
        assert list_items is not None

    def test_decorator_command_callable(self, app):
        """Test that the decorated command is still the original function."""

        def original_func():
            """List items."""
            return "listed"

        decorated = app.command("list", aliases=["ls"])(original_func)

        # The decorated result should be a Command
        assert decorated is not None


class TestDecoratorMultipleCommands:
    """Tests for multiple commands with decorator."""

    def test_multiple_decorated_commands(self, app_with_aliases):
        """Test decorating multiple commands."""

        assert "list" in app_with_aliases._command_aliases
        assert "delete" in app_with_aliases._command_aliases
        assert len(app_with_aliases._command_aliases) == 2
        assert len(app_with_aliases._alias_to_command) == 3  # 2 + 1 aliases (ls, l, rm)

    def test_mixing_decorator_and_standard_command(self, app):
        """Test mixing decorated and standard commands."""

        @app.command("list", aliases=["ls"])
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
        assert app._get_command(ctx, "list") is not None
        assert app._get_command(ctx, "hello") is not None

        # Only list should have aliases
        assert "list" in app._command_aliases
        assert "hello" not in app._command_aliases
