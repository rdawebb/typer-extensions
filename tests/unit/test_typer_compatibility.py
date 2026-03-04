"""Unit tests for Typer compatibility features like Argument, Option, and other utility functions"""

from unittest.mock import patch

import pytest
import typer


class TestTyperArgumentAndOption:
    """Tests for accessing Typer's Argument and Option through ExtendedTyper"""

    def test_argument_accessible(self, app):
        """Test that Argument is accessible on ExtendedTyper"""
        assert hasattr(app, "Argument")
        assert app.Argument == typer.Argument

    def test_option_accessible(self, app):
        """Test that Option is accessible on ExtendedTyper"""
        assert hasattr(app, "Option")
        assert app.Option == typer.Option

    def test_argument_with_decorator(self, app):
        """Test using Argument as part of function signature"""

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            return f"Hello, {name}!"

        assert greet is not None

    def test_option_with_decorator(self, app):
        """Test using Option with command decorator"""

        @app.command("count", aliases=["c"])
        def count(items: int = app.Option(5, "--items", "-i")):
            """Count items."""
            return f"Total: {items}"

        assert count is not None

    def test_argument_and_option_together(self, app):
        """Test using Argument (as positional) and Option together in a command"""

        @app.command("task", aliases=["t"])
        def task(
            name: str,
            priority: int = app.Option(1, "--priority", "-p"),
        ):
            """Create a task."""
            return f"Task: {name}, Priority: {priority}"

        assert task is not None


class TestTyperUtilityFunctions:
    """Tests for accessing common Typer utility functions via ExtendedTyper.

    Each utility is delegated from ExtendedTyper.__getattr__ to the underlying
    typer module. The parametrized test confirms all delegations are correct;
    the individual tests below verify the handful of functions with real behaviour.
    """

    @pytest.mark.parametrize(
        "attr",
        [
            "echo",
            "echo_via_pager",
            "secho",
            "style",
            "prompt",
            "confirm",
            "getchar",
            "clear",
            "pause",
            "progressbar",
            "launch",
            "open_file",
            "get_app_dir",
            "get_terminal_size",
            "run",
        ],
    )
    def test_utility_delegated_to_typer(self, app, attr):
        """Test that every utility function is accessible and delegates to typer."""
        assert hasattr(app, attr)
        assert getattr(app, attr) is getattr(typer, attr)

    def test_style_returns_string(self, app):
        """Test that style() returns a styled string."""
        result = app.style("Hello, World!", fg="blue")
        assert isinstance(result, str)

    def test_open_file_reads_content(self, app, tmp_path):
        """Test that open_file() can open and read a file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, Typer!")
        with app.open_file(str(test_file), "r") as f:
            assert f.read() == "Hello, Typer!"

    def test_get_app_dir_returns_path_string(self, app):
        """Test that get_app_dir() returns a valid directory string."""
        result = app.get_app_dir("ExtendedTyper")
        assert isinstance(result, str)
        assert "extendedtyper" in result.lower()

    def test_get_terminal_size_returns_int_tuple(self, app):
        """Test that get_terminal_size() returns a 2-tuple of ints."""
        result = app.get_terminal_size()
        assert isinstance(result, tuple)
        assert len(result) == 2
        assert all(isinstance(x, int) for x in result)

    def test_progressbar_is_iterable(self, app):
        """Test that progressbar() works as a context manager iterator."""
        items = [1, 2, 3]
        with app.progressbar(iter(items)) as bar:
            for _ in bar:
                pass  # Should not raise

    def test_launch_is_callable(self, app):
        """Test that launch() is callable (mocked to avoid opening a browser)."""
        with patch.object(app, "launch") as mock_launch:
            app.launch("http://example.com")
            mock_launch.assert_called_once_with("http://example.com")
