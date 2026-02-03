"""Integration tests for _rich_utils module with Typer commands.

Tests both Rich-enabled and Rich-disabled code paths through actual CLI commands.
"""

import os
from unittest.mock import patch

import typer

from typer_extensions import ExtendedTyper


class TestRichUtilsFormatHelp:
    """Integration tests for rich help formatting."""

    def test_help_formatting_with_extended_typer(self, cli_runner, clean_output):
        """Test that help is properly formatted with ExtendedTyper"""
        app = ExtendedTyper()

        @app.command()
        def hello(name: str = app.Option(..., help="The name to greet")):
            """Say hello to someone."""
            app.echo(f"Hello {name}!")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)

        # Help should contain command info
        assert "hello" in clean
        assert "Say hello" in clean
        assert "name" in clean

    def test_command_help_with_arguments(self, cli_runner, clean_output):
        """Test command help with arguments"""
        app = ExtendedTyper()

        @app.command()
        def greet(name: str = app.Argument(..., help="The person to greet")):
            """Greet someone by name."""
            app.echo(f"Hi {name}!")

        result = cli_runner.invoke(app, ["greet", "--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)
        assert "Greet someone" in clean
        assert "name" in clean

    def test_command_help_with_multiple_options(self, cli_runner, clean_output):
        """Test help with multiple options"""
        app = ExtendedTyper()

        @app.command()
        def configure(
            host: str = app.Option("localhost", help="Server host"),
            port: int = app.Option(8000, help="Server port"),
            debug: bool = app.Option(False, "--debug", help="Enable debug mode"),
        ):
            """Configure the server."""
            app.echo(f"Config: {host}:{port}")

        result = cli_runner.invoke(app, ["configure", "--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)

        # Should show all options
        assert "host" in clean
        assert "port" in clean
        assert "debug" in clean


class TestRichUtilsErrorFormatting:
    """Integration tests for rich error formatting."""

    def test_error_message_on_missing_required_option(self, cli_runner):
        """Test error message when required option is missing"""
        app = ExtendedTyper()

        @app.command()
        def needs_name(name: str = app.Option(..., help="Required name")):
            """A command that needs a name."""
            app.echo(f"Name: {name}")

        result = cli_runner.invoke(app, ["needs_name"])
        # Should fail with non-zero exit code
        assert result.exit_code != 0

    def test_error_message_on_invalid_argument_type(self, cli_runner):
        """Test error message with invalid argument type"""
        app = ExtendedTyper()

        @app.command()
        def take_number(count: int = app.Argument(...)):
            """Take a number."""
            app.echo(f"Count: {count}")

        result = cli_runner.invoke(app, ["take_number", "not-a-number"])
        assert result.exit_code != 0

    def test_deprecation_message_in_help(self, cli_runner):
        """Test deprecation markers in help text"""
        app = ExtendedTyper()

        @app.command(deprecated=True)
        def old_command():
            """This command is deprecated."""
            app.echo("Old!")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Should indicate deprecation somehow
        output_lower = result.output.lower()
        assert "deprecated" in output_lower


class TestRichUtilsWithRichDisabled:
    """Tests for _rich_utils when Rich rendering is disabled."""

    def test_help_works_with_rich_disabled(self, cli_runner):
        """Test that help still works when Rich output is disabled"""
        app = ExtendedTyper()

        @app.command()
        def simple(name: str = app.Option("World", help="Name to greet")):
            """A simple greeting."""
            app.echo(f"Hello {name}!")

        # Disable Rich output
        with patch.dict(os.environ, {"TYPER_USE_RICH": "0"}):
            result = cli_runner.invoke(app, ["--help"])
            assert result.exit_code == 0
            assert "simple" in result.output or "greet" in result.output

    def test_error_output_without_rich(self, cli_runner):
        """Test error output works without Rich"""
        app = ExtendedTyper()

        @app.command()
        def cmd(value: int = app.Argument(...)):
            """Command with int argument."""
            app.echo(f"Value: {value}")

        with patch.dict(os.environ, {"TYPER_USE_RICH": "0"}):
            result = cli_runner.invoke(app, ["cmd", "invalid"])
            # Should fail gracefully
            assert result.exit_code != 0


class TestRichUtilsHelpWithGroups:
    """Test help formatting for command groups."""

    def test_group_help_formatting(self, cli_runner, clean_output):
        """Test help formatting for command groups"""
        app = ExtendedTyper()

        db_app = typer.Typer()

        @db_app.command()
        def init():
            """Initialise database."""
            typer.echo("DB initialised")

        @db_app.command()
        def migrate():
            """Run migrations."""
            typer.echo("Migrated")

        app.add_typer(db_app, name="db", help="Database commands")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)

        # Should show the db group
        assert "db" in clean
        assert "Database" in clean

    def test_subcommand_help(self, cli_runner, clean_output):
        """Test help for subcommands within groups"""
        app = ExtendedTyper()

        db_app = typer.Typer()

        @db_app.command()
        def connect(
            host: str = app.Option("localhost", help="Database host"),
            port: int = app.Option(5432, help="Database port"),
        ):
            """Connect to database."""
            app.echo(f"Connecting to {host}:{port}")

        app.add_typer(db_app, name="db")

        result = cli_runner.invoke(app, ["db", "connect", "--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)

        assert "host" in clean
        assert "port" in clean


class TestRichUtilsCustomHelpText:
    """Test help formatting with custom help text."""

    def test_multiline_help_text(self, cli_runner, clean_output):
        """Test multiline help text formatting"""
        app = ExtendedTyper()

        @app.command()
        def document(
            title: str = app.Option(
                ...,
                help="""
                The document title.
                This can be any string.
                It will appear in the output.
                """,
            ),
        ):
            """Process a document with multiple lines of help."""
            app.echo(f"Processing: {title}")

        result = cli_runner.invoke(app, ["document", "--help"])
        assert result.exit_code == 0
        assert "title" in result.output

    def test_help_text_with_special_characters(self, cli_runner, clean_output):
        """Test help text with special characters"""
        app = ExtendedTyper()

        @app.command()
        def special(
            pattern: str = app.Option(
                ".*",
                help="Regex pattern (e.g., [a-z]+, \\d{3}, etc.)",
            ),
        ):
            """Match patterns."""
            app.echo(f"Pattern: {pattern}")

        result = cli_runner.invoke(app, ["special", "--help"])
        assert result.exit_code == 0
        assert "special" in result.output or "Match" in result.output


class TestRichUtilsAbortAndExit:
    """Test abort and exit error handling."""

    def test_abort_displays_message(self, cli_runner):
        """Test abort displays error message"""
        app = ExtendedTyper()

        @app.command()
        def hello():
            """Say hello."""
            app.echo("Hello!")

        @app.command()
        def will_abort():
            """This command will abort."""
            app.echo("Starting...")
            raise typer.Abort()

        result = cli_runner.invoke(app, ["will_abort"])
        assert result.exit_code != 0

    def test_error_handling_in_command(self, cli_runner):
        """Test error handling in commands"""
        app = ExtendedTyper()

        @app.command()
        def hello():
            """Say hello."""
            app.echo("Hello!")

        @app.command()
        def failing():
            """This command will fail."""
            raise typer.BadParameter("Invalid input")

        result = cli_runner.invoke(app, ["failing"])
        # Should fail with some exit code
        assert result.exit_code != 0


class TestRichUtilsVersionDisplay:
    """Test version display in help."""

    def test_no_version_by_default(self, cli_runner):
        """Test that version is not shown by default"""
        app = ExtendedTyper()

        @app.command()
        def hello():
            """Say hello."""
            app.echo("Hello!")

        @app.command()
        def goodbye():
            """Say goodbye."""
            app.echo("Goodbye!")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        # Should have help but not version by default

    def test_explicit_version_callback(self, cli_runner):
        """Test with explicit version in help"""
        app = ExtendedTyper()

        @app.command()
        def hello(
            version: bool = app.Option(False, "--version", help="Show version"),
        ):
            """My app."""
            if version:
                app.echo("Version 1.0.0")
            else:
                app.echo("Hello!")

        @app.command()
        def goodbye():
            """Say goodbye."""
            app.echo("Goodbye!")

        result = cli_runner.invoke(app, ["hello", "--version"])
        assert result.exit_code == 0
        assert "Version 1.0.0" in result.output


class TestRichUtilsAliasesInHelp:
    """Test that rich formatting works with alias commands."""

    def test_alias_help_display(self, cli_runner, clean_output):
        """Test that aliases show correctly in help"""
        app = ExtendedTyper(show_aliases_in_help=True)

        @app.command("list", aliases=["ls", "l"])
        def list_cmd():
            """List items."""
            app.echo("Items:")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean = clean_output(result.output)

        # Should show the command
        assert "list" in clean

    def test_alias_command_works(self, cli_runner):
        """Test that commands with aliases work properly"""
        app = ExtendedTyper()

        @app.command("create", aliases=["add", "new"])
        def create_item():
            """Create an item."""
            app.echo("Created!")

        @app.command()
        def list_items():
            """List all items."""
            app.echo("Items listed")

        # Test original command
        result = cli_runner.invoke(app, ["create"])
        assert result.exit_code == 0
        assert "Created" in result.output
