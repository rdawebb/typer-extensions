"""Typer extension for command aliases with grouped help display"""

from typing import Any

from typer_extensions._version import __version__
from typer_extensions.core import Context, ExtendedTyper

__all__ = [  # noqa: RUF022 - grouped by category rather than sorted
    # Core
    "ExtendedTyper",
    "Context",
    "__version__",
    # Typer parameter types
    "Argument",
    "Option",
    "CallbackParam",
    # Typer file type aliases
    "FileBinaryRead",
    "FileBinaryWrite",
    "FileText",
    "FileTextWrite",
    # Typer exceptions
    "Abort",
    "Exit",
    "BadParameter",
    # Typer utility functions
    "confirm",
    "echo",
    "format_filename",
    "get_app_dir",
    "get_binary_stream",
    "get_terminal_size",
    "get_text_stream",
    "getchar",
    "launch",
    "progressbar",
    "prompt",
    "run",
    "secho",
    "style",
]


def __getattr__(name: str) -> Any:
    """Fallback attribute access from Typer, provides forward compatibility.

    Args:
        name (str): The name of the attribute to access.

    Returns:
        Any: The value of the requested attribute.
    """
    import typer

    return getattr(typer, name)
