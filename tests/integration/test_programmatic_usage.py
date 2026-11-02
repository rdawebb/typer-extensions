"""Integration tests for programmatic API methods"""

import typer

from typer_extensions import ExtendedTyper


def test_invoke_programmatic_command(cli) -> None:
    """Test invoking command registered programmatically"""
    app = ExtendedTyper()

    def list_items():
        print("Listing items...")

    def delete_item():
        print("Deleting item...")

    app.add_command(list_items, "list", aliases=["ls"])
    app.add_command(delete_item, "delete", aliases=["rm", "del"])

    assert "Listing items..." in cli(app, "list")
    assert "Listing items..." in cli(app, "ls")


def test_dynamic_alias_workflow(cli, make_app) -> None:
    """Test a complete workflow of dynamic alias management."""
    app = make_app(aliases=False)
    cli(app, "ls", ok=False)

    app.add_alias("list", "ls")
    cli(app, "ls")

    app.add_alias("list", "l")
    cli(app, "l")

    app.remove_alias("ls")
    cli(app, "ls", ok=False)
    cli(app, "l")


def test_re_add_removed_alias_to_different_command(cli, make_app) -> None:
    """Test that a removed alias can be added to a different command"""
    app = make_app(aliases=False)

    app.add_alias("list", "ls")
    assert "Listing items..." in cli(app, "ls")

    app.remove_alias("ls")
    cli(app, "ls", ok=False)

    app.add_alias("delete", "ls")
    assert "Deleting item..." in cli(app, "ls")


def test_add_alias_to_decorated_command(cli, make_app) -> None:
    """Test adding alias to command registered with decorator"""
    app = make_app()

    app.add_alias("list", "dir")

    for name in ["list", "ls", "dir"]:
        assert "Listing items..." in cli(app, name)


def test_command_help_after_add_alias(cli, make_app) -> None:
    """Test that command help works after adding alias"""
    app = make_app(aliases=False)

    app.add_alias("list", "ls")

    assert "List all items" in cli(app, "list", "--help")
    assert "List all items" in cli(app, "ls", "--help")


class TestRegularTyperWithMonkeyPatch:
    """Tests for regular Typer instances with the monkey patch applied"""

    @staticmethod
    def _regular_app() -> typer.Typer:
        """Build a regular Typer app (not ExtendedTyper)"""
        app = typer.Typer()

        @app.command("list")
        def list_items():
            """List all items in the system."""
            print("Listing items...")

        @app.command("delete")
        def delete_items():
            """Delete items from the system."""
            print("Deleting items...")

        return app

    def test_regular_typer_still_works(self, cli) -> None:
        """Test that regular Typer apps still work after ExtendedTyper import"""
        app = self._regular_app()

        assert "Listing items..." in cli(app, "list")
        assert "Deleting items..." in cli(app, "delete")

    def test_regular_typer_help_still_works(self, cli) -> None:
        """Test that regular Typer help text still works after ExtendedTyper import"""
        output = cli(self._regular_app(), "--help")

        assert "list" in output
        assert "delete" in output
        assert "List all items" in output
