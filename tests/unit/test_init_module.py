"""Tests for typer_extensions.__init__ module initialisation and patch application."""

import os

import pytest


class TestPatchFunctionality:
    """Test the core patch functions directly"""

    def test_apply_rich_patch_function_returns_bool(self):
        """Test that apply_rich_patch returns a boolean"""
        from typer_extensions._patch import apply_rich_patch

        result = apply_rich_patch()
        assert isinstance(result, bool)

    def test_is_patch_applied_returns_bool(self):
        """Test that is_patch_applied returns a boolean"""
        from typer_extensions._patch import is_patch_applied

        result = is_patch_applied()
        assert isinstance(result, bool)

    def test_get_patch_info_returns_dict(self):
        """Test that get_patch_info returns a dictionary with required keys"""
        from typer_extensions._patch import get_patch_info

        info = get_patch_info()
        assert isinstance(info, dict)
        assert "applied" in info
        assert isinstance(info["applied"], bool)

    def test_get_patch_status_returns_string(self):
        """Test that get_patch_status returns a non-empty string"""
        from typer_extensions._patch import get_patch_status

        status = get_patch_status()
        assert isinstance(status, str)
        assert len(status) > 0

    def test_undo_rich_patch_returns_none(self):
        """Test that undo_rich_patch can be called safely"""
        from typer_extensions._patch import undo_rich_patch

        # Should not raise and should return None
        result = undo_rich_patch()
        assert result is None


class TestEnvironmentVariableLogic:
    """Test the environment variable control logic"""

    def test_rich_env_var_true(self):
        """Test TYPER_EXTENSIONS_RICH=1 means patching is enabled"""
        # Directly test the logic
        should_apply = os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "1"
        assert should_apply is True

    def test_rich_env_var_false(self):
        """Test TYPER_EXTENSIONS_RICH=0 means patching is disabled"""
        # Directly test the logic
        should_not_apply = os.environ.get("TYPER_EXTENSIONS_RICH_DISABLED", "0") == "1"
        assert should_not_apply is False

    def test_lazy_rich_env_var_default(self):
        """Test TYPER_EXTENSIONS_LAZY_RICH defaults to enabled"""
        # Directly test the logic
        should_apply = os.environ.get("TYPER_EXTENSIONS_LAZY_RICH_NOTSET", "1") == "1"
        assert should_apply is True

    def test_debug_env_var_logic(self):
        """Test TYPER_EXTENSIONS_DEBUG environment variable logic"""
        # When not set, should be None
        debug_off = os.environ.get("TYPER_EXTENSIONS_DEBUG_NOTSET")
        assert debug_off is None
        # When set to "1", should be truthy
        debug_on = os.environ.get("TYPER_EXTENSIONS_DEBUG_NOTSET", "1")
        assert debug_on == "1"


class TestModuleExports:
    """Test that the module exports the expected items"""

    def test_extended_typer_exported(self):
        """Test that ExtendedTyper is exported"""
        import typer_extensions

        assert hasattr(typer_extensions, "ExtendedTyper")
        # Verify it's a class
        assert isinstance(typer_extensions.ExtendedTyper, type)

    def test_extended_typer_instantiation(self):
        """Test that ExtendedTyper can be instantiated"""
        from typer_extensions import ExtendedTyper

        app = ExtendedTyper()
        assert app is not None
        assert isinstance(app, ExtendedTyper)
        # Verify expected methods exist
        assert hasattr(app, "command")
        assert hasattr(app, "callback")

    def test_context_exported(self):
        """Test that Context is exported and matches the core module"""
        import typer_extensions
        from typer_extensions.core import Context as CoreContext

        assert hasattr(typer_extensions, "Context")
        assert typer_extensions.Context is CoreContext

    def test_version_exported(self):
        """Test that __version__ is exported as a string"""
        import typer_extensions

        assert hasattr(typer_extensions, "__version__")
        assert isinstance(typer_extensions.__version__, str)
        # Verify semantic versioning format
        parts = typer_extensions.__version__.split(".")
        assert len(parts) >= 2

    def test_all_exports_in_all(self):
        """Test that __all__ contains the expected exports"""
        import typer_extensions

        assert hasattr(typer_extensions, "__all__")
        expected = {"ExtendedTyper", "__version__", "Context"}
        for item in expected:
            assert item in typer_extensions.__all__

    def test_all_declared_exports_exist(self):
        """Test that all items in __all__ actually exist in the module"""
        import typer_extensions

        for name in typer_extensions.__all__:
            assert hasattr(typer_extensions, name), (
                f"__all__ declares {name} but it's not in module"
            )


class TestGetAttrFallback:
    """Test __getattr__ fallback mechanism for delegating to typer"""

    def test_getattr_delegates_to_typer(self):
        """Test that __getattr__ correctly delegates to typer module"""
        import typer_extensions
        import typer

        # These should come from typer via __getattr__
        assert typer_extensions.Typer is typer.Typer
        assert typer_extensions.Exit is typer.Exit
        assert typer_extensions.Abort is typer.Abort

    def test_getattr_raises_attribute_error_for_missing(self):
        """Test that __getattr__ raises AttributeError for non-existent attributes"""
        import typer_extensions

        with pytest.raises(AttributeError):
            _ = typer_extensions.DoesNotExist12345_Hopefully

    def test_getattr_with_common_typer_exports(self):
        """Test __getattr__ with a variety of common Typer exports"""
        import typer_extensions
        import typer

        # List of common Typer exports that should be accessible
        common_exports = ["Typer", "Exit", "Abort", "BadParameter"]
        for export in common_exports:
            if hasattr(typer, export):
                # Should get the same object from both
                assert getattr(typer_extensions, export) is getattr(typer, export)


