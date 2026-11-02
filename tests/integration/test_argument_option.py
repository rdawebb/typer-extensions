"""Integration tests for Arguments and Options with command aliases."""


def test_required_argument_missing_error(cli, make_app) -> None:
    """Test error when required argument is missing."""
    app = make_app()

    @app.command("greet", aliases=["hi"])
    def greet(name: str):
        """Greet someone."""

    cli(app, "greet", ok=False)


def test_arguments_and_options_reach_command(cli, make_app) -> None:
    """Test arguments and options work identically via primary and alias."""
    app = make_app()

    @app.command("build", aliases=["b"])
    def build(
        project: str = app.Argument(...),
        target: str = app.Argument("default"),
        release: bool = app.Option(False, "--release", "-r"),
        jobs: int = app.Option(1, "--jobs", "-j"),
    ):
        """Build a project."""
        mode = "release" if release else "debug"
        print(f"Building {project} (target: {target}, mode: {mode}, jobs: {jobs})")

    expected = "Building myapp (target: default, mode: debug, jobs: 1)"
    assert expected in cli(app, "build", "myapp")

    expected = "Building myapp (target: production, mode: release, jobs: 8)"
    assert expected in cli(app, "b", "myapp", "production", "-r", "-j", "8")


def test_help_shows_arguments_and_options_via_alias(cli, make_app) -> None:
    """Test command help via an alias shows all arguments and options."""
    app = make_app()

    @app.command("copy", aliases=["cp"])
    def copy_file(
        source: str = app.Argument(..., help="Source file path"),
        dest: str = app.Argument(..., help="Destination file path"),
        force: bool = app.Option(False, "--force", "-f", help="Force overwrite"),
    ):
        """Copy a file from source to destination."""

    output = cli(app, "cp", "--help")

    assert "SOURCE" in output
    assert "DEST" in output
    assert "--force" in output
    assert "Copy a file" in output
