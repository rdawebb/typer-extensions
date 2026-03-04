"""Integration tests for basic command invocation with aliases."""


class TestBasicInvocation:
    """Tests for invoking commands via primary name and aliases."""

    def test_invoke_command_by_primary_name(self, app_with_commands, assert_success):
        """Test invoking command using primary name."""

        assert_success(app_with_commands, ["list"], "Listing items...")


class TestDecoratorSyntax:
    """Tests for command decorator syntax."""

    def test_invoke_bare_decorator_by_primary_and_alias(
        self, app, assert_success, assert_failure
    ):
        """Test invoking command decorated without parentheses by primary name and alias"""

        @app.command
        def hello():
            """Say hello."""
            print("Hello!")

        @app.command
        def goodbye():
            """Say goodbye."""
            print("Goodbye!")

        assert_success(app, ["hello"])
        # Should fail since no aliases were provided
        assert_failure(app, ["hi"], expected_exit_code=2, expected=["Usage:"])

    def test_decorator_with_typer_context(self, app, assert_success):
        """Test decorated command with Typer context"""
        from typer_extensions import Context

        @app.command("info", aliases=["i"])
        def show_info(ctx: Context):
            """Show info."""
            print(f"Command: {ctx.info_name}")
            print(f"Parent: {ctx.parent.info_name if ctx.parent else 'None'}")

        @app.command("child", aliases=["c"])
        def show_child_info(ctx: Context):
            """Show child info."""
            print(f"Child Command: {ctx.info_name}")
            print(f"Parent: {ctx.parent.info_name if ctx.parent else 'None'}")

        # Should show command and parent information
        assert_success(app, ["info"], "Command:")

    def test_both_decorator_types_work(self, app, assert_success):
        """Test using both decorator styles in same app."""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            print("Listing...")

        @app.command()
        def hello():
            """Say hello."""
            print("Hello!")

        # Both should work
        assert_success(app, ["list"], ["Listing..."])
        assert_success(app, ["ls"], ["Listing..."])

        assert_success(app, ["hello"], ["Hello!"])

    def test_help_shows_both_command_types(self, app, assert_success):
        """Test that help shows both types of commands"""

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command()
        def hello():
            """Say hello."""
            pass

        # Should show primary commands and descriptions
        assert_success(app, ["--help"], ["list", "hello", "List items", "Say hello"])


class TestHelpText:
    """Tests for help text display with aliases."""

    def test_help_shows_primary_command(self, app, assert_success, unreg_commands):
        """Test that help text shows primary command."""

        list_items, _ = unreg_commands

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])

        # Should show primary command and description
        assert_success(app, ["--help"], ["list", "List all items"])

    def test_command_help_works_via_alias(self, app, assert_success, unreg_commands):
        """Test that command-specific help works via alias."""

        list_items, delete_item = unreg_commands

        app._register_command_with_aliases(list_items, "list", aliases=["ls"])
        app._register_command_with_aliases(delete_item, "delete", aliases=["rm"])

        # Should both show same command and description
        assert_success(app, ["list", "--help"], ["List all items"])
        assert_success(app, ["ls", "--help"], ["List all items"])


class TestErrorHandling:
    """Tests for error handling with aliases."""

    def test_invalid_command_shows_error(self, app_with_commands, assert_failure):
        """Test that invalid command shows appropriate error."""

        assert_failure(app_with_commands, ["invalid"], expected_exit_code=2)

    def test_single_command_works_without_alias(self, app, assert_success):
        """Test that single-command apps work as expected (aliases not supported by Typer)."""

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        # Single command is default command as expected
        assert_success(app, ["World"], "Hello World")

    def test_case_insensitivity_works(
        self, app_case_insensitive, assert_success, unreg_commands
    ):
        """Test that case insensitivity works when configured."""

        list_items, delete_items = unreg_commands

        app_case_insensitive._register_command_with_aliases(
            list_items, "list", aliases=["ls"]
        )
        app_case_insensitive._register_command_with_aliases(
            delete_items, "delete", aliases=["rm"]
        )

        # Should match all case variations
        for variant in ["ls", "LS", "Ls", "lS"]:
            assert_success(app_case_insensitive, [variant], "Listing items...")


class TestTyperCompatibility:
    """Tests for compatibility with standard Typer features."""

    def test_standard_typer_command_still_works(self, assert_success):
        """Test that standard Typer commands work without aliases."""
        import typer

        app = typer.Typer()

        @app.command()
        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        @app.command()
        def goodbye(name: str):
            """Say goodbye."""
            print(f"Goodbye {name}")

        assert_success(app, ["hello", "World"], "Hello World")

    def test_mixed_commands_with_and_without_aliases(
        self, app_with_aliases, assert_success
    ):
        """Test mixing aliased and non-aliased commands."""

        def hello(name: str):
            """Say hello."""
            print(f"Hello {name}")

        app_with_aliases._register_command_with_aliases(hello, "hello")

        assert_success(app_with_aliases, ["hello", "World"], "Hello World")
        assert_success(app_with_aliases, ["ls"], "Listing items...")

    def test_typer_context_works(self, app, assert_success):
        """Test that Typer context still works correctly."""
        from typer_extensions import Context

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

        assert_success(app, ["list"], "Command: list")
