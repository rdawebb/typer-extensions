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
            pass

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
            pass

        def delete_item():
            """Delete an item from the system."""
            pass

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
            pass

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
