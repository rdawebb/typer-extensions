"""Robust import hook-based patching for enhanced Rich loading."""

import logging
import os
import sys
from importlib.abc import Loader, MetaPathFinder
from importlib.machinery import ModuleSpec
from types import ModuleType
from typing import Optional, Sequence

logger = logging.getLogger(__name__)


class TyperRichUtilsInterceptor(MetaPathFinder, Loader):
    """Import hook that intercepts typer.rich_utils with enhanced version."""

    def __init__(self):
        """Initialise the interceptor."""
        self._loaded = False
        self._our_module = None

    def find_spec(
        self,
        fullname: str,
        path: Optional[Sequence[str]],
        target: Optional[ModuleType] = None,
    ) -> Optional[ModuleSpec]:
        """Find module spec for typer.rich_utils.

        Args:
            fullname: The fully qualified name of the module.
            path: The search path for the module.
            target: The target module (if any).

        Returns:
            The module spec for typer.rich_utils, or None if not found.
        """
        if fullname == "typer.rich_utils":
            spec = ModuleSpec(
                name="typer.rich_utils",
                loader=self,
                origin="typer_extensions._rich_utils (enhanced)",
                is_package=False,
            )
            spec.submodule_search_locations = None
            return spec
        return None

    def create_module(self, spec: ModuleSpec) -> Optional[ModuleType]:
        """Create the module object.

        Args:
            spec: The module spec.

        Returns:
            The created module object, or None to use default module creation.
        """
        return None

    def exec_module(self, module: ModuleType) -> None:
        """Execute the module - load enhanced version.

        Args:
            module: The module to execute.
        """
        if self._loaded and self._our_module is not None:
            module.__dict__.update(self._our_module.__dict__)
            return

        try:
            from typer_extensions import _rich_utils

            # Copy all attributes and fix module metadata
            module.__dict__.update(_rich_utils.__dict__)
            module.__name__ = "typer.rich_utils"
            module.__package__ = "typer"
            module.__file__ = _rich_utils.__file__

            # Cache it
            self._our_module = module
            self._loaded = True

            if os.environ.get("TYPER_EXTENSIONS_DEBUG"):
                logger.info("Rich utils loaded via import hook")

        except Exception as e:
            logger.error(f"Failed to load _rich_utils: {e}", exc_info=True)
            raise

    # Backwards compatibility for Python < 3.10
    def find_module(
        self, fullname: str, path: Optional[Sequence[str]] = None
    ) -> Optional[Loader]:
        """Older import protocol support.

        Args:
            fullname: The fully qualified name of the module.
            path: The search path for the module.

        Returns:
            The loader for the module, or None if not found.
        """
        if fullname == "typer.rich_utils":
            return self
        return None

    def load_module(self, fullname: str) -> ModuleType:
        """Older import protocol support.

        Args:
            fullname: The fully qualified name of the module.
            path: The search path for the module.

        Returns:
            The loader for the module, or None if not found.
        """
        if fullname == "typer.rich_utils":
            if fullname in sys.modules:
                return sys.modules[fullname]

            # Create module
            module = ModuleType(fullname)
            sys.modules[fullname] = module

            self.exec_module(module)
            return module

        raise ImportError(f"Cannot load {fullname}")


def install_import_hook() -> bool:
    """Install the import hook to intercept typer.rich_utils.

    Returns:
        True if hook installed successfully, False otherwise
    """
    if "typer.rich_utils" in sys.modules:
        logger.warning("typer.rich_utils already imported - cannot install hook")
        return False

    try:
        for finder in sys.meta_path:
            if isinstance(finder, TyperRichUtilsInterceptor):
                logger.debug("Import hook already installed")
                return True

        # Install at the beginning of meta_path for priority
        hook = TyperRichUtilsInterceptor()
        sys.meta_path.insert(0, hook)

        if os.environ.get("TYPER_EXTENSIONS_DEBUG"):
            logger.info("Import hook installed successfully")

        return True

    except Exception as e:
        logger.error(f"Failed to install import hook: {e}", exc_info=True)
        return False


def uninstall_import_hook() -> bool:
    """Remove the import hook.

    Returns:
        True if hook removed, False if not found
    """
    removed = False
    for finder in list(sys.meta_path):
        if isinstance(finder, TyperRichUtilsInterceptor):
            sys.meta_path.remove(finder)
            removed = True

    if removed and os.environ.get("TYPER_EXTENSIONS_DEBUG"):
        logger.info("Import hook uninstalled")

    return removed
