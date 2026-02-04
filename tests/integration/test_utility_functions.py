"""Integration tests for common Typer utility functions in ExtendedTyper"""

from unittest.mock import patch

from typer_extensions import ExtendedTyper


class TestUtilityFunctions:
    """Tests for common Typer utility functions in ExtendedTyper"""

    def test_prompt_integration(self, cli_runner, clean_output):
        """Test prompt working with commands and aliases."""
        app = ExtendedTyper()

        @app.command()
        def greet():
            """Greet the user by name."""
            name = app.prompt("Enter your name")
            app.echo(f"Hello, {name}!")

        @app.command(aliases=["bye", "farewell"])
        def goodbye():
            """Greet the user by name."""
            name = app.prompt("Enter your name")
            app.echo(f"Goodbye, {name}!")

        result = cli_runner.invoke(app, ["greet"], input="Alice\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Hello, Alice!" in clean_result

        result = cli_runner.invoke(app, ["bye"], input="Bob\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Goodbye, Bob!" in clean_result

        result = cli_runner.invoke(app, ["farewell"], input="Charlie\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Goodbye, Charlie!" in clean_result

    def test_prompt_with_default(self, cli_runner, clean_output):
        """Test prompt working with default values."""
        app = ExtendedTyper()

        @app.command()
        def greet():
            """Greet the user by name."""
            name = app.prompt("Enter your name", default="World")
            app.echo(f"Hello, {name}!")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        result = cli_runner.invoke(app, ["greet"], input="\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Hello, World!" in clean_result

    def test_prompt_type_conversion(self, cli_runner, clean_output):
        """Test prompt working with type conversion"""
        app = ExtendedTyper()

        @app.command()
        def ask_age():
            """Ask the user for their age."""
            age = app.prompt("Enter your age", type=int)
            app.echo(f"You are {age} years old.")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        # Valid int
        result = cli_runner.invoke(app, ["ask_age"], input="30\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You are 30 years old." in clean_result

    def test_confirm_integration(self, cli_runner, clean_output):
        """Test confirm working with commands and aliases."""
        app = ExtendedTyper()

        @app.command()
        def save_file():
            """Save a file."""
            if app.confirm("Are you sure you want to save this file?"):
                app.echo("File saved.")
            else:
                app.echo("File not saved.")

        @app.command(aliases=["rm", "del"])
        def delete_file():
            """Delete a file."""
            if app.confirm("Are you sure you want to delete this file?"):
                app.echo("File deleted.")
            else:
                app.echo("File not deleted.")

        result = cli_runner.invoke(app, ["save_file"], input="y\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File saved." in clean_result

        result = cli_runner.invoke(app, ["rm"], input="n\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File not deleted." in clean_result

        result = cli_runner.invoke(app, ["del"], input="y\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File deleted." in clean_result

    def test_confirm_case_insensitivity(self, cli_runner, clean_output):
        """Test confirm working with case insensitivity."""
        app = ExtendedTyper()

        @app.command()
        def save_file():
            """Save a file."""
            if app.confirm("Are you sure you want to save this file?"):
                app.echo("File saved.")
            else:
                app.echo("File not saved.")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        # Uppercase "Y"
        result = cli_runner.invoke(app, ["save_file"], input="Y\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File saved." in clean_result

        # Full word "no"
        result = cli_runner.invoke(app, ["save_file"], input="no\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File not saved." in clean_result

        # Invalid input, then lowercase "y"
        result = cli_runner.invoke(app, ["save_file"], input="maybe\ny\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "File saved." in clean_result

    def test_getchar_integration(self, cli_runner, clean_output):
        """Test getchar working with commands and aliases."""
        app = ExtendedTyper()

        @app.command(aliases=["char", "key"])
        def getchar():
            """Get a single character input."""
            char = app.getchar()
            app.echo(f"You pressed: {char}")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        result = cli_runner.invoke(app, ["getchar"], input="A\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: A" in clean_result

        result = cli_runner.invoke(app, ["char"], input="B\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: B" in clean_result

        result = cli_runner.invoke(app, ["key"], input="C\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: C" in clean_result

    def test_getchar_special_unicode(self, cli_runner, clean_output):
        """Test getchar working with special unicode characters."""
        app = ExtendedTyper()

        @app.command(aliases=["char", "key"])
        def getchar():
            """Get a single character input."""
            char = app.getchar()
            app.echo(f"You pressed: {char}")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        # Space
        result = cli_runner.invoke(app, ["getchar"], input=" \n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed:  " in clean_result

        # Emoji
        result = cli_runner.invoke(app, ["getchar"], input="😀\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: 😀" in clean_result

        # Unicode
        result = cli_runner.invoke(app, ["getchar"], input="ñ\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: ñ" in clean_result

        # Non-Latin characters
        result = cli_runner.invoke(app, ["getchar"], input="蛇\n")
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "You pressed: 蛇" in clean_result

    def test_launch_integration(self, cli_runner, clean_output):
        """Test launch working with commands and aliases."""
        app = ExtendedTyper()

        @app.command(aliases=["start", "run"])
        def launch():
            """Launch a process."""
            app.launch("http://example.com")
            app.echo("Launched!")

        @app.command()
        def dummy():
            """Dummy command."""
            pass

        with patch.object(ExtendedTyper, "launch") as mock_launch:
            result = cli_runner.invoke(app, ["launch"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Launched!" in clean_result

            result = cli_runner.invoke(app, ["start"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Launched!" in clean_result

            result = cli_runner.invoke(app, ["run"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Launched!" in clean_result

            assert mock_launch.call_count == 3

    def test_launch_filepath_and_empty(self, cli_runner, clean_output):
        """Test launch working with file paths and empty inputs."""
        app = ExtendedTyper()

        @app.command()
        def file():
            """Open a file path."""
            app.launch("/tmp/test.txt")
            app.echo("Opened file.")

        @app.command()
        def empty():
            """Launch an empty string."""
            app.launch("")
            app.echo("Launched empty string.")

        with patch.object(ExtendedTyper, "launch") as mock_launch:
            result = cli_runner.invoke(app, ["file"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Opened file." in clean_result

            result = cli_runner.invoke(app, ["empty"])
            clean_result = clean_output(result.output)

            assert result.exit_code == 0
            assert "Launched empty string." in clean_result

            assert mock_launch.call_count == 2
            mock_launch.assert_any_call("/tmp/test.txt")
            mock_launch.assert_any_call("")

    def test_run_integration(self, cli_runner, clean_output):
        """Test run working with commands and aliases."""
        app = ExtendedTyper()

        @app.command()
        def greet():
            """Greet the user."""
            app.echo("Hello!")

        @app.command("run", aliases=["execute", "start"])
        def run_alias():
            """Run a process."""
            app.echo("Process started.")

        result = cli_runner.invoke(app, ["greet"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Hello!" in clean_result

        result = cli_runner.invoke(app, ["execute"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Process started." in clean_result

        result = cli_runner.invoke(app, ["start"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Process started." in clean_result

    def test_run_command_raises(self, cli_runner):
        """Test run command raises an error."""
        app = ExtendedTyper()

        @app.command()
        def error():
            """Raise an error."""
            raise RuntimeError("An error occurred.")

        @app.command()
        def another_error():
            """Raise another error."""
            raise ValueError("Another error occurred.")

        result = cli_runner.invoke(app, ["error"])
        assert result.exit_code != 0

        result = cli_runner.invoke(app, ["another_error"])
        assert result.exit_code != 0
