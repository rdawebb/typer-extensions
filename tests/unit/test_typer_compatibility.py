"""Unit tests for Typer compatibility features like Argument, Option, and other utility functions"""

from unittest.mock import patch

import typer

from typer_extensions import ExtendedTyper


class TestTyperArgumentAndOption:
    """Tests for accessing Typer's Argument and Option through ExtendedTyper"""

    def test_argument_accessible(self):
        """Test that Argument is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "Argument")
        assert app.Argument == typer.Argument

    def test_option_accessible(self):
        """Test that Option is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "Option")
        assert app.Option == typer.Option

    def test_argument_is_callable(self):
        """Test that Argument can be called as a function"""
        app = ExtendedTyper()
        arg = app.Argument(...)
        assert arg is not None

    def test_option_is_callable(self):
        """Test that Option can be called as a function"""
        app = ExtendedTyper()
        opt = app.Option(False)
        assert opt is not None

    def test_argument_with_decorator(self):
        """Test using Argument as part of function signature"""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            return f"Hello, {name}!"

        # Should not raise an error
        assert greet is not None

    def test_option_with_decorator(self):
        """Test using Option with command_with_aliases decorator"""
        app = ExtendedTyper()

        @app.command("count", aliases=["c"])
        def count(items: int = app.Option(5, "--items", "-i")):
            """Count items."""
            return f"Total: {items}"

        # Should not raise an error
        assert count is not None

    def test_argument_and_option_together(self):
        """Test using Argument (as positional) and Option with command_with_aliases decorator"""
        app = ExtendedTyper()

        @app.command("task", aliases=["t"])
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
        app = ExtendedTyper()

        @app.command()
        def list_items(limit: int):
            """List items."""
            return f"Limit: {limit}"

        # Should not raise an error
        assert list_items is not None

    def test_option_with_standard_command(self):
        """Test using Option with standard @app.command decorator"""
        app = ExtendedTyper()

        @app.command()
        def show_info(verbose: bool = app.Option(False, "--verbose", "-v")):
            """Show info."""
            return "Verbose" if verbose else "Normal"

        # Should not raise an error
        assert show_info is not None

    def test_explicit_argument_call(self):
        """Test explicitly calling app.Argument()"""
        app = ExtendedTyper()

        # Should be able to call app.Argument() like typer.Argument()
        arg = app.Argument(...)
        assert arg is not None

        arg_with_default = app.Argument("default_value")
        assert arg_with_default is not None


class TestTyperUtilityFunctions:
    """Tests for accessing common Typer utility functions"""

    def test_echo_accessible(self):
        """Test that echo function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "echo")
        assert app.echo == typer.echo

    def test_echo_is_callable(self):
        """Test that echo function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        app.echo("Hello, World!")  # Should not raise an error

    def test_secho_accessible(self):
        """Test that secho function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "secho")
        assert app.secho == typer.secho

    def test_secho_is_callable(self):
        """Test that secho function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        app.secho("Hello, World!", fg="green")  # Should not raise an error

    def test_style_accessible(self):
        """Test that style function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "style")
        assert app.style == typer.style

    def test_style_is_callable(self):
        """Test that style function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        result = app.style("Hello, World!", fg="blue")
        assert isinstance(result, str)

    def test_prompt_accessible(self):
        """Test that prompt function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "prompt")
        assert app.prompt == typer.prompt

    def test_confirm_accessible(self):
        """Test that confirm function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "confirm")
        assert app.confirm == typer.confirm

    def test_getchar_accessible(self):
        """Test that getchar function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "getchar")
        assert app.getchar == typer.getchar

    def test_progressbar_accessible(self):
        """Test that progressbar function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "progressbar")
        assert app.progressbar == typer.progressbar

    def test_progressbar_is_callable(self):
        """Test that progressbar function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        items = [1, 2, 3]
        with app.progressbar(iter(items)) as bar:
            for _ in bar:
                pass  # Should not raise an error

    def test_launch_accessible(self):
        """Test that launch function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "launch")
        assert app.launch == typer.launch

    def test_launch_is_callable(self):
        """Test that launch function is callable on ExtendedTyper"""
        with patch.object(ExtendedTyper, "launch") as mock_launch:
            app = ExtendedTyper()
            app.launch("http://example.com")
            mock_launch.assert_called_once_with("http://example.com")

    def test_get_app_dir_accessible(self):
        """Test that get_app_dir function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "get_app_dir")
        assert app.get_app_dir == typer.get_app_dir

    def test_get_app_dir_is_callable(self):
        """Test that get_app_dir function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        result = app.get_app_dir("ExtendedTyper")
        assert isinstance(result, str)
        assert "extendedtyper" in result.lower()

    def test_get_terminal_size_accessible(self):
        """Test that get_terminal_size function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "get_terminal_size")
        assert app.get_terminal_size == typer.get_terminal_size

    def test_get_terminal_size_is_callable(self):
        """Test that get_terminal_size function is callable on ExtendedTyper"""
        app = ExtendedTyper()
        result = app.get_terminal_size()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)

    def test_run_accessible(self):
        """Test that run function is accessible on ExtendedTyper"""
        app = ExtendedTyper()
        assert hasattr(app, "run")
        assert app.run == typer.run
