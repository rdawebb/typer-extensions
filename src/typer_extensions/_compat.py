"""Click compatibility shim

Typer 0.26 vendored Click as ``typer._click`` and dropped its dependency on the
standalone ``click`` package. Earlier versions import the standalone package
instead, and always declare it as a dependency, so the fallback branch only runs
where ``click`` is guaranteed to be installed.

All internal Click access goes through this module so the split is resolved in
one place.

Type checkers are pointed at the vendored copy unconditionally. Typer's own
signatures are written in terms of ``typer._click``, so resolving both branches
would widen every annotation to ``typer._click.core.X | click.core.X`` and make
the shim's types incompatible with the Typer API it wraps.
"""

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typer import _click as click
    from typer._click import types

else:
    try:  # Typer >= 0.26 vendors Click as typer._click
        from typer import _click as click
        from typer._click import types
    except ImportError:  # Typer < 0.26 uses the standalone click package
        import click
        from click import types

Command = click.Command
Context = click.Context
HelpFormatter = click.HelpFormatter

__all__ = ["Command", "Context", "HelpFormatter", "click", "types"]
