"""Integration tests for basic command invocation with aliases."""

from typer_extensions import Context, ExtendedTyper


class TestBasicInvocation:
    """Tests for invoking commands via primary name and aliases."""

    def test_invoke_command_by_primary_name(self, cli_runner):
        """Test invoking command using primary name."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List all items."""
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            """Delete all items."""
            print("Deleting items...")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output


class TestHelpText:
    """Tests for help text display with aliases."""

    def test_help_shows_primary_command(self, cli_runner, clean_output):
        """Test that help text shows primary command."""
        app = ExtendedTyper()

        def list_items():
            """List all items in the system."""

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show primary command and description
        assert "list" in clean_result
        assert "List all items in the system" in clean_result

    def test_command_help_works_via_alias(self, cli_runner, clean_output):
        """Test that command-specific help works via alias."""
        app = ExtendedTyper()

        def list_items():
            """List all items in the system."""

        def delete_item():
            """Delete an item from the system."""

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_item, "delete", aliases=["rm"])

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command and description
        assert "List all items" in clean_result

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command and description
        assert "List all items" in clean_result


class TestErrorHandling:
    """Tests for error handling with aliases."""

    def test_invalid_command_shows_error(self, cli_runner):
        """Test that invalid command shows appropriate error."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items():
            """List items."""

        result = cli_runner.invoke(app, ["invalid"])
        assert result.exit_code != 0
        # Click shows "No such command" error

    def test_case_sensitivity_respected(self, cli_runner):
        """Test that case sensitivity is respected when configured."""
        app = ExtendedTyper(alias_case_sensitive=True)

        def list_items():
            """List items."""
            print("Listing items...")

        def delete_items():
            """Delete items."""
            print("Deleting items...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["rm"])

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["LS"])
        assert result.exit_code != 0

    def test_single_command_works_without_alias(self, cli_runner):
        """Test that single-command apps work as expected (aliases not supported by Typer)."""
        app = ExtendedTyper()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        # Single command is default command as expected
        result = cli_runner.invoke(app, ["World"])
        assert result.exit_code == 0
        assert "Hello World" in result.output

    def test_case_insensitivity_works(self, cli_runner):
        """Test that case insensitivity works when configured."""
        app = ExtendedTyper(alias_case_sensitive=False)

        def list_items():
            """List items."""
            print("Listing items...")

        def delete_items():
            """Delete items."""
            print("Deleting items...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["rm"])

        for variant in ["ls", "LS", "Ls", "lS"]:
            result = cli_runner.invoke(app, [variant])
            assert result.exit_code == 0
            assert "Listing items..." in result.output


class TestTyperCompatibility:
    """Tests for compatibility with standard Typer features."""

    def test_standard_typer_command_still_works(self, cli_runner):
        """Test that standard Typer commands work without aliases."""
        app = ExtendedTyper()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        @app.command()
        def goodbye(name: str):
            """Say goodbye."""
            print(f"Goodbye {name}")

        result = cli_runner.invoke(app, ["hello", "World"])
        assert result.exit_code == 0
        assert "Hello World" in result.output

    def test_mixed_commands_with_and_without_aliases(self, cli_runner):
        """Test mixing aliased and non-aliased commands."""
        app = ExtendedTyper()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        def list_items():
            """List items."""
            print("Listing...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["hello", "World"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

    def test_typer_context_works(self, cli_runner, clean_output):
        """Test that Typer context still works correctly."""
        app = ExtendedTyper()

        @app.command("list")
        def list_items(ctx: Context):
            """List items."""
            assert ctx is not None
            print(f"Command: {ctx.info_name}")

        @app.command("delete")
        def delete_items(ctx: Context):
            """Delete items."""
            assert ctx is not None
            print(f"Command: {ctx.info_name}")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command name as default Typer behaviour
        assert "Command:" in clean_result


class TestAliasedAppCallback:
    """Tests that aliased apps keep their callback and group settings."""

    def test_callback_option_reaches_callback(self, cli_runner):
        """Test that a parameterised callback receives its option via an alias."""
        app = ExtendedTyper()

        @app.callback()
        def main(verbose: bool = False):
            """Main callback."""
            print(f"verbose={verbose}")

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items."""
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            """Delete all items."""

        result = cli_runner.invoke(app, ["--verbose", "ls"])
        assert result.exit_code == 0, result.output
        assert "verbose=True" in result.output
        assert "Listing items..." in result.output

    def test_invoke_without_command_runs_callback(self, cli_runner):
        """Test that invoke_without_command runs the callback with no subcommand."""
        app = ExtendedTyper()

        @app.callback(invoke_without_command=True)
        def main(ctx: Context):
            """Main callback."""
            if ctx.invoked_subcommand is None:
                print("No subcommand")

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items."""

        @app.command("delete")
        def delete_items():
            """Delete all items."""

        result = cli_runner.invoke(app, [])
        assert result.exit_code == 0, result.output
        assert "No subcommand" in result.output

    def test_no_args_is_help_shows_help(self, cli_runner, clean_output):
        """Test that no_args_is_help prints help when called with no arguments."""
        app = ExtendedTyper(no_args_is_help=True)

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items."""

        @app.command("delete")
        def delete_items():
            """Delete all items."""

        result = cli_runner.invoke(app, [])
        assert "Usage:" in clean_output(result.output)
        assert "List all items." in clean_output(result.output)

    def test_add_help_option_false_disables_help(self, cli_runner):
        """Test that add_help_option=False removes --help from an aliased app."""
        app = ExtendedTyper(add_help_option=False)

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items."""

        @app.command("delete")
        def delete_items():
            """Delete all items."""

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code != 0
        assert "No such option" in result.output

    def test_hidden_and_deprecated_sub_app(self, cli_runner, clean_output):
        """Test that an aliased sub-app keeps its hidden and deprecated settings."""
        app = ExtendedTyper()
        visible = ExtendedTyper(deprecated=True)
        secret = ExtendedTyper(hidden=True)

        for sub in (visible, secret):

            @sub.command("list", aliases=["ls"])
            def list_items():
                """List all items."""
                print("Listing items...")

            @sub.command("delete")
            def delete_items():
                """Delete all items."""

        app.add_typer(visible, name="visible")
        app.add_typer(secret, name="secret")

        help_output = clean_output(cli_runner.invoke(app, ["--help"]).output)
        assert "visible" in help_output
        assert "deprecated" in help_output.lower()
        assert "secret" not in help_output

        result = cli_runner.invoke(app, ["secret", "ls"])
        assert result.exit_code == 0, result.output
        assert "Listing items..." in result.output
