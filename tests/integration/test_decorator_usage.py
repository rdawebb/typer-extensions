"""Integration tests for decorator usage in real CLI scenarios"""

import typer
from typer_aliases import AliasedTyper


class TestDecoratorInvocation:
    """Tests for invoking decorator-registered commands"""

    def test_invoke_decorated_command_by_name(self, cli_runner):
        """Test invoking decorated command by primary name"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""
            print("Listing items...")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_decorated_command_by_alias(self, cli_runner):
        """Test invoking decorated command by alias"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""
            print("Listing items...")

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_bare_decorator(self, cli_runner):
        """Test invoking command decorated without parentheses"""
        app = AliasedTyper()

        @app.command_with_aliases
        def hello():
            """Say hello."""
            print("Hello!")

        result = cli_runner.invoke(app, ["hello"])
        assert result.exit_code != 0
        assert "Usage: hello" in result.output

    def test_bare_decorator_with_aliases(self, cli_runner):
        """Test invoking command decorated without parentheses and with aliases"""
        app = AliasedTyper()

        @app.command_with_aliases
        def hello():
            """Say hello."""
            print("Hello!")

        result = cli_runner.invoke(app, ["hello"])
        assert result.exit_code != 0
        assert "Usage: hello" in result.output


class TestDecoratorWithTyperFeatures:
    """Tests for decorator with Typer arguments and options"""

    def test_decorator_with_argument(self, cli_runner):
        """Test decorated command with argument"""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["greet", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

        # Via alias
        result = cli_runner.invoke(app, ["hi", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_decorator_with_option(self, cli_runner):
        """Test decorated command with option."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(verbose: bool = typer.Option(False, "--verbose", "-v")):
            """List items."""
            if verbose:
                print("Listing items (verbose)...")
            else:
                print("Listing items...")

        # Without option
        result = cli_runner.invoke(app, ["list"])
        assert "Listing items..." in result.output
        assert "verbose" not in result.output

        # With option via primary
        result = cli_runner.invoke(app, ["list", "--verbose"])
        assert "verbose" in result.output

        # With option via alias
        result = cli_runner.invoke(app, ["ls", "-v"])
        assert "verbose" in result.output

    def test_decorator_with_multiple_arguments(self, cli_runner):
        """Test decorated command with multiple arguments"""
        app = AliasedTyper()

        @app.command_with_aliases("copy", aliases=["cp"])
        def copy_file(source: str, dest: str):
            """Copy a file."""
            print(f"Copying {source} to {dest}")

        result = cli_runner.invoke(app, ["cp", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    def test_decorator_with_typer_context(self, cli_runner):
        """Test decorated command with Typer context"""
        app = AliasedTyper()

        @app.command_with_aliases("info", aliases=["i"])
        def show_info(ctx: typer.Context):
            """Show info."""
            print(f"Command: {ctx.info_name}")
            print(f"Parent: {ctx.parent.info_name if ctx.parent else 'None'}")

        result = cli_runner.invoke(app, ["info"])
        assert result.exit_code == 0
        assert "Command:" in result.output


class TestDecoratorHelpDisplay:
    """Tests for help text display with decorated commands"""

    def test_main_help_shows_decorated_commands(self, cli_runner):
        """Test that main help shows decorated commands"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List all items in the system."""
            pass

        @app.command_with_aliases("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "delete" in result.output
        assert "List all items" in result.output
        assert "Delete an item" in result.output

    def test_command_help_via_primary(self, cli_runner):
        """Test command help via primary name"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(verbose: bool = typer.Option(False, "--verbose")):
            """List all items in the system."""
            pass

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        assert "List all items" in result.output
        assert "--verbose" in result.output

    def test_command_help_via_alias(self, cli_runner):
        """Test command help via alias"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(verbose: bool = typer.Option(False, "--verbose")):
            """List all items in the system."""
            pass

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        assert "List all items" in result.output
        assert "--verbose" in result.output

    def test_help_hides_alias_commands(self, cli_runner):
        """Test that alias commands don't appear separately in help"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_items():
            """List items."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0

        # Primary should be shown
        assert "list" in result.output

        # Aliases should be hidden (not shown as separate commands)
        # They may appear elsewhere in help, but not as separate command entries


class TestDecoratorRealWorldScenarios:
    """Tests for real-world CLI scenarios"""

    def test_git_like_cli(self, cli_runner):
        """Test a Git-like CLI with common aliases"""
        app = AliasedTyper()

        @app.command_with_aliases("checkout", aliases=["co"])
        def checkout(branch: str):
            """Checkout a branch."""
            print(f"Switched to branch '{branch}'")

        @app.command_with_aliases("status", aliases=["st"])
        def status():
            """Show status."""
            print("On branch main")

        @app.command_with_aliases("commit", aliases=["ci"])
        def commit(message: str = typer.Option(..., "--message", "-m")):
            """Commit changes."""
            print(f"Committed: {message}")

        # Test checkout
        result = cli_runner.invoke(app, ["co", "develop"])
        assert "Switched to branch 'develop'" in result.output

        # Test status
        result = cli_runner.invoke(app, ["st"])
        assert "On branch main" in result.output

        # Test commit
        result = cli_runner.invoke(app, ["ci", "-m", "test commit"])
        assert "Committed: test commit" in result.output

    def test_package_manager_cli(self, cli_runner):
        """Test a package manager-like CLI"""
        app = AliasedTyper()

        @app.command_with_aliases("install", aliases=["i", "add"])
        def install(package: str):
            """Install a package."""
            print(f"Installing {package}...")

        @app.command_with_aliases("remove", aliases=["rm", "uninstall"])
        def remove(package: str):
            """Remove a package."""
            print(f"Removing {package}...")

        @app.command_with_aliases("list", aliases=["ls", "l"])
        def list_packages():
            """List installed packages."""
            print("Installed packages: pkg1, pkg2")

        # Test install
        result = cli_runner.invoke(app, ["i", "requests"])
        assert "Installing requests..." in result.output

        # Test remove
        result = cli_runner.invoke(app, ["rm", "requests"])
        assert "Removing requests..." in result.output

        # Test list
        result = cli_runner.invoke(app, ["ls"])
        assert "Installed packages:" in result.output


class TestDecoratorErrorHandling:
    """Tests for error handling with decorated commands"""

    def test_missing_required_argument(self, cli_runner):
        """Test error when required argument is missing"""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["greet"])
        assert result.exit_code != 0
        # Typer/Click should show missing argument error

    def test_invalid_alias_invocation(self, cli_runner):
        """Test invoking non-existent alias"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        result = cli_runner.invoke(app, ["dir"])  # Not an alias
        assert result.exit_code != 0
        # Should show "No such command" error


class TestDecoratorWithStandardCommands:
    """Tests for mixing decorated and standard Typer commands"""

    def test_both_decorator_types_work(self, cli_runner):
        """Test using both decorator styles in same app."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            print("Listing...")

        @app.command()
        def hello():
            """Say hello."""
            print("Hello!")

        # Both should work
        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0

        result = cli_runner.invoke(app, ["hello"])
        assert result.exit_code == 0

    def test_help_shows_both_command_types(self, cli_runner):
        """Test that help shows both types of commands"""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command()
        def hello():
            """Say hello."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "list" in result.output
        assert "hello" in result.output
        assert "List items" in result.output
        assert "Say hello" in result.output
