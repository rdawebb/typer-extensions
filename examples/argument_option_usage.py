"""Simple Argument and Option compatibility example with typer-extensions

This example showcases how to use both Typer's Arguments and Options with the
ExtendedTyper class. Run with '--help' to see how aliases are displayed in the help text.
"""

from typer_extensions import ExtendedTyper

app = ExtendedTyper()


@app.command("greet", aliases=["hi", "hello"])
def greet(name: str = app.Argument(...)):
    """Greet someone by name."""
    print(f"Hello, {name}!")


@app.command("process", aliases=["p"])
def process(
    items: int = app.Argument(...),
    verbose: bool = app.Option(False, "--verbose", "-v"),
):
    """Process a number of items."""
    if verbose:
        print(f"Processing {items} items (verbose mode)...")
    else:
        print(f"Processing {items} items...")


if __name__ == "__main__":
    app()
