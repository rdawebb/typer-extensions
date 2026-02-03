"""Integration tests for decorator usage in real CLI scenarios"""

from typer_extensions import ExtendedTyper, Context


class TestDecoratorInvocation:
    """Tests for invoking decorator-registered commands"""

    def test_invoke_decorated_command_by_name(self, cli_runner):
        """Test invoking decorated command by primary name"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""
            print("Listing items...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_decorated_command_by_alias(self, cli_runner):
        """Test invoking decorated command by alias"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List all items."""
            print("Listing items...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

        result = cli_runner.invoke(app, ["l"])
        assert result.exit_code == 0
        assert "Listing items..." in result.output

    def test_invoke_bare_decorator(self, cli_runner, clean_output):
        """Test invoking command decorated without parentheses"""
        app = ExtendedTyper()

        @app.command
        def hello():
            """Say hello."""
            print("Hello!")

        @app.command
        def goodbye():
            """Say goodbye."""
            print("Goodbye!")

        result = cli_runner.invoke(app, ["hello"])
        assert result.exit_code == 0

    def test_bare_decorator_with_aliases(self, cli_runner, clean_output):
        """Test invoking command decorated without parentheses and with aliases"""
        app = ExtendedTyper()

        @app.command
        def hello():
            """Say hello."""
            print("Hello!")

        @app.command
        def goodbye():
            """Say goodbye."""
            print("Goodbye!")

        # Invoke via alias should fail since no aliases were provided
        result = cli_runner.invoke(app, ["hi"])
        assert result.exit_code != 0
        clean_result = clean_output(result.output)

        # Should show usage information
        assert "Usage:" in clean_result


class TestDecoratorWithTyperFeatures:
    """Tests for decorator with Typer arguments and options"""

    def test_decorator_with_argument(self, cli_runner):
        """Test decorated command with argument"""
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command("goodbye", aliases=["bye", "farewell"])
        def goodbye(name: str):
            """Say goodbye."""
            print(f"Goodbye, {name}!")

        result = cli_runner.invoke(app, ["greet", "World"])
        assert result.exit_code == 0
        assert "Hello, World!" in result.output

        # Via alias
        result = cli_runner.invoke(app, ["hi", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_decorator_with_option(self, cli_runner):
        """Test decorated command with option."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items(verbose: bool = app.Option(False, "--verbose", "-v")):
            """List items."""
            if verbose:
                print("Listing items (verbose)...")
            else:
                print("Listing items...")

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

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
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(source: str, dest: str):
            """Copy a file."""
            print(f"Copying {source} to {dest}")

        @app.command("move", aliases=["mv"])
        def move_file(source: str, dest: str):
            """Move a file."""
            print(f"Moving {source} to {dest}")

        result = cli_runner.invoke(app, ["cp", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    def test_decorator_with_typer_context(self, cli_runner, clean_output):
        """Test decorated command with Typer context"""
        app = ExtendedTyper()

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

        result = cli_runner.invoke(app, ["info"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command and parent information
        assert "Command:" in clean_result


class TestDecoratorHelpDisplay:
    """Tests for help text display with decorated commands"""

    def test_main_help_shows_decorated_commands(self, cli_runner, clean_output):
        """Test that main help shows decorated commands"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List all items in the system."""
            pass

        @app.command("delete", aliases=["rm"])
        def delete_item():
            """Delete an item."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show primary commands and descriptions
        assert "list" in clean_result
        assert "delete" in clean_result
        assert "List all items" in clean_result
        assert "Delete an item" in clean_result

    def test_command_help_via_primary(self, cli_runner, clean_output):
        """Test command help via primary name"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items(verbose: bool = app.Option(False, "--verbose")):
            """List all items in the system."""
            pass

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)
        assert "List all items" in clean_result
        assert "--verbose" in clean_result

    def test_command_help_via_alias(self, cli_runner, clean_output):
        """Test command help via alias"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items(verbose: bool = app.Option(False, "--verbose")):
            """List all items in the system."""
            pass

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show command and typer.Option
        assert "List all items" in clean_result
        assert "--verbose" in clean_result

    def test_help_shows_no_alias_commands(self, cli_runner, clean_output):
        """Test that alias commands don't appear separately in help"""
        import re

        app = ExtendedTyper()

        @app.command("list", aliases=["ls", "l"])
        def list_items():
            """List items."""
            pass

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Primaries should be shown
        assert "list" in clean_result
        assert "delete" in clean_result

        # Extract the commands section from the help output
        match = re.search(r"(?s)Commands:\n(.*?)(\n\n|\Z)", clean_result)
        commands_section = match.group(1) if match else ""

        # Check that aliases do not appear as separate commands
        for alias in ["ls", "l", "rm", "del"]:
            assert not re.search(rf"^\s*{alias}\s", commands_section, re.MULTILINE)


class TestDecoratorRealWorldScenarios:
    """Tests for real-world CLI scenarios"""

    def test_git_like_cli(self, cli_runner):
        """Test a Git-like CLI with common aliases"""
        app = ExtendedTyper()

        @app.command("checkout", aliases=["co"])
        def checkout(branch: str):
            """Checkout a branch."""
            print(f"Switched to branch '{branch}'")

        @app.command("status", aliases=["st"])
        def status():
            """Show status."""
            print("On branch main")

        @app.command("commit", aliases=["ci"])
        def commit(message: str = app.Option(..., "--message", "-m")):
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
        app = ExtendedTyper()

        @app.command("install", aliases=["i", "add"])
        def install(package: str):
            """Install a package."""
            print(f"Installing {package}...")

        @app.command("remove", aliases=["rm", "uninstall"])
        def remove(package: str):
            """Remove a package."""
            print(f"Removing {package}...")

        @app.command("list", aliases=["ls", "l"])
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
        app = ExtendedTyper()

        @app.command("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command("goodbye", aliases=["bye"])
        def goodbye(name: str):
            """Say goodbye."""
            print(f"Goodbye, {name}!")

        result = cli_runner.invoke(app, ["greet"])

        # Typer/Click should show missing argument error
        assert result.exit_code != 0

    def test_invalid_alias_invocation(self, cli_runner):
        """Test invoking non-existent alias"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command("delete", aliases=["rm", "del"])
        def delete_item():
            """Delete an item."""
            print("Deleting item...")

        result = cli_runner.invoke(app, ["dir"])  # Not an alias

        # Should show "No such command" error
        assert result.exit_code != 0


class TestDecoratorWithStandardCommands:
    """Tests for mixing decorated and standard Typer commands"""

    def test_both_decorator_types_work(self, cli_runner):
        """Test using both decorator styles in same app."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
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

    def test_help_shows_both_command_types(self, cli_runner, clean_output):
        """Test that help shows both types of commands"""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
        def list_items():
            """List items."""
            pass

        @app.command()
        def hello():
            """Say hello."""
            pass

        result = cli_runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show primary commands and descriptions
        assert "list" in clean_result
        assert "hello" in clean_result
        assert "List items" in clean_result
        assert "Say hello" in clean_result
