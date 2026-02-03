"""Typer extension for command aliases with grouped help display"""

import logging
import os

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
    # Core functionality
    "ExtendedTyper",
    "__version__",
    # Exported from Typer
    # "Abort",
    # "Argument",
    # "BadParameter",
    # "CallbackParam",
    "Context",
    # "Exit",
    # "FileBinaryRead",
    # "FileBinaryWrite",
    # "FileText",
    # "Option",
]


def __getattr__(name: str) -> str:
    """Fallback attribute access from Typer, provides forward compatibility.

    Args:
        name (str): The name of the attribute to access.

    Returns:
        str: The value of the requested attribute.
    """
    import typer

    return getattr(typer, name)