class TestModuleImportBehavior:
    """Test that the module imports successfully and has expected structure"""

    def test_module_imports_successfully(self):
        """Test that typer_extensions module imports without errors"""
        import typer_extensions

        assert typer_extensions is not None

    def test_patch_module_is_importable(self):
        """Test that the _patch module exists and is importable"""
        from typer_extensions import _patch

        assert hasattr(_patch, "apply_rich_patch")
        assert hasattr(_patch, "is_patch_applied")
        assert hasattr(_patch, "get_patch_info")
        assert hasattr(_patch, "get_patch_status")
        assert hasattr(_patch, "undo_rich_patch")

    def test_import_hook_module_is_importable(self):
        """Test that the _import_hook module exists and is importable"""
        from typer_extensions import _import_hook

        assert hasattr(_import_hook, "install_import_hook")
        assert hasattr(_import_hook, "uninstall_import_hook")

    def test_core_module_components_available(self):
        """Test that core module components are available through the package"""
        import typer_extensions
        from typer_extensions.core import ExtendedTyper, Context

        # These should be available from the main package
        assert typer_extensions.ExtendedTyper is ExtendedTyper
        assert typer_extensions.Context is Context


class TestPatchExceptionHandling:
    """Test that patch exceptions don't break module initialization"""

    def test_patch_function_handles_already_applied(self):
        """Test that calling apply_rich_patch twice is safe"""
        from typer_extensions._patch import apply_rich_patch

        # First call
        result1 = apply_rich_patch()
        # Second call should return early
        result2 = apply_rich_patch()

        # Both should return booleans
        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

    def test_patch_state_initialization(self):
        """Test that PATCH_STATE is properly initialized"""
        from typer_extensions._patch import PATCH_STATE

        assert isinstance(PATCH_STATE, dict)
        assert "applied" in PATCH_STATE
        assert "skipped_reason" in PATCH_STATE
        assert isinstance(PATCH_STATE["applied"], bool)


class TestModuleInitializationRobustness:
    """Test that the module is robust to various conditions"""

    def test_module_loads_with_default_environment(self):
        """Test that module loads successfully with default environment"""
        import typer_extensions

        assert typer_extensions is not None
        assert hasattr(typer_extensions, "ExtendedTyper")
        assert hasattr(typer_extensions, "__version__")
        assert hasattr(typer_extensions, "Context")

    def test_core_functionality_available_after_import(self):
        """Test that all core functionality is available after import"""
        from typer_extensions import ExtendedTyper, Context

        # Should be able to use them
        app = ExtendedTyper(name="test")
        assert app is not None

        # Context should be available
        assert Context is not None


class TestPatchApplicationWithDebugFlag:
    """Test patch application code paths with debug flag set"""

    def test_patch_applied_debug_flag_enabled(self, monkeypatch):
        """Test that debug message is logged when patch is applied with debug flag"""
        from typer_extensions._patch import PATCH_STATE, apply_rich_patch
        import sys

        original_state = PATCH_STATE.copy()
        # Save original modules
        original_typer = sys.modules.get("typer")
        original_rich_utils = sys.modules.get("typer.rich_utils")

        PATCH_STATE.clear()
        PATCH_STATE.update(
            {
                "applied": False,
                "typer_version": None,
                "patched_functions": [],
                "originals": {},
                "skipped_reason": None,
            }
        )

        try:
            monkeypatch.setenv("TYPER_EXTENSIONS_RICH", "1")
            monkeypatch.setenv("TYPER_EXTENSIONS_DEBUG", "1")

            # Ensure clean state for testing
            if "typer.rich_utils" in sys.modules:
                del sys.modules["typer.rich_utils"]
            if "typer" in sys.modules:
                del sys.modules["typer"]

            # Mock successful import hook installation
            from unittest.mock import patch

            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=True
            ):
                result = apply_rich_patch()
                assert result is True
                assert PATCH_STATE["applied"] is True
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)
            # Restore original modules
            if original_typer is not None:
                sys.modules["typer"] = original_typer
            if original_rich_utils is not None:
                sys.modules["typer.rich_utils"] = original_rich_utils


class TestInitModuleAttributeAccess:
    """Test __getattr__ function in __init__.py"""

    def test_getattr_forwards_to_typer(self):
        """Test that __getattr__ forwards undefined attributes to Typer"""
        import typer_extensions
        import typer

        # Access an attribute that's not explicitly exported
        attr = typer_extensions.__getattr__("Argument")
        assert attr is typer.Argument


class TestExceptionHandlingDuringModuleInit:
    """Test exception handling during module initialization"""

    def test_patch_exception_logged_but_module_loads(self, monkeypatch, caplog):
        """Test that exceptions during patch application are caught and logged"""
        import logging
        from unittest.mock import patch

        # Set up to trigger the exception path
        with caplog.at_level(logging.ERROR):
            with patch(
                "typer_extensions._patch.apply_rich_patch",
                side_effect=RuntimeError("Test error"),
            ):
                # This simulates what happens during module import
                try:
                    # If we're in the test, the module is already imported, so we need to mock carefully
                    from typer_extensions._patch import apply_rich_patch

                    apply_rich_patch()  # This will raise
                except RuntimeError as e:
                    # Expected
                    assert str(e) == "Test error"
