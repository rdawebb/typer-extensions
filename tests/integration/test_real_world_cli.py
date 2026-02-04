"""Integration tests for real-world CLI scenarios.

This module contains tests that simulate realistic CLI applications like Git, Docker, npm, and other common command-line tools to ensure the alias functionality works well in practical use cases.
"""

from typer_extensions import ExtendedTyper


class TestGitLikeCLI:
    """Tests for Git-like CLI scenarios."""

    def test_git_add_like_command(self, cli_runner):
        """Test Git-like 'add' command with pattern and options."""
        app = ExtendedTyper()

        @app.command("add", aliases=["a"])
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


class TestDockerLikeCLI:
    """Tests for Docker-like CLI scenarios."""

    def test_docker_run_like_command(self, cli_runner):
        """Test Docker run-like command with multiple options."""
        app = ExtendedTyper()

        @app.command("run", aliases=["r"])
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


class TestNpmLikeCLI:
    """Tests for npm-like CLI scenarios."""

    def test_npm_install_like_command(self, cli_runner):
        """Test npm install-like command with optional package and flags."""
        app = ExtendedTyper()

        @app.command("install", aliases=["i", "add"])
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


class TestConfigManagementCLI:
    """Tests for configuration management CLI scenarios."""

    def test_config_command_subcommand_like(self, cli_runner):
        """Test config-like command with action argument and options."""
        app = ExtendedTyper()

        @app.command("config", aliases=["cfg"])
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


class TestPackageManagerCLI:
    """Tests for package manager-like CLI scenarios."""

    def test_package_manager_commands(self, cli_runner):
        """Test a package manager-like CLI with multiple commands."""
        app = ExtendedTyper()

        @app.command("install", aliases=["i", "add"])
        def install(package: str):
            """Install a package."""
            print(f"Installing {package}...")

        @app.command("remove", aliases=["rm", "uninstall", "delete"])
        def remove(package: str):
            """Remove a package."""
            print(f"Removing {package}...")

        @app.command("list", aliases=["ls", "l"])
        def list_packages():
            """List installed packages."""
            print("Installed packages: pkg1, pkg2")

        result = cli_runner.invoke(app, ["i", "requests"])
        assert result.exit_code == 0
        assert "Installing requests..." in result.output

        result = cli_runner.invoke(app, ["rm", "requests"])
        assert result.exit_code == 0
        assert "Removing requests..." in result.output

        result = cli_runner.invoke(app, ["ls"])
        assert result.exit_code == 0
        assert "Installed packages:" in result.output


class TestFileOperationsCLI:
    """Tests for file operations CLI scenarios."""

    def test_copy_command(self, cli_runner):
        """Test copy command with source, destination, and options."""
        app = ExtendedTyper()

        @app.command("copy", aliases=["cp"])
        def copy_file(
            source: str = app.Argument(..., help="Source file"),
            dest: str = app.Argument(..., help="Destination file"),
            force: bool = app.Option(False, "--force", "-f", help="Force overwrite"),
            recursive: bool = app.Option(
                False, "--recursive", "-r", help="Copy recursively"
            ),
        ):
            """Copy files or directories."""
            flags = []
            if force:
                flags.append("force")
            if recursive:
                flags.append("recursive")

            flags_str = f" ({', '.join(flags)})" if flags else ""
            print(f"Copying {source} to {dest}{flags_str}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["cp", "file.txt", "backup.txt"])
        assert result.exit_code == 0
        assert "Copying file.txt to backup.txt" in result.output

        result = cli_runner.invoke(app, ["copy", "dir/", "backup/", "-r", "-f"])
        assert result.exit_code == 0
        assert "Copying dir/ to backup/" in result.output
        assert "recursive" in result.output
        assert "force" in result.output

    def test_move_command(self, cli_runner):
        """Test move command similar to mv."""
        app = ExtendedTyper()

        @app.command("move", aliases=["mv"])
        def move_file(
            source: str = app.Argument(...),
            dest: str = app.Argument(...),
            interactive: bool = app.Option(
                False, "--interactive", "-i", help="Prompt before overwrite"
            ),
        ):
            """Move files or directories."""
            mode = "interactive" if interactive else "direct"
            print(f"Moving {source} to {dest} ({mode})")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["mv", "old.txt", "new.txt"])
        assert result.exit_code == 0
        assert "Moving old.txt to new.txt" in result.output
        assert "direct" in result.output

        result = cli_runner.invoke(app, ["move", "old.txt", "new.txt", "-i"])
        assert result.exit_code == 0
        assert "interactive" in result.output


