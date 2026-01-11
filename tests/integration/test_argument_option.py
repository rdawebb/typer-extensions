"""Integration tests for Arguments and Options with command aliases."""

import typer
from typer_aliases import AliasedTyper


class TestArgumentsWithAliases:
    """Tests for arguments working identically with primary commands and aliases."""

    def test_single_argument_via_primary(self, cli_runner):
        """Test single positional argument via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["greet", "Alice"])
        assert result.exit_code == 0
        assert "Hello, Alice!" in result.output

    def test_single_argument_via_alias(self, cli_runner):
        """Test single positional argument via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi", "hello"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["hi", "Bob"])
        assert result.exit_code == 0
        assert "Hello, Bob!" in result.output

        result = cli_runner.invoke(app, ["hello", "Charlie"])
        assert result.exit_code == 0
        assert "Hello, Charlie!" in result.output

    def test_multiple_arguments_via_primary(self, cli_runner):
        """Test multiple positional arguments via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("copy", aliases=["cp"])
        def copy_file(source: str, destination: str):
            """Copy a file."""
            print(f"Copying {source} to {destination}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["copy", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    def test_multiple_arguments_via_alias(self, cli_runner):
        """Test multiple positional arguments via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("copy", aliases=["cp"])
        def copy_file(source: str, destination: str):
            """Copy a file."""
            print(f"Copying {source} to {destination}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["cp", "file1.txt", "file2.txt"])
        assert result.exit_code == 0
        assert "Copying file1.txt to file2.txt" in result.output

    def test_argument_with_type_conversion_int(self, cli_runner):
        """Test argument with integer type conversion."""
        app = AliasedTyper()

        @app.command_with_aliases("count", aliases=["c"])
        def count_down(number: int):
            """Count down from a number."""
            print(f"Counting down from {number}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["count", "5"])
        assert result.exit_code == 0
        assert "Counting down from 5" in result.output

        result = cli_runner.invoke(app, ["c", "10"])
        assert result.exit_code == 0
        assert "Counting down from 10" in result.output

    def test_argument_with_type_conversion_float(self, cli_runner):
        """Test argument with float type conversion."""
        app = AliasedTyper()

        @app.command_with_aliases("calculate", aliases=["calc"])
        def calculate(value: float):
            """Calculate something."""
            result = value * 2
            print(f"Result: {result}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["calculate", "3.5"])
        assert result.exit_code == 0
        assert "Result: 7" in result.output

        result = cli_runner.invoke(app, ["calc", "2.5"])
        assert result.exit_code == 0
        assert "Result: 5" in result.output

    def test_optional_argument_with_default(self, cli_runner):
        """Test optional argument with default value."""
        app = AliasedTyper()

        @app.command_with_aliases("say", aliases=["s"])
        def say(message: str = app.Argument("Hello")):
            """Say a message."""
            print(message)

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["say"])
        assert result.exit_code == 0
        assert "Hello" in result.output

        result = cli_runner.invoke(app, ["say", "Goodbye"])
        assert result.exit_code == 0
        assert "Goodbye" in result.output

        result = cli_runner.invoke(app, ["s", "Hi there"])
        assert result.exit_code == 0
        assert "Hi there" in result.output

    def test_required_argument_missing_error(self, cli_runner):
        """Test error when required argument is missing."""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone."""
            print(f"Hello, {name}!")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["greet"])
        assert result.exit_code != 0


class TestOptionsWithAliases:
    """Tests for options working identically with primary commands and aliases."""

    def test_boolean_option_flag_via_primary(self, cli_runner):
        """Test boolean option flag via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(verbose: bool = app.Option(False, "--verbose", "-v")):
            """List items."""
            if verbose:
                print("Listing items (verbose mode)")
            else:
                print("Listing items")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Listing items" in result.output
        assert (
            "verbose" not in result.output.lower()
            or "verbose mode" not in result.output
        )

        result = cli_runner.invoke(app, ["list", "--verbose"])
        assert result.exit_code == 0
        assert "verbose mode" in result.output

    def test_boolean_option_flag_via_alias(self, cli_runner):
        """Test boolean option flag via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(verbose: bool = typer.Option(False, "--verbose", "-v")):
            """List items."""
            if verbose:
                print("Listing items (verbose mode)")
            else:
                print("Listing items")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["ls", "--verbose"])
        assert result.exit_code == 0
        assert "verbose mode" in result.output

        result = cli_runner.invoke(app, ["ls", "-v"])
        assert result.exit_code == 0
        assert "verbose mode" in result.output

    def test_option_with_value_via_primary(self, cli_runner):
        """Test option with value via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("process", aliases=["proc"])
        def process(output: str = app.Option("default.txt", "--output", "-o")):
            """Process with output file."""
            print(f"Writing to {output}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["process", "--output", "result.txt"])
        assert result.exit_code == 0
        assert "Writing to result.txt" in result.output

    def test_option_with_value_via_alias(self, cli_runner):
        """Test option with value via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("process", aliases=["proc"])
        def process(output: str = app.Option("default.txt", "--output", "-o")):
            """Process with output file."""
            print(f"Writing to {output}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["proc", "-o", "result.txt"])
        assert result.exit_code == 0
        assert "Writing to result.txt" in result.output

    def test_option_with_default_value(self, cli_runner):
        """Test option with default value."""
        app = AliasedTyper()

        @app.command_with_aliases("run", aliases=["r"])
        def run(threads: int = app.Option(1, "--threads", "-t")):
            """Run with specified threads."""
            print(f"Running with {threads} threads")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["run"])
        assert result.exit_code == 0
        assert "Running with 1 threads" in result.output

        result = cli_runner.invoke(app, ["r", "--threads", "4"])
        assert result.exit_code == 0
        assert "Running with 4 threads" in result.output

    def test_multiple_options_via_primary(self, cli_runner):
        """Test multiple options together via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("download", aliases=["dl"])
        def download(
            url: str = app.Argument(...),
            output: str = app.Option("downloaded.bin", "--output", "-o"),
            timeout: int = app.Option(30, "--timeout", "-t"),
        ):
            """Download a file."""
            print(f"Downloading from {url} to {output} (timeout: {timeout}s)")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(
            app,
            [
                "download",
                "http://example.com/file",
                "--output",
                "myfile.bin",
                "--timeout",
                "60",
            ],
        )
        assert result.exit_code == 0
        assert "http://example.com/file" in result.output
        assert "myfile.bin" in result.output
        assert "60s" in result.output

    def test_multiple_options_via_alias(self, cli_runner):
        """Test multiple options together via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("download", aliases=["dl"])
        def download(
            url: str = app.Argument(...),
            output: str = app.Option("downloaded.bin", "--output", "-o"),
            timeout: int = app.Option(30, "--timeout", "-t"),
        ):
            """Download a file."""
            print(f"Downloading from {url} to {output} (timeout: {timeout}s)")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(
            app, ["dl", "http://example.com/file", "-o", "myfile.bin", "-t", "60"]
        )
        assert result.exit_code == 0
        assert "http://example.com/file" in result.output
        assert "myfile.bin" in result.output
        assert "60s" in result.output

    def test_option_with_short_flag_only(self, cli_runner):
        """Test option with only short flag."""
        app = AliasedTyper()

        @app.command_with_aliases("verify", aliases=["v"])
        def verify(quiet: bool = app.Option(False, "-q")):
            """Verify something."""
            if quiet:
                print("Verified (quiet)")
            else:
                print("Verified")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["verify", "-q"])
        assert result.exit_code == 0
        assert "quiet" in result.output

        result = cli_runner.invoke(app, ["v", "-q"])
        assert result.exit_code == 0
        assert "quiet" in result.output


class TestArgumentOptionCombinations:
    """Tests for combining arguments and options together."""

    def test_argument_and_option_together_via_primary(self, cli_runner):
        """Test command with both argument and option via primary."""
        app = AliasedTyper()

        @app.command_with_aliases("deploy", aliases=["d"])
        def deploy(service: str, force: bool = app.Option(False, "--force", "-f")):
            """Deploy a service."""
            mode = "force" if force else "normal"
            print(f"Deploying {service} in {mode} mode")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["deploy", "api-server"])
        assert result.exit_code == 0
        assert "api-server" in result.output
        assert "normal mode" in result.output

        result = cli_runner.invoke(app, ["deploy", "api-server", "--force"])
        assert result.exit_code == 0
        assert "api-server" in result.output
        assert "force mode" in result.output

    def test_argument_and_option_together_via_alias(self, cli_runner):
        """Test command with both argument and option via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("deploy", aliases=["d"])
        def deploy(service: str, force: bool = app.Option(False, "--force", "-f")):
            """Deploy a service."""
            mode = "force" if force else "normal"
            print(f"Deploying {service} in {mode} mode")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["d", "web-server"])
        assert result.exit_code == 0
        assert "web-server" in result.output

        result = cli_runner.invoke(app, ["d", "web-server", "-f"])
        assert result.exit_code == 0
        assert "web-server" in result.output
        assert "force mode" in result.output

    def test_multiple_arguments_and_options(self, cli_runner):
        """Test command with multiple arguments and options."""
        app = AliasedTyper()

        @app.command_with_aliases("build", aliases=["b"])
        def build(
            project: str = app.Argument(...),
            target: str = app.Argument("default"),
            release: bool = app.Option(False, "--release", "-r"),
            jobs: int = app.Option(1, "--jobs", "-j"),
        ):
            """Build a project."""
            mode = "release" if release else "debug"
            print(f"Building {project} (target: {target}, mode: {mode}, jobs: {jobs})")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["build", "myapp"])
        assert result.exit_code == 0
        assert "myapp" in result.output
        assert "target: default" in result.output

        result = cli_runner.invoke(app, ["b", "myapp", "production", "-r", "-j", "8"])
        assert result.exit_code == 0
        assert "myapp" in result.output
        assert "target: production" in result.output
        assert "release" in result.output
        assert "jobs: 8" in result.output

    def test_argument_with_option_bool_flag(self, cli_runner):
        """Test argument with boolean option flag."""
        app = AliasedTyper()

        @app.command_with_aliases("delete", aliases=["rm", "del"])
        def delete(path: str, force: bool = app.Option(False, "--force", "-f")):
            """Delete a file or directory."""
            if force:
                print(f"Force deleting {path}")
            else:
                print(f"Deleting {path}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["rm", "file.txt"])
        assert result.exit_code == 0
        assert "Deleting file.txt" in result.output

        result = cli_runner.invoke(app, ["del", "important_dir", "--force"])
        assert result.exit_code == 0
        assert "Force deleting important_dir" in result.output


class TestHelpWithArgumentsOptions:
    """Tests for help display with arguments and options."""

    def test_help_shows_argument_via_primary(self, cli_runner, clean_output):
        """Test help shows argument info via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone by name."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["greet", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show argument info
        assert "NAME" in clean_result or "name" in clean_result
        assert "Greet someone" in clean_result

    def test_help_shows_argument_via_alias(self, cli_runner, clean_output):
        """Test help shows argument info via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("greet", aliases=["hi"])
        def greet(name: str):
            """Greet someone by name."""
            print(f"Hello, {name}!")

        result = cli_runner.invoke(app, ["hi", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show argument info
        assert "NAME" in clean_result or "name" in clean_result
        assert "Greet someone" in clean_result

    def test_help_shows_option_via_primary(self, cli_runner, clean_output):
        """Test help shows option info via primary command."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(
            verbose: bool = app.Option(
                False, "--verbose", "-v", help="Show verbose output"
            ),
        ):
            """List items in the system."""
            print("Items")

        result = cli_runner.invoke(app, ["list", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show option info
        assert "--verbose" in clean_result or "-v" in clean_result
        assert "verbose output" in clean_result.lower()

    def test_help_shows_option_via_alias(self, cli_runner, clean_output):
        """Test help shows option info via alias."""
        app = AliasedTyper()

        @app.command_with_aliases("list", aliases=["ls"])
        def list_items(
            verbose: bool = app.Option(
                False, "--verbose", "-v", help="Show verbose output"
            ),
        ):
            """List items in the system."""
            print("Items")

        result = cli_runner.invoke(app, ["ls", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show option info
        assert "--verbose" in clean_result or "-v" in clean_result
        assert "verbose output" in clean_result.lower()

    def test_help_shows_multiple_arguments_options(self, cli_runner, clean_output):
        """Test help shows all arguments and options."""
        app = AliasedTyper()

        @app.command_with_aliases("copy", aliases=["cp"])
        def copy_file(
            source: str = app.Argument(..., help="Source file path"),
            dest: str = app.Argument(..., help="Destination file path"),
            force: bool = app.Option(False, "--force", "-f", help="Force overwrite"),
        ):
            """Copy a file from source to destination."""
            print(f"Copying {source} to {dest}")

        result = cli_runner.invoke(app, ["cp", "--help"])
        assert result.exit_code == 0
        clean_result = clean_output(result.output)

        # Should show all arguments and options
        assert "SOURCE" in clean_result or "source" in clean_result
        assert "DEST" in clean_result or "dest" in clean_result
        assert "--force" in clean_result or "-f" in clean_result
        assert "Copy a file" in clean_result


class TestRealWorldScenarios:
    """Tests for real-world CLI scenarios with arguments and options."""

    def test_git_add_like_command(self, cli_runner):
        """Test Git-like 'add' command with pattern and options."""
        app = AliasedTyper()

        @app.command_with_aliases("add", aliases=["a"])
        def add(
            pattern: str = app.Argument(".", help="Files to add"),
            all_files: bool = app.Option(
                False, "--all", "-A", help="Stage all changes"
            ),
        ):
            """Add files to staging area."""
            if all_files:
                print("Adding all changes")
            else:
                print(f"Adding {pattern}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["add"])
        assert result.exit_code == 0
        assert "Adding ." in result.output

        result = cli_runner.invoke(app, ["a", "src/", "-A"])
        assert result.exit_code == 0
        assert "Adding all changes" in result.output

    def test_docker_run_like_command(self, cli_runner):
        """Test Docker run-like command with multiple options."""
        app = AliasedTyper()

        @app.command_with_aliases("run", aliases=["r"])
        def run(
            image: str = app.Argument(...),
            detach: bool = app.Option(
                False, "-d", "--detach", help="Run in background"
            ),
            port: str = app.Option(None, "-p", "--port", help="Port mapping"),
        ):
            """Run a container."""
            msg = f"Running image {image}"
            if detach:
                msg += " in background"
            if port:
                msg += f" with port {port}"
            print(msg)

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["run", "nginx"])
        assert result.exit_code == 0
        assert "nginx" in result.output

        result = cli_runner.invoke(app, ["r", "postgres", "-d", "-p", "5432:5432"])
        assert result.exit_code == 0
        assert "postgres" in result.output
        assert "background" in result.output
        assert "5432:5432" in result.output

    def test_npm_install_like_command(self, cli_runner):
        """Test npm install-like command with optional package and flags."""
        app = AliasedTyper()

        @app.command_with_aliases("install", aliases=["i", "add"])
        def install(
            package: str = app.Argument(None, help="Package name"),
            save_dev: bool = app.Option(
                False, "--save-dev", "-D", help="Save as dev dependency"
            ),
            global_install: bool = app.Option(
                False, "-g", "--global", help="Install globally"
            ),
        ):
            """Install dependencies."""
            if package:
                scope = "globally" if global_install else "locally"
                dtype = "dev" if save_dev else "prod"
                print(f"Installing {package} ({dtype}) {scope}")
            else:
                print("Installing all dependencies")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["install"])
        assert result.exit_code == 0
        assert "Installing all" in result.output

        result = cli_runner.invoke(app, ["add", "lodash", "-D"])
        assert result.exit_code == 0
        assert "lodash" in result.output
        assert "dev" in result.output

        result = cli_runner.invoke(app, ["i", "eslint", "-g"])
        assert result.exit_code == 0
        assert "eslint" in result.output
        assert "globally" in result.output

    def test_config_command_subcommand_like(self, cli_runner):
        """Test config-like command with action argument and options."""
        app = AliasedTyper()

        @app.command_with_aliases("config", aliases=["cfg"])
        def config(
            action: str = app.Argument(..., help="Action: get, set, or list"),
            key: str = app.Argument(None, help="Config key"),
            value: str = app.Argument(None, help="Config value"),
            scope: str = app.Option(
                "local", "--scope", "-s", help="Scope: local or global"
            ),
        ):
            """Manage configuration."""
            scope_msg = f"({scope})" if scope != "local" else ""
            print(f"{action.upper()} {key or 'all'} {scope_msg}".strip())

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["config", "list", "-s", "global"])
        assert result.exit_code == 0
        assert "LIST" in result.output
        assert "global" in result.output

        result = cli_runner.invoke(app, ["cfg", "set", "theme", "dark"])
        assert result.exit_code == 0
        assert "SET" in result.output
