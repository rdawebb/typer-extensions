"""Unit tests for Typer compatibility features like Argument and Option"""

import typer
from typer_aliases import AliasedTyper


class TestTyperArgumentAndOption:
    """Tests for accessing Typer's Argument and Option through AliasedTyper"""

    def test_argument_accessible(self):
        """Test that Argument is accessible on AliasedTyper"""
        app = AliasedTyper()
        assert hasattr(app, "Argument")
        assert app.Argument == typer.Argument

    def test_option_accessible(self):
        """Test that Option is accessible on AliasedTyper"""
        app = AliasedTyper()
        assert hasattr(app, "Option")
        assert app.Option == typer.Option

    def test_argument_is_callable(self):
        """Test that Argument can be called as a function"""
        app = AliasedTyper()
        arg = app.Argument(...)
        assert arg is not None

    def test_option_is_callable(self):
        """Test that Option can be called as a function"""
        app = AliasedTyper()
        opt = app.Option(False)
        assert opt is not None

    def test_argument_with_decorator(self):
        """Test using Argument as part of function signature"""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            return f"Hello, {name}!"

        # Should not raise an error
        assert greet is not None

    def test_option_with_decorator(self):
        """Test using Option with command_with_aliases decorator"""
        app = AliasedTyper()

        @app.command_with_aliases("count", aliases=["c"])
        def count(items: int = app.Option(5, "--items", "-i")):
            """Count items."""
            return f"Total: {items}"

        # Should not raise an error
        assert count is not None

    def test_argument_and_option_together(self):
        """Test using Argument (as positional) and Option with command_with_aliases decorator"""
        app = AliasedTyper()

        @app.command_with_aliases("task", aliases=["t"])
        def task(
            name: str,
            priority: int = app.Option(1, "--priority", "-p"),
        ):
            """Create a task."""
            return f"Task: {name}, Priority: {priority}"

        # Should not raise an error
        assert task is not None

    def test_argument_with_standard_command(self):
        """Test using positional arguments with standard @app.command decorator"""
        app = AliasedTyper()

        @app.command()
        def list_items(limit: int):
            """List items."""
            return f"Limit: {limit}"

        # Should not raise an error
        assert list_items is not None

    def test_option_with_standard_command(self):
        """Test using Option with standard @app.command decorator"""
        app = AliasedTyper()

        @app.command()
        def show_info(verbose: bool = app.Option(False, "--verbose", "-v")):
            """Show info."""
            return "Verbose" if verbose else "Normal"

        # Should not raise an error
        assert show_info is not None

    def test_explicit_argument_call(self):
        """Test explicitly calling app.Argument()"""
        app = AliasedTyper()

        # Should be able to call app.Argument() like typer.Argument()
        arg = app.Argument(...)
        assert arg is not None

        arg_with_default = app.Argument("default_value")
        assert arg_with_default is not None
