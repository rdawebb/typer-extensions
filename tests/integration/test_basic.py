"""Integration tests for basic command invocation with aliases."""

import pytest

from typer_extensions import Context, ExtendedTyper


class TestBasicInvocation:
    """Tests for invoking commands via primary name and aliases."""

    @pytest.mark.parametrize("name", ["list", "ls", "l"])
    def test_invoke_command(self, cli, make_app, name) -> None:
        """Test invoking a command by its primary name and aliases."""
        assert "Listing items..." in cli(make_app(), name)

    @pytest.mark.parametrize("name", ["list", "ls"])
    def test_command_help(self, cli, make_app, name) -> None:
        """Test that command-specific help works by primary name and alias."""
        assert "List all items" in cli(make_app(), name, "--help")


class TestErrorHandling:
    """Tests for error handling with aliases."""

    def test_invalid_command_shows_error(self, cli, make_app) -> None:
        """Test that an invalid command shows an appropriate error."""
        assert "No such command" in cli(make_app(), "invalid", ok=False)

    def test_case_sensitivity_respected(self, cli, make_app) -> None:
        """Test that case sensitivity is respected when configured."""
        app = make_app(alias_case_sensitive=True)

        cli(app, "ls")
        cli(app, "LS", ok=False)

    def test_single_command_works_without_alias(self, cli) -> None:
        """Test that single-command apps work as expected (aliases not supported by Typer)."""
        app = ExtendedTyper()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        # Single command is default command as expected
        assert "Hello World" in cli(app, "World")

    @pytest.mark.parametrize("variant", ["ls", "LS", "Ls", "lS"])
    def test_case_insensitivity_works(self, cli, make_app, variant) -> None:
        """Test that case insensitivity works when configured."""
        app = make_app(alias_case_sensitive=False)

        assert "Listing items..." in cli(app, variant)


class TestTyperCompatibility:
    """Tests for compatibility with standard Typer features."""

    def test_mixed_commands_with_and_without_aliases(self, cli, make_app) -> None:
        """Test mixing aliased and non-aliased commands."""
        app = make_app()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        assert "Hello World" in cli(app, "hello", "World")
        assert "Listing items..." in cli(app, "ls")


class TestAliasedAppCallback:
    """Tests that aliased apps keep their callback and group settings."""

    def test_callback_option_reaches_callback(self, cli, make_app) -> None:
        """Test that a parameterised callback receives its option via an alias."""
        app = make_app()

        @app.callback()
        def main(verbose: bool = False):
            """Main callback."""
            print(f"verbose={verbose}")

        output = cli(app, "--verbose", "ls")

        assert "verbose=True" in output
        assert "Listing items..." in output

    def test_invoke_without_command_runs_callback(self, cli, make_app) -> None:
        """Test that invoke_without_command runs the callback with no subcommand."""
        app = make_app()

        @app.callback(invoke_without_command=True)
        def main(ctx: Context):
            """Main callback."""
            if ctx.invoked_subcommand is None:
                print("No subcommand")

        assert "No subcommand" in cli(app)

    def test_no_args_is_help_shows_help(self, cli, make_app) -> None:
        """Test that no_args_is_help prints help when called with no arguments."""
        output = cli(make_app(no_args_is_help=True), ok=False)

        assert "Usage:" in output
        assert "List all items." in output

    def test_add_help_option_false_disables_help(self, cli, make_app) -> None:
        """Test that add_help_option=False removes --help from an aliased app."""
        app = make_app(add_help_option=False)

        assert "No such option" in cli(app, "--help", ok=False)

    def test_hidden_and_deprecated_sub_app(self, cli, make_app) -> None:
        """Test that an aliased sub-app keeps its hidden and deprecated settings."""
        app = ExtendedTyper()
        app.add_typer(make_app(deprecated=True), name="visible")
        app.add_typer(make_app(hidden=True), name="secret")

        help_output = cli(app, "--help")

        assert "visible" in help_output
        assert "deprecated" in help_output.lower()
        assert "secret" not in help_output
        assert "Listing items..." in cli(app, "secret", "ls")
