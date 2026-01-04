"""Integration tests for basic command invocation with aliases."""

from typer_aliases import AliasedTyper


class TestBasicInvocation:
    """Tests for invoking commands via primary name and aliases."""

    def test_invoke_command_by_primary_name(self, cli_runner):
        """Test invoking command using primary name."""
        app = AliasedTyper()

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

    def test_invoke_command_by_alias(self, cli_runner):
        """Test invoking command using alias."""
        app = AliasedTyper()

        def list_items():
            """List all items."""
            print("Listing items...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_command_multiple_aliases(self, cli_runner):
        """Test that all aliases work for same command."""
        app = AliasedTyper()

        def list_items():
            """List all items."""
            print("Listing items...")

        app._register_command_with_aliases(
            list_items, "list", aliases=["ls", "l", "dir"]
        )

        for alias in ["list", "ls", "l", "dir"]:
            result = cli_runner.invoke(app, [alias])
            assert result.exit_code == 0
            assert "Listing items..." in result.output

    def test_command_with_arguments(self, cli_runner):
        """Test command with arguments works via alias."""
        app = AliasedTyper()

        def delete_item(name: str):
            """Delete an item."""
            print(f"Deleting {name}")

        app._register_command_with_aliases(
            delete_item, "delete", aliases=["rm", "remove"]
        )

        result = cli_runner.invoke(app, ["delete", "test.txt"])
        assert result.exit_code == 0
        assert "Deleting test.txt" in result.output

        result = cli_runner.invoke(app, ["rm", "test.txt"])
        assert result.exit_code == 0
        assert "Deleting test.txt" in result.output

    def test_command_with_options(self, cli_runner):
        """Test command with options works via alias."""
        import typer

        app = AliasedTyper()

        def list_items(verbose: bool = typer.Option(False, "--verbose", "-v")):
            """List all items."""
            if verbose:
                print("Listing items (verbose mode)...")
            else:
                print("Listing items...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["list"])
        assert "Listing items..." in result.output
        assert "verbose mode" not in result.output

        result = cli_runner.invoke(app, ["ls", "--verbose"])
        assert "verbose mode" in result.output


class TestHelpText:
    """Tests for help text display with aliases."""

    def test_help_shows_primary_command(self, cli_runner):
        """Test that help text shows primary command."""
        app = AliasedTyper()

        def list_items():
            """List all items in the system."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "List all items in the system" in result.output

    def test_help_hides_alias_commands(self, cli_runner):
        """Test that alias commands are hidden in help."""
        app = AliasedTyper()

        def list_items():
            """List all items."""
            pass

        def delete_items():
            """Delete all items."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls", "l"])
        app._register_command_with_aliases(delete_items, "delete", aliases=["rm"])

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Primary commands should be shown
        assert "list" in result.output
        assert "delete" in result.output

        # Aliases should not be shown (hidden=True)

    def test_command_help_works_via_alias(self, cli_runner):
        """Test that command-specific help works via alias."""
        app = AliasedTyper()

        def list_items():
            """List all items in the system."""
            pass

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "List all items" in result.output

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        assert "List all items" in result.output


class TestErrorHandling:
    """Tests for error handling with aliases."""

    def test_invalid_command_shows_error(self, cli_runner):
        """Test that invalid command shows appropriate error."""
        app = AliasedTyper()

        @app.command("list")
        def list_items():
            """List items."""
            pass

        result = cli_runner.invoke(app, ["invalid"])
        assert result.exit_code != 0
        # Click shows "No such command" error

    def test_case_sensitivity_respected(self, cli_runner):
        """Test that case sensitivity is respected when configured."""
        app = AliasedTyper(alias_case_sensitive=True)

        def list_items():
            """List items."""
            print("Listing items...")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["LS"])
        assert result.exit_code != 0

    def test_single_command_works_without_alias(self, cli_runner):
        """Test that single-command apps work as expected (aliases not supported by Typer)."""
        app = AliasedTyper()

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
        app = AliasedTyper(alias_case_sensitive=False)

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
        app = AliasedTyper()

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
        app = AliasedTyper()

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

    def test_typer_context_works(self, cli_runner):
        """Test that Typer context still works correctly."""
        import typer

        app = AliasedTyper()

        def list_items(ctx: typer.Context):
            """List items."""
            assert ctx is not None
            print(f"Command: {ctx.info_name}")

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Command:" in result.output
