"""Integration tests for Option with command aliases.

This module tests that options work identically whether invoked via the primary command name or an aliase.
"""

from typer_extensions import ExtendedTyper


class TestOptionsWithAliases:
    """Tests for options working identically with primary commands and aliases."""

    def test_boolean_option_flag_via_primary(self, cli_runner, clean_output):
        """Test boolean option flag via primary command."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
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
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Listing items" in clean_result
        assert (
            "verbose" not in clean_result.lower() or "verbose mode" not in clean_result
        )

        result = cli_runner.invoke(app, ["list", "--verbose"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "verbose mode" in clean_result

    def test_boolean_option_flag_via_alias(self, cli_runner, clean_output):
        """Test boolean option flag via alias."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
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

        result = cli_runner.invoke(app, ["ls", "--verbose"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "verbose mode" in clean_result

        result = cli_runner.invoke(app, ["ls", "-v"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "verbose mode" in clean_result

    def test_option_with_value_via_primary(self, cli_runner, clean_output):
        """Test option with value via primary command."""
        app = ExtendedTyper()

        @app.command("process", aliases=["proc"])
        def process(output: str = app.Option("default.txt", "--output", "-o")):
            """Process with output file."""
            print(f"Writing to {output}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["process", "--output", "result.txt"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Writing to result.txt" in clean_result

    def test_option_with_value_via_alias(self, cli_runner, clean_output):
        """Test option with value via alias."""
        app = ExtendedTyper()

        @app.command("process", aliases=["proc"])
        def process(output: str = app.Option("default.txt", "--output", "-o")):
            """Process with output file."""
            print(f"Writing to {output}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["proc", "-o", "result.txt"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Writing to result.txt" in clean_result

    def test_option_with_default_value(self, cli_runner, clean_output):
        """Test option with default value."""
        app = ExtendedTyper()

        @app.command("run", aliases=["r"])
        def run(threads: int = app.Option(1, "--threads", "-t")):
            """Run with specified threads."""
            print(f"Running with {threads} threads")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["run"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Running with 1 threads" in clean_result

        result = cli_runner.invoke(app, ["r", "--threads", "4"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Running with 4 threads" in clean_result

    def test_multiple_options_via_primary(self, cli_runner, clean_output):
        """Test multiple options together via primary command."""
        app = ExtendedTyper()

        @app.command("download", aliases=["dl"])
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
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "http://example.com/file" in clean_result
        assert "myfile.bin" in clean_result
        assert "60s" in clean_result

    def test_multiple_options_via_alias(self, cli_runner, clean_output):
        """Test multiple options together via alias."""
        app = ExtendedTyper()

        @app.command("download", aliases=["dl"])
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
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "http://example.com/file" in clean_result
        assert "myfile.bin" in clean_result
        assert "60s" in clean_result

    def test_option_with_short_flag_only(self, cli_runner, clean_output):
        """Test option with only short flag."""
        app = ExtendedTyper()

        @app.command("verify", aliases=["v"])
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
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "quiet" in clean_result

        result = cli_runner.invoke(app, ["v", "-q"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "quiet" in clean_result


class TestOptionsInHelp:
    """Tests for option display in help text."""

    def test_help_shows_option_via_primary(self, cli_runner, clean_output):
        """Test help shows option info via primary command."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
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

        assert "--verbose" in clean_result or "-v" in clean_result
        assert "verbose output" in clean_result.lower()

    def test_help_shows_option_via_alias(self, cli_runner, clean_output):
        """Test help shows option info via alias."""
        app = ExtendedTyper()

        @app.command("list", aliases=["ls"])
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

        assert "--verbose" in clean_result or "-v" in clean_result
        assert "verbose output" in clean_result.lower()
