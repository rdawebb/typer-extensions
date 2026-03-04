"""Integration tests for _rich_utils module with Typer commands.

Tests both Rich-enabled and Rich-disabled code paths through actual CLI commands.
"""

import os
from unittest.mock import patch


class TestRichUtilsFormatHelp:
    """Integration tests for rich help formatting."""

    def test_help_formatting_with_extended_typer(self, app, assert_success):
        """Test that help is properly formatted with ExtendedTyper"""

        @app.command()
        def hello(name: str = app.Option(..., help="The name to greet")):
            """Say hello to someone."""
            app.echo(f"Hello {name}!")

        # Help should contain command info
        assert_success(app, ["--help"], ["hello", "Say hello", "The name to greet"])

    def test_command_help_with_arguments(self, app, assert_success):
        """Test command help with arguments"""

        @app.command()
        def greet(name: str = app.Argument(..., help="The person to greet")):
            """Greet someone by name."""
            app.echo(f"Hi {name}!")

        assert_success(app, ["greet", "--help"], ["Greet someone", "name"])

    def test_command_help_with_multiple_options(self, app, assert_success):
        """Test help with multiple options"""

        @app.command()
        def configure(
            host: str = app.Option("localhost", help="Server host"),
            port: int = app.Option(8000, help="Server port"),
            debug: bool = app.Option(False, "--debug", help="Enable debug mode"),
        ):
            """Configure the server."""
            app.echo(f"Config: {host}:{port}")

        # Should show all options
        assert_success(
            app,
            ["configure", "--help"],
            ["Configure the server", "host", "port", "debug"],
        )


class TestRichUtilsErrorFormatting:
    """Integration tests for rich error formatting."""

    def test_error_message_on_missing_required_option(self, app, assert_failure):
        """Test error message when required option is missing"""

        @app.command()
        def needs_name(name: str = app.Option(..., help="Required name")):
            """A command that needs a name."""
            app.echo(f"Name: {name}")

        assert_failure(
            app,
            ["needs_name"],
            expected_exit_code=2,
            expected=["Missing option", "name"],
        )

    def test_error_message_on_invalid_argument_type(self, app, assert_failure):
        """Test error message with invalid argument type"""

        @app.command()
        def take_number(count: int = app.Argument(...)):
            """Take a number."""
            app.echo(f"Count: {count}")

        assert_failure(
            app,
            ["take_number", "not-a-number"],
            expected_exit_code=2,
            expected=["Invalid value", "COUNT"],
        )

    def test_deprecation_message_in_help(self, app, clean_output, assert_success):
        """Test deprecation markers in help text"""

        @app.command(deprecated=True)
        def old_command():
            """This command is deprecated."""
            app.echo("Old!")

        # Should indicate deprecation
        assert_success(app, ["--help"], ["old_command", "deprecated"])


class TestRichUtilsWithRichDisabled:
    """Tests for _rich_utils when Rich rendering is disabled."""

    def test_help_works_with_rich_disabled(self, app, assert_success):
        """Test that help still works when Rich output is disabled"""

        @app.command()
        def simple(name: str = app.Option("World", help="Name to greet")):
            """A simple greeting."""
            app.echo(f"Hello {name}!")

        # Disable Rich output
        with patch.dict(os.environ, {"TYPER_USE_RICH": "0"}):
            assert_success(app, ["--help"], ["simple", "Name to greet"])

    def test_error_output_without_rich(self, app, assert_failure):
        """Test error output works without Rich"""

        @app.command()
        def cmd(value: int = app.Argument(...)):
            """Command with int argument."""
            app.echo(f"Value: {value}")

        with patch.dict(os.environ, {"TYPER_USE_RICH": "0"}):
            assert_failure(
                app,
                ["cmd", "invalid"],
                expected_exit_code=2,
                expected=["Invalid value", "VALUE"],
            )


class TestRichUtilsHelpWithGroups:
    """Test help formatting for command groups."""

    def test_group_help_formatting(self, app, assert_success):
        """Test help formatting for command groups"""
        from typer_extensions import ExtendedTyper

        db_app = ExtendedTyper()

        @db_app.command()
        def init():
            """Initialise database."""
            app.echo("DB initialised")

        @db_app.command()
        def migrate():
            """Run migrations."""
            app.echo("Migrated")

        app.add_typer(db_app, name="db", help="Database commands")

        # Should show the db group
        assert_success(app, ["--help"], ["db", "Database commands"])

    def test_subcommand_help(self, app, assert_success):
        """Test help for subcommands within groups"""
        from typer_extensions import ExtendedTyper

        db_app = ExtendedTyper()

        @db_app.command()
        def connect(
            host: str = app.Option("localhost", help="Database host"),
            port: int = app.Option(5432, help="Database port"),
        ):
            """Connect to database."""
            app.echo(f"Connecting to {host}:{port}")

        app.add_typer(db_app, name="db")

        assert_success(
            app, ["db", "connect", "--help"], ["Connect to database", "host", "port"]
        )


class TestRichUtilsCustomHelpText:
    """Test help formatting with custom help text."""

    def test_multiline_help_text(self, app, assert_success):
        """Test multiline help text formatting"""

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

        assert_success(
            app, ["document", "--help"], ["Process a document", "The document title"]
        )

    def test_help_text_with_special_characters(self, app, assert_success):
        """Test help text with special characters"""

        @app.command()
        def special(
            pattern: str = app.Option(
                ".*",
                help="Regex pattern (e.g., [a-z]+, \\d{3}, etc.)",
            ),
        ):
            """Match patterns."""
            app.echo(f"Pattern: {pattern}")

        assert_success(app, ["special", "--help"], ["Match patterns", "Regex"])


class TestRichUtilsAbortAndExit:
    """Test abort and exit error handling."""

    def test_abort_displays_message(self, app_with_commands, assert_failure):
        """Test abort displays error message"""

        @app_with_commands.command()
        def will_abort():
            """This command will abort."""
            app_with_commands.echo("Starting...")
            raise app_with_commands.Abort()

        assert_failure(
            app_with_commands,
            ["will_abort"],
            expected_exit_code=1,
            expected=["Starting"],
        )

    def test_error_handling_in_command(self, app_with_commands, assert_failure):
        """Test error handling in commands"""

        @app_with_commands.command()
        def failing():
            """This command will fail."""
            raise app_with_commands.BadParameter("Invalid input")

        assert_failure(
            app_with_commands,
            ["failing"],
            expected_exit_code=1,
        )


class TestRichUtilsVersionDisplay:
    """Test version display in help."""

    def test_no_version_by_default(self, app_with_commands, assert_success):
        """Test that version is not shown by default"""

        # Should not show version by default
        assert_success(
            app_with_commands,
            ["--help"],
            ["list", "delete"],
            not_expected=["Version"],
        )

    def test_explicit_version_callback(self, app_with_commands, assert_success):
        """Test with explicit version in help"""

        @app_with_commands.command()
        def my_app(
            version: bool = app_with_commands.Option(
                False, "--version", help="Show version"
            ),
        ):
            """My app."""
            if version:
                app_with_commands.echo("Version 1.0.0")
            else:
                app_with_commands.echo("Hello!")

        assert_success(app_with_commands, ["my_app", "--version"], ["Version 1.0.0"])
