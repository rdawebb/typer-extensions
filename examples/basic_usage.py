"""Basic usage example for typer-extensions

This example demonstrates the decorator syntax for creating commands with aliases
using typer-extensions. Run with '--help' to see how aliases are displayed in the help text.
"""

from typer_extensions import ExtendedTyper

app = ExtendedTyper()


@app.command("list", aliases=["ls", "l"])
def list_items():
    """List all items in the system."""
    print("Listing items...")
    print("- Item 1")
    print("- Item 2")
    print("- Item 3")


@app.command("delete", aliases=["rm", "del"])
def delete_item(name: str):
    """Delete an item by name."""
    print(f"Deleting {name}...")
    print(f"✓ {name} deleted successfully")


@app.command("create", aliases=["new", "add"])
def create_item(name: str, description: str = ""):
    """Create a new item."""
    print(f"Creating item: {name}")
    if description:
        print(f"Description: {description}")
    print("✓ Item created successfully")


# Standard command (no aliases)
@app.command()
def hello(name: str = "World"):
    """Say hello."""
    print(f"Hello, {name}!")


if __name__ == "__main__":
    app()
