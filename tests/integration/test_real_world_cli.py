"""Integration tests for real-world CLI scenarios.

This module contains tests that simulate realistic CLI applications like Git, Docker, npm, and other common command-line tools to ensure the alias functionality works well in practical use cases.
"""


class TestGitLikeCLI:
    """Tests for Git-like CLI scenarios."""

    def test_git_add_like_command(self, app, assert_success):
        """Test Git-like 'add' command with pattern and options."""

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

        assert_success(app, ["add"], ["Adding ."])
        assert_success(app, ["a", "src/", "-A"], ["Adding all changes"])
        assert_success(
            app,
            ["--help"],
            ["add", "(a)", "Add files to staging area"],
        )


class TestDockerLikeCLI:
    """Tests for Docker-like CLI scenarios."""

    def test_docker_run_like_command(self, app, assert_success):
        """Test Docker run-like command with multiple options."""

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

        assert_success(app, ["run", "nginx"], ["Running image nginx"])
        assert_success(
            app,
            ["r", "postgres", "-d", "-p", "5432:5432"],
            ["Running image postgres in background with port 5432:5432"],
        )


class TestNpmLikeCLI:
    """Tests for npm-like CLI scenarios."""

    def test_npm_install_like_command(self, app, assert_success):
        """Test npm install-like command with optional package and flags."""

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

        assert_success(app, ["install"], ["Installing all dependencies"])
        assert_success(
            app, ["add", "lodash", "-D"], ["Installing lodash (dev) locally"]
        )
        assert_success(
            app, ["i", "eslint", "-g"], ["Installing eslint (prod) globally"]
        )


class TestConfigManagementCLI:
    """Tests for configuration management CLI scenarios."""

    def test_config_command_subcommand_like(self, app, assert_success):
        """Test config-like command with action argument and options."""

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

        assert_success(app, ["config", "list", "-s", "global"], ["LIST all (global)"])
        assert_success(app, ["cfg", "set", "theme", "dark"], ["SET theme"])


class TestPackageManagerCLI:
    """Tests for package manager-like CLI scenarios."""

    def test_package_manager_commands(self, app, assert_success):
        """Test a package manager-like CLI with multiple commands."""

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

        assert_success(app, ["i", "requests"], ["Installing requests..."])
        assert_success(app, ["rm", "requests"], ["Removing requests..."])
        assert_success(app, ["ls"], ["Installed packages: pkg1, pkg2"])


class TestFileOperationsCLI:
    """Tests for file operations CLI scenarios."""

    def test_copy_command(self, app, assert_success):
        """Test copy command with source, destination, and options."""

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

        assert_success(
            app, ["cp", "file.txt", "backup.txt"], ["Copying file.txt to backup.txt"]
        )
        assert_success(
            app,
            ["copy", "dir/", "backup/", "-f", "-r"],
            ["Copying dir/ to backup/ (force, recursive)"],
        )

    def test_move_command(self, app, assert_success):
        """Test move command similar to mv."""

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

        assert_success(
            app, ["mv", "old.txt", "new.txt"], ["Moving old.txt to new.txt (direct)"]
        )
        assert_success(
            app,
            ["mv", "old.txt", "new.txt", "-i"],
            ["Moving old.txt to new.txt (interactive)"],
        )


class TestDatabaseCLI:
    """Tests for database management CLI scenarios."""

    def test_database_migration_commands(self, app, assert_success):
        """Test database migration-like commands."""

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

        assert_success(app, ["migrate"], ["Migrating up 1 step(s)"])
        assert_success(
            app,
            ["m", "down", "-n", "3", "--dry-run"],
            ["DRY RUN: Migrating down 3 step(s)"],
        )


class TestBuildToolCLI:
    """Tests for build tool CLI scenarios."""

    def test_build_command_comprehensive(self, app, assert_success):
        """Test comprehensive build command with multiple options."""

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

        assert_success(
            app,
            ["build", "myapp"],
            ["Building myapp (target: default, mode: debug, jobs: 1)"],
        )
        assert_success(
            app,
            ["b", "myapp", "production", "-r", "-j", "8", "-v"],
            ["Building myapp (target: production, mode: release, jobs: 8) [verbose]"],
        )


class TestServerManagementCLI:
    """Tests for server management CLI scenarios."""

    def test_server_start_command(self, app, assert_success):
        """Test server start command with various options."""

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

        assert_success(
            app,
            ["start"],
            ["Starting server at localhost:8000 with 1 worker(s)"],
        )
        assert_success(
            app,
            ["s", "-h", "0.0.0.0", "-p", "3000", "-w", "4", "--reload"],
            ["Starting server at 0.0.0.0:3000 with 4 worker(s) (auto-reload)"],
        )


class TestDeploymentCLI:
    """Tests for deployment CLI scenarios."""

    def test_deploy_command_with_environment(self, app, assert_success):
        """Test deployment command with environment selection."""

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

        assert_success(
            app,
            ["deploy", "api"],
            ["Deploying api to staging"],
        )
        assert_success(
            app,
            ["d", "web-app", "-e", "production", "-f", "--dry-run"],
            ["SIMULATING: Deploying web-app to production (forced)"],
        )
