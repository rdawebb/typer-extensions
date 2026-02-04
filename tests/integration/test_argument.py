"""Integration tests for Argument with command aliases.

This module tests that positional arguments work identically whether invoked via the primary command name or an alias.
"""

import pytest
from typer_extensions import ExtendedTyper


class TestArgumentsWithAliases:
    """Tests for arguments working identically with primary commands and aliases."""

    def test_single_argument_via_primary(self, cli_runner):
        """Test single positional argument via primary command."""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["greet", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_single_argument_via_alias(self, cli_runner):
        """Test single positional argument via alias."""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["hi", "Bob"])
        assert result.exit_code == 0
        assert "Hello, Bob!" in result.output

        result = cli_runner.invoke(app, ["hello", "Charlie"])
        assert result.exit_code == 0
        assert "Hello, Charlie!" in result.output

    def test_multiple_arguments_via_primary(self, cli_runner):
        """Test multiple positional arguments via primary command."""
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(source: str, destination: str):
            """Copy a file."""
            print(f"Copying {source} to {destination}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["copy", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    def test_multiple_arguments_via_alias(self, cli_runner):
        """Test multiple positional arguments via alias."""
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(source: str, destination: str):
            """Copy a file."""
            print(f"Copying {source} to {destination}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["cp", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    @pytest.mark.parametrize(
        "command,number",
        [
            ("count", "5"),
            ("c", "10"),
        ],
    )
    def test_argument_with_type_conversion_int(self, cli_runner, command, number):
        """Test argument with integer type conversion."""
        app = ExtendedTyper()

        @app.command("count", aliases=["c"])
        def count_down(number: int):
            """Count down from a number."""
            print(f"Counting down from {number}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, [command, number])
        assert result.exit_code == 0
        assert f"Counting down from {number}" in result.output

    @pytest.mark.parametrize(
        "command,value,expected",
        [
            ("calculate", "3.5", "7.0"),
            ("calc", "2.5", "5.0"),
        ],
    )
    def test_argument_with_type_conversion_float(
        self, cli_runner, command, value, expected
    ):
        """Test argument with float type conversion."""
        app = ExtendedTyper()

        @app.command("calculate", aliases=["calc"])
        def calculate(value: float):
            """Calculate something."""
            result = value * 2
            print(f"Result: {result}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, [command, value])
        assert result.exit_code == 0
        assert f"Result: {expected}" in result.output

    def test_optional_argument_with_default(self, cli_runner):
        """Test optional argument with default value."""
        app = ExtendedTyper()

        @app.command("say", aliases=["s"])
        def say(message: str = app.Argument("Hello")):
            """Say a message."""
            print(message)

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["say"])
        assert result.exit_code == 0
        assert "Hello" in result.output

        result = cli_runner.invoke(app, ["say", "Goodbye"])
        assert result.exit_code == 0
        assert "Goodbye" in result.output

        result = cli_runner.invoke(app, ["s", "Hi there"])
        assert result.exit_code == 0
        assert "Hi there" in result.output

    def test_required_argument_missing_error(self, cli_runner):
        """Test error when required argument is missing."""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["greet"])
        assert result.exit_code != 0


class TestArgumentsInHelp:
    """Tests for argument display in help text."""

    def test_help_shows_argument_via_primary(self, cli_runner, clean_output):
        """Test help shows argument info via primary command."""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone by name."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["greet", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "NAME" in clean_result or "name" in clean_result
        assert "Greet someone" in clean_result

    def test_help_shows_argument_via_alias(self, cli_runner, clean_output):
        """Test help shows argument info via alias."""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone by name."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["hi", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "NAME" in clean_result or "name" in clean_result
        assert "Greet someone" in clean_result

    def test_help_shows_multiple_arguments(self, cli_runner, clean_output):
        """Test help shows all arguments."""
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(
            source: str = app.Argument(..., help="Source file path"),
            dest: str = app.Argument(..., help="Destination file path"),
        ):
            """Copy a file from source to destination."""
            print(f"Copying {source} to {dest}")

        result = cli_runner.invoke(app, ["cp", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "SOURCE" in clean_result or "source" in clean_result
        assert "DEST" in clean_result or "dest" in clean_result
        assert "Copy a file" in clean_result


class TestArgumentsWithOptions:
    """Tests for combining arguments and options together."""

    def test_argument_and_option_together_via_primary(self, cli_runner):
        """Test command with both argument and option via primary."""
        app = ExtendedTyper()

        @app.command("deploy", aliases=["d"])
        def deploy(service: str, force: bool = app.Option(False, "--force", "-f")):
            """Deploy a service."""
            mode = "force" if force else "normal"
            print(f"Deploying {service} in {mode} mode")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["deploy", "api-server"])
        assert result.exit_code == 0
        assert "api-server" in result.output
        assert "normal mode" in result.output

        result = cli_runner.invoke(app, ["deploy", "api-server", "--force"])
        assert result.exit_code == 0
        assert "api-server" in result.output
        assert "force mode" in result.output

    def test_argument_and_option_together_via_alias(self, cli_runner):
        """Test command with both argument and option via alias."""
        app = ExtendedTyper()

        @app.command("deploy", aliases=["d"])
        def deploy(service: str, force: bool = app.Option(False, "--force", "-f")):
            """Deploy a service."""
            mode = "force" if force else "normal"
            print(f"Deploying {service} in {mode} mode")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["d", "web-server"])
        assert result.exit_code == 0
        assert "web-server" in result.output

        result = cli_runner.invoke(app, ["d", "web-server", "-f"])
        assert result.exit_code == 0
        assert "web-server" in result.output
        assert "force mode" in result.output

    def test_multiple_arguments_and_options(self, cli_runner):
        """Test command with multiple arguments and options."""
        app = ExtendedTyper()

        @app.command("build", aliases=["b"])
        def build(
            project: str = app.Argument(...),
            target: str = app.Argument("default"),
            release: bool = app.Option(False, "--release", "-r"),
            jobs: int = app.Option(1, "--jobs", "-j"),
        ):
            """Build a project."""
            mode = "release" if release else "debug"
            print(f"Building {project} (target: {target}, mode: {mode}, jobs: {jobs})")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["build", "myapp"])
        assert result.exit_code == 0
        assert "myapp" in result.output
        assert "target: default" in result.output

        result = cli_runner.invoke(app, ["b", "myapp", "production", "-r", "-j", "8"])
        assert result.exit_code == 0
        assert "myapp" in result.output
        assert "target: production" in result.output
        assert "release" in result.output
        assert "jobs: 8" in result.output

    def test_argument_with_option_bool_flag(self, cli_runner):
        """Test argument with boolean option flag."""
        app = ExtendedTyper()

        @app.command("delete", aliases=["rm", "del"])
        def delete(path: str, force: bool = app.Option(False, "--force", "-f")):
            """Delete a file or directory."""
            if force:
                print(f"Force deleting {path}")
            else:
                print(f"Deleting {path}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["rm", "file.txt"])
        assert result.exit_code == 0
        assert "Deleting file.txt" in result.output

        result = cli_runner.invoke(app, ["del", "important_dir", "--force"])
        assert result.exit_code == 0
        assert "Force deleting important_dir" in result.output

    def test_help_with_arguments_and_options(self, cli_runner, clean_output):
        """Test help shows all arguments and options."""
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(
            source: str = app.Argument(..., help="Source file path"),
            dest: str = app.Argument(..., help="Destination file path"),
            force: bool = app.Option(False, "--force", "-f", help="Force overwrite"),
        ):
            """Copy a file from source to destination."""
            print(f"Copying {source} to {dest}")

        result = cli_runner.invoke(app, ["cp", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        assert "SOURCE" in clean_result or "source" in clean_result
        assert "DEST" in clean_result or "dest" in clean_result
        assert "--force" in clean_result or "-f" in clean_result
        assert "Copy a file" in clean_result
