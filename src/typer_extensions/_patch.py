"""Monkey-patching logic for enhanced _rich_utils in Typer with version checking and graceful fallback."""

import logging
import os
import sys
from typing import Any, Dict

logger = logging.getLogger(__name__)

# Patch state tracking
PATCH_STATE: Dict[str, Any] = {
    "applied": False,
    "typer_version": None,
    "patched_functions": [],
    "originals": {},
    "skipped_reason": None,
}


def apply_rich_patch() -> bool:
    """Apply rich_utils patch to Typer using import hook.

    Returns:
        True if patch applied successfully, False if skipped
    """
    global PATCH_STATE

    # Check if already patched
    if PATCH_STATE["applied"]:
        logger.debug("Rich patch already applied")
        return True

    # Check opt-out flag
    if os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "0":
        PATCH_STATE["skipped_reason"] = "TYPER_EXTENSIONS_RICH=0 (opt-out)"
        logger.debug("Rich patch skipped: opt-out flag set")
        return False

    if "typer.rich_utils" in sys.modules:
        PATCH_STATE["skipped_reason"] = "typer.rich_utils already imported"
        logger.warning("Rich patch skipped: typer.rich_utils already imported")
        return False

    try:
        try:
            # Try via import hook
            from typer_extensions._import_hook import install_import_hook

            if install_import_hook():
                PATCH_STATE.update(
                    {
                        "applied": True,
                        "method": "import_hook",
                        "patched_functions": ["import hook interceptor"],
                        "originals": {},
                        "skipped_reason": None,
                    }
                )

                if os.environ.get("TYPER_EXTENSIONS_DEBUG"):
                    logger.info(
                        f"Rich patch applied via import hook for Typer {PATCH_STATE['typer_version']}"
                    )

                return True

        except Exception as e:
            logger.error(
                f"Failed to apply patch via import hook: {e} - trying fallback",
                exc_info=True,
            )

        # Fallback to sys.modules injection
        if "typer" in sys.modules:
            PATCH_STATE["skipped_reason"] = (
                "typer module already imported, cannot apply patch"
            )
            logger.warning("Rich patch skipped: typer module already imported")
            return False

        from typer_extensions import _rich_utils

        if "typer" not in sys.modules:  # pragma: no cover
            import types

            typer_package = types.ModuleType("typer")
            typer_package.__package__ = "typer"
            typer_package.__path__ = []
            sys.modules["typer"] = typer_package

        _rich_utils.__name__ = "typer.rich_utils"
        _rich_utils.__package__ = "typer"

        sys.modules["typer.rich_utils"] = _rich_utils
        setattr(sys.modules["typer"], "rich_utils", _rich_utils)

        PATCH_STATE.update(
            {
                "applied": True,
                "method": "sys_modules_injection",
                "patched_functions": ["sys.modules pre-injection"],
                "originals": {},
                "skipped_reason": None,
            }
        )

        if os.environ.get("TYPER_EXTENSIONS_DEBUG"):
            logger.info(
                f"Rich patch applied via sys.modules injection for Typer {PATCH_STATE['typer_version']}"
            )

        return True

    except Exception as e:  # pragma: no cover
        PATCH_STATE["skipped_reason"] = f"Exception during patching: {e}"
        logger.warning(f"Rich patch failed: {e}", exc_info=True)
        return False


def undo_rich_patch() -> None:
    """Restore Typer's original rich_utils functions.

    This function reverses the monkey-patching done by apply_rich_patch().
    Can be called multiple times safely (idempotent).
    """
    global PATCH_STATE

    if not PATCH_STATE["applied"]:
        logger.debug("Rich patch not applied, nothing to undo")
        return

    try:
        import typer.rich_utils

        # Restore original functions
        originals = PATCH_STATE["originals"]
        for func_name, original_func in originals.items():
            setattr(typer.rich_utils, func_name, original_func)

        # Reset patch state
        PATCH_STATE.update(
            {
                "applied": False,
                "patched_functions": [],
                "originals": {},
            }
        )

        logger.info("Rich patch removed successfully")

    except Exception as e:
        logger.error(f"Failed to undo Rich patch: {e}", exc_info=True)


def is_patch_applied() -> bool:
    """Check if Rich patch is currently active.

    Returns:
        True if patch is applied, False otherwise
    """
    return PATCH_STATE["applied"]


def get_patch_info() -> Dict[str, Any]:
    """Get patch metadata for debugging.

    Returns:
        Dictionary with patch state information
    """
    return PATCH_STATE.copy()


def get_patch_status() -> str:
    """Get human-readable patch status.

    Returns:
        Status string describing current patch state
    """
    if PATCH_STATE["applied"]:
        version = PATCH_STATE.get("typer_version", "unknown")
        num_funcs = len(PATCH_STATE.get("patched_functions", []))
        return f"Applied (Typer {version}, {num_funcs} functions patched)"
    elif PATCH_STATE["skipped_reason"]:
        return f"Skipped: {PATCH_STATE['skipped_reason']}"
    else:
        return "Not applied"


# Auto-apply patch on module import (unless opted out)
_auto_apply = os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "1"
if _auto_apply and not PATCH_STATE["applied"]:  # pragma: no cover
    # Note: Actual auto-apply happens in __init__.py to avoid circular imports
    pass
