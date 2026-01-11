"""Simple Argument and Option compatibility example with typer-aliases

This example showcases how to use both Typer's Arguments and Options with the AliasedTyper class. Run with '--help' to see how aliases are displayed in the help text.
"""

from typer_aliases import AliasedTyper

app = AliasedTyper()


@app.command_with_aliases("greet", aliases=["hi", "hello"])
def greet(name: str = app.Argument(...)):
    """Greet someone by name."""
    print(f"Hello, {name}!")


@app.command_with_aliases("process", aliases=["p"])
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
