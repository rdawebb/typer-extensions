"""Typer extension for command aliases with grouped help display"""

import logging
import os
from typing import Any

# Apply lazy Rich patch if enabled (opt-out via TYPER_EXTENSIONS_RICH=0)
if os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "1":  # pragma: no cover
    try:
        from typer_extensions._patch import apply_rich_patch

        _patch_applied = apply_rich_patch()
        if os.environ.get("TYPER_EXTENSIONS_DEBUG") and _patch_applied:
            logging.getLogger(__name__).debug("Rich patch applied")

    except Exception as e:
        logging.getLogger(__name__).error(f"Failed to apply Rich patch: {e}")
        pass  # Fall back to default behavior


from typer_extensions._version import __version__
from typer_extensions.core import Context, ExtendedTyper


__all__ = [
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
    "clear",
    "confirm",
    "echo",
    "echo_via_pager",
    "edit",
    "format_filename",
    "get_app_dir",
    "get_binary_stream",
    "get_terminal_size",
    "get_text_stream",
    "getchar",
    "launch",
    "open_file",
    "pause",
    "progressbar",
    "prompt",
    "run",
    "secho",
    "style",
    "unstyle",
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