class TestDatabaseCLI:
    """Tests for database management CLI scenarios."""

    def test_database_migration_commands(self, cli_runner, clean_output):
        """Test database migration-like commands."""
        app = ExtendedTyper()

        @app.command("migrate", aliases=["mig", "m"])
        def migrate(
            direction: str = app.Argument("up", help="Migration direction: up or down"),
            steps: int = app.Option(1, "--steps", "-n", help="Number of steps"),
            dry_run: bool = app.Option(
                False, "--dry-run", help="Show what would be done"
            ),
        ):
            """Run database migrations."""
            dry = "DRY RUN: " if dry_run else ""
            print(f"{dry}Migrating {direction} {steps} step(s)")

        @app.command()
        def rollback(
            steps: int = app.Option(1, "--steps", "-n", help="Number of steps"),
            dry_run: bool = app.Option(
                False, "--dry-run", help="Show what would be done"
            ),
        ):
            """Rollback database migrations."""
            dry = "DRY RUN: " if dry_run else ""
            print(f"{dry}Rolling back {steps} step(s)")

        result = cli_runner.invoke(app, ["migrate"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Migrating up 1 step(s)" in clean_result

        result = cli_runner.invoke(app, ["m", "down", "-n", "3", "--dry-run"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "DRY RUN" in clean_result
        assert "down 3 step(s)" in clean_result


class TestBuildToolCLI:
    """Tests for build tool CLI scenarios."""

    def test_build_command_comprehensive(self, cli_runner, clean_output):
        """Test comprehensive build command with multiple options."""
        app = ExtendedTyper()

        @app.command("build", aliases=["b"])
        def build(
            project: str = app.Argument(..., help="Project to build"),
            target: str = app.Argument("default", help="Build target"),
            release: bool = app.Option(False, "--release", "-r", help="Release build"),
            jobs: int = app.Option(1, "--jobs", "-j", help="Parallel jobs"),
            verbose: bool = app.Option(False, "--verbose", "-v", help="Verbose output"),
        ):
            """Build a project."""
            mode = "release" if release else "debug"
            flags = []
            if verbose:
                flags.append("verbose")

            flags_str = f" [{', '.join(flags)}]" if flags else ""
            print(
                f"Building {project} (target: {target}, mode: {mode}, jobs: {jobs}){flags_str}"
            )

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["build", "myapp"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Building myapp" in clean_result
        assert "target: default" in clean_result
        assert "mode: debug" in clean_result

        result = cli_runner.invoke(
            app, ["b", "myapp", "production", "-r", "-j", "8", "-v"]
        )
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Building myapp" in clean_result
        assert "target: production" in clean_result
        assert "mode: release" in clean_result
        assert "jobs: 8" in clean_result
        assert "verbose" in clean_result


class TestServerManagementCLI:
    """Tests for server management CLI scenarios."""

    def test_server_start_command(self, cli_runner, clean_output):
        """Test server start command with various options."""
        app = ExtendedTyper()

        @app.command("start", aliases=["s", "run"])
        def start(
            host: str = app.Option("localhost", "--host", "-h", help="Server host"),
            port: int = app.Option(8000, "--port", "-p", help="Server port"),
            workers: int = app.Option(1, "--workers", "-w", help="Number of workers"),
            reload: bool = app.Option(False, "--reload", help="Auto-reload on changes"),
        ):
            """Start the server."""
            reload_str = " (auto-reload)" if reload else ""
            print(
                f"Starting server at {host}:{port} with {workers} worker(s){reload_str}"
            )

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["start"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Starting server at localhost:8000" in clean_result
        assert "1 worker(s)" in clean_result

        result = cli_runner.invoke(
            app, ["s", "-h", "0.0.0.0", "-p", "3000", "-w", "4", "--reload"]
        )
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "0.0.0.0:3000" in clean_result
        assert "4 worker(s)" in clean_result
        assert "auto-reload" in clean_result


class TestDeploymentCLI:
    """Tests for deployment CLI scenarios."""

    def test_deploy_command_with_environment(self, cli_runner, clean_output):
        """Test deployment command with environment selection."""
        app = ExtendedTyper()

        @app.command("deploy", aliases=["d"])
        def deploy(
            service: str = app.Argument(..., help="Service to deploy"),
            environment: str = app.Option(
                "staging", "--env", "-e", help="Target environment"
            ),
            force: bool = app.Option(False, "--force", "-f", help="Force deployment"),
            dry_run: bool = app.Option(False, "--dry-run", help="Simulate deployment"),
        ):
            """Deploy a service."""
            prefix = "SIMULATING: " if dry_run else ""
            force_str = " (forced)" if force else ""
            print(f"{prefix}Deploying {service} to {environment}{force_str}")

        @app.command()
        def other():
            """Another command."""
            print("Other")

        result = cli_runner.invoke(app, ["deploy", "api"])
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "Deploying api to staging" in clean_result

        result = cli_runner.invoke(
            app, ["d", "web-app", "-e", "production", "-f", "--dry-run"]
        )
        clean_result = clean_output(result.output)

        assert result.exit_code == 0
        assert "SIMULATING" in clean_result
        assert "web-app to production" in clean_result
        assert "forced" in clean_result
