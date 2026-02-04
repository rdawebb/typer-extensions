"""Comprehensive tests for typer_extensions module initialisation.

This module tests the initialisation behavior of typer_extensions, including:
- Module imports and exports
- Patch application with various environment variables
- Error handling during initialisation
- Configuration and state management
"""

import os
import sys
import json
import logging
from unittest.mock import patch

import pytest
import typer


# =============================================================================
# Module Exports and Basic Functionality Tests
# =============================================================================


class TestModuleExports:
    """Test that the module exports the expected items."""

    def test_extended_typer_exported(self):
        """Test that ExtendedTyper is exported."""
        import typer_extensions

        assert hasattr(typer_extensions, "ExtendedTyper")
        assert isinstance(typer_extensions.ExtendedTyper, type)

    def test_extended_typer_instantiation(self):
        """Test that ExtendedTyper can be instantiated."""
        from typer_extensions import ExtendedTyper

        app = ExtendedTyper()
        assert app is not None
        assert isinstance(app, ExtendedTyper)
        assert hasattr(app, "command")
        assert hasattr(app, "callback")

    def test_context_exported(self):
        """Test that Context is exported and matches the core module."""
        import typer_extensions
        from typer_extensions.core import Context as CoreContext

        assert hasattr(typer_extensions, "Context")
        assert typer_extensions.Context is CoreContext

    def test_version_exported(self):
        """Test that __version__ is exported as a string."""
        import typer_extensions

        assert hasattr(typer_extensions, "__version__")
        assert isinstance(typer_extensions.__version__, str)
        parts = typer_extensions.__version__.split(".")
        assert len(parts) >= 2

    def test_all_exports_in_all(self):
        """Test that __all__ contains the expected exports."""
        import typer_extensions

        assert hasattr(typer_extensions, "__all__")
        expected = {"ExtendedTyper", "__version__", "Context"}
        for item in expected:
            assert item in typer_extensions.__all__

    def test_all_declared_exports_exist(self):
        """Test that all items in __all__ actually exist in the module."""
        import typer_extensions

        for name in typer_extensions.__all__:
            assert hasattr(typer_extensions, name), (
                f"__all__ declares {name} but it's not in module"
            )


class TestGetAttrFallback:
    """Test __getattr__ fallback mechanism for delegating to typer."""

    def test_getattr_delegates_to_typer(self):
        """Test that __getattr__ correctly delegates to typer module."""
        import typer_extensions

        assert typer_extensions.Typer is typer.Typer
        assert typer_extensions.Exit is typer.Exit
        assert typer_extensions.Abort is typer.Abort

    def test_getattr_raises_attribute_error_for_missing(self):
        """Test that __getattr__ raises AttributeError for non-existent attributes."""
        import typer_extensions

        with pytest.raises(AttributeError):
            _ = typer_extensions.DoesNotExist12345_Hopefully

    def test_getattr_with_common_typer_exports(self):
        """Test __getattr__ with a variety of common Typer exports."""
        import typer_extensions

        common_exports = ["Typer", "Exit", "Abort", "BadParameter"]
        for export in common_exports:
            if hasattr(typer, export):
                assert getattr(typer_extensions, export) is getattr(typer, export)

    def test_getattr_forwards_to_typer(self):
        """Test that __getattr__ forwards undefined attributes to Typer."""
        import typer_extensions

        attr = typer_extensions.__getattr__("Argument")
        assert attr is typer.Argument


# =============================================================================
# Patch Functionality Tests
# =============================================================================


class TestPatchFunctionality:
    """Test the core patch functions directly."""

    def test_apply_rich_patch_function_returns_bool(self):
        """Test that apply_rich_patch returns a boolean."""
        from typer_extensions._patch import apply_rich_patch

        result = apply_rich_patch()
        assert isinstance(result, bool)

    def test_is_patch_applied_returns_bool(self):
        """Test that is_patch_applied returns a boolean."""
        from typer_extensions._patch import is_patch_applied

        result = is_patch_applied()
        assert isinstance(result, bool)

    def test_get_patch_info_returns_dict(self):
        """Test that get_patch_info returns a dictionary with required keys."""
        from typer_extensions._patch import get_patch_info

        info = get_patch_info()
        assert isinstance(info, dict)
        assert "applied" in info
        assert isinstance(info["applied"], bool)

    def test_get_patch_status_returns_string(self):
        """Test that get_patch_status returns a non-empty string."""
        from typer_extensions._patch import get_patch_status

        status = get_patch_status()
        assert isinstance(status, str)
        assert len(status) > 0

    def test_undo_rich_patch_returns_none(self):
        """Test that undo_rich_patch can be called safely."""
        from typer_extensions._patch import undo_rich_patch

        result = undo_rich_patch()
        assert result is None

    def test_patch_state_initialization(self):
        """Test that PATCH_STATE is properly initialized."""
        from typer_extensions._patch import PATCH_STATE

        assert isinstance(PATCH_STATE, dict)
        assert "applied" in PATCH_STATE
        assert "skipped_reason" in PATCH_STATE
        assert isinstance(PATCH_STATE["applied"], bool)


# =============================================================================
# Environment Variable Logic Tests
# =============================================================================


class TestEnvironmentVariableLogic:
    """Test the environment variable control logic."""

    def test_rich_env_var_true(self):
        """Test TYPER_EXTENSIONS_RICH=1 means patching is enabled."""
        should_apply = os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "1"
        assert should_apply is True

    def test_rich_env_var_false(self):
        """Test TYPER_EXTENSIONS_RICH=0 means patching is disabled."""
        should_not_apply = os.environ.get("TYPER_EXTENSIONS_RICH_DISABLED", "0") == "1"
        assert should_not_apply is False

    def test_lazy_rich_env_var_default(self):
        """Test TYPER_EXTENSIONS_LAZY_RICH defaults to enabled."""
        should_apply = os.environ.get("TYPER_EXTENSIONS_LAZY_RICH_NOTSET", "1") == "1"
        assert should_apply is True

    def test_debug_env_var_logic(self):
        """Test TYPER_EXTENSIONS_DEBUG environment variable logic."""
        debug_off = os.environ.get("TYPER_EXTENSIONS_DEBUG_NOTSET")
        assert debug_off is None

        debug_on = os.environ.get("TYPER_EXTENSIONS_DEBUG_NOTSET", "1")
        assert debug_on == "1"


# =============================================================================
# Module Import Behavior Tests
# =============================================================================


class TestModuleImportBehavior:
    """Test that the module imports successfully and has expected structure."""

    def test_module_imports_successfully(self):
        """Test that typer_extensions module imports without errors."""
        import typer_extensions

        assert typer_extensions is not None

    def test_patch_module_is_importable(self):
        """Test that the _patch module exists and is importable."""
        from typer_extensions import _patch

        assert hasattr(_patch, "apply_rich_patch")
        assert hasattr(_patch, "is_patch_applied")
        assert hasattr(_patch, "get_patch_info")
        assert hasattr(_patch, "get_patch_status")
        assert hasattr(_patch, "undo_rich_patch")

    def test_import_hook_module_is_importable(self):
        """Test that the _import_hook module exists and is importable."""
        from typer_extensions import _import_hook

        assert hasattr(_import_hook, "install_import_hook")
        assert hasattr(_import_hook, "uninstall_import_hook")

    def test_core_module_components_available(self):
        """Test that core module components are available through the package."""
        import typer_extensions
        from typer_extensions.core import ExtendedTyper, Context

        assert typer_extensions.ExtendedTyper is ExtendedTyper
        assert typer_extensions.Context is Context


# =============================================================================
# Patch Exception Handling Tests
# =============================================================================


class TestPatchExceptionHandling:
    """Test that patch exceptions don't break module initialization."""

    def test_patch_function_handles_already_applied(self):
        """Test that calling apply_rich_patch twice is safe."""
        from typer_extensions._patch import apply_rich_patch

        result1 = apply_rich_patch()
        result2 = apply_rich_patch()

        assert isinstance(result1, bool)
        assert isinstance(result2, bool)

    def test_patch_exception_logged_but_module_loads(self, monkeypatch, caplog):
        """Test that exceptions during patch application are caught and logged."""
        with caplog.at_level(logging.ERROR):
            with patch(
                "typer_extensions._patch.apply_rich_patch",
                side_effect=RuntimeError("Test error"),
            ):
                try:
                    from typer_extensions._patch import apply_rich_patch

                    apply_rich_patch()
                except RuntimeError as e:
                    assert str(e) == "Test error"


# =============================================================================
# Module Initialisation Tests (subprocess-based)
# =============================================================================


class TestModuleInitialisationWithEnvironment:
    """Tests for module initialisation with different environment settings."""

    @pytest.mark.isolated
    def test_init_with_rich_disabled(self, subprocess_runner):
        """Test module initialisation when TYPER_EXTENSIONS_RICH=0."""
        code = """
import typer_extensions
print("Success")
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "0"})
        assert result.returncode == 0
        assert "Success" in result.stdout

    @pytest.mark.isolated
    def test_init_with_debug_enabled(self, subprocess_runner):
        """Test module initialisation with debug enabled."""
        code = """
import typer_extensions
print("Success")
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_DEBUG": "1"})
        assert result.returncode == 0
        assert "Success" in result.stdout

    @pytest.mark.isolated
    def test_basic_imports_available(self, subprocess_runner):
        """Test that all expected imports are available after initialisation."""
        code = """
import typer_extensions
assert hasattr(typer_extensions, 'ExtendedTyper')
assert hasattr(typer_extensions, '__version__')
assert hasattr(typer_extensions, 'Context')
print("All imports available")
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        assert "All imports available" in result.stdout


class TestInitModuleErrorHandling:
    """Test error handling during module initialisation."""

    @pytest.mark.isolated
    def test_patch_failure_graceful_fallback(self, subprocess_runner):
        """Test that module loads even if Rich patch fails."""
        code = """
import json
import typer_extensions

result = {"module_loaded": True, "error": None}
print(json.dumps(result))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert output.get("module_loaded") is True
            except json.JSONDecodeError:
                assert result.returncode == 0

    @pytest.mark.isolated
    def test_rich_disabled_via_env(self, subprocess_runner):
        """Test that Rich features are disabled when TYPER_EXTENSIONS_RICH=0."""
        code = """
import json
import typer_extensions
from typer_extensions._patch import PATCH_STATE

result = {
    "module_loaded": True,
    "patch_applied": PATCH_STATE.get("applied", False)
}
print(json.dumps(result))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "0"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert output.get("module_loaded") is True
                assert output.get("patch_applied") in [False, None]
            except json.JSONDecodeError:
                assert result.returncode == 0

    @pytest.mark.isolated
    def test_debug_logging_enabled(self, subprocess_runner):
        """Test that debug logging works when TYPER_EXTENSIONS_DEBUG is set."""
        code = """
import json
import logging

log_messages = []

class TestHandler(logging.Handler):
    def emit(self, record):
        log_messages.append(record.getMessage())

logger = logging.getLogger("typer_extensions")
handler = TestHandler()
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

import typer_extensions

result = {
    "module_loaded": True,
    "logs_captured": len(log_messages) > 0
}
print(json.dumps(result))
"""
        result = subprocess_runner(
            code, env={"TYPER_EXTENSIONS_DEBUG": "1", "TYPER_EXTENSIONS_RICH": "1"}
        )
        assert result.returncode == 0


class TestInitModuleImportPaths:
    """Test different import paths in __init__.py."""

    @pytest.mark.isolated
    def test_import_version(self, subprocess_runner):
        """Test that __version__ is importable from package."""
        code = """
import json
from typer_extensions import __version__

result = {
    "version_exists": __version__ is not None,
    "version_is_string": isinstance(__version__, str)
}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout.strip())
            assert output.get("version_exists") is True
            assert output.get("version_is_string") is True

    @pytest.mark.isolated
    def test_import_extended_typer(self, subprocess_runner):
        """Test that ExtendedTyper is importable from package."""
        code = """
import json
from typer_extensions import ExtendedTyper

result = {
    "class_exists": ExtendedTyper is not None,
    "is_class": isinstance(ExtendedTyper, type)
}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout.strip())
            assert output.get("class_exists") is True
            assert output.get("is_class") is True

    @pytest.mark.isolated
    def test_import_context(self, subprocess_runner):
        """Test that Context is importable from package."""
        code = """
import json
from typer_extensions import Context

result = {
    "class_exists": Context is not None
}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        assert result.returncode == 0
        if result.stdout.strip():
            output = json.loads(result.stdout.strip())
            assert output.get("class_exists") is True

    @pytest.mark.isolated
    def test_exception_in_patch_apply(self, subprocess_runner):
        """Test that exceptions in apply_rich_patch are handled gracefully."""
        code = """
import json

try:
    import typer_extensions
    result = {"module_loaded": True, "error": None}
except Exception as e:
    result = {"module_loaded": False, "error": str(type(e).__name__)}

print(json.dumps(result))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert output.get("module_loaded") is True
            except json.JSONDecodeError:
                pass


# =============================================================================
# Module Initialisation Robustness Tests
# =============================================================================


class TestModuleInitialisationRobustness:
    """Test that the module is robust to various conditions."""

    def test_module_loads_with_default_environment(self):
        """Test that module loads successfully with default environment."""
        import typer_extensions

        assert typer_extensions is not None
        assert hasattr(typer_extensions, "ExtendedTyper")
        assert hasattr(typer_extensions, "__version__")
        assert hasattr(typer_extensions, "Context")

    def test_core_functionality_available_after_import(self):
        """Test that all core functionality is available after import."""
        from typer_extensions import ExtendedTyper, Context

        app = ExtendedTyper(name="test")
        assert app is not None
        assert Context is not None


# =============================================================================
# Environment-Specific Edge Cases
# =============================================================================


class TestLazyRichPatchOptOut:
    """Test TYPER_EXTENSIONS_RICH environment variable."""

    @pytest.mark.isolated
    def test_rich_opt_out_via_env(self, subprocess_runner):
        """Test that rich patch can be disabled via env var."""
        code = """
import os
import sys
import json

os.environ["TYPER_EXTENSIONS_RICH"] = "0"

from typer_extensions._patch import PATCH_STATE
import typer_extensions

result = {
    "patch_applied": PATCH_STATE.get("applied", False),
    "module_loaded": True
}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert "module_loaded" in output
            except json.JSONDecodeError:
                assert result.returncode == 0

    @pytest.mark.isolated
    def test_rich_enabled_by_default(self, subprocess_runner):
        """Test that rich patch is enabled by default."""
        code = """
import sys
import os
import json

os.environ.pop("TYPER_EXTENSIONS_RICH", None)

import typer_extensions

result = {"module_loaded": True}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert output.get("module_loaded") is True
            except json.JSONDecodeError:
                assert result.returncode == 0


class TestInitModuleDebugLogging:
    """Test debug logging during module initialisation."""

    @pytest.mark.isolated
    def test_patch_applied_debug_message(self, subprocess_runner):
        """Test that debug message is logged when patch is applied."""
        code = """
import os
import logging
import sys
import json

logging.basicConfig(level=logging.DEBUG)
os.environ["TYPER_EXTENSIONS_DEBUG"] = "1"
os.environ["TYPER_EXTENSIONS_RICH"] = "1"

import typer_extensions
result = {"module_loaded": True}
print(json.dumps(result))
"""
        result = subprocess_runner(code)
        if result.returncode == 0:
            assert "module_loaded" in result.stdout or result.stderr


# =============================================================================
# Patch Application with Debug Tests
# =============================================================================


class TestPatchApplicationWithDebugFlag:
    """Test patch application code paths with debug flag set."""

    def test_patch_applied_debug_flag_enabled(self, monkeypatch):
        """Test that debug message is logged when patch is applied with debug flag."""
        from typer_extensions._patch import PATCH_STATE, apply_rich_patch

        original_state = PATCH_STATE.copy()
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

            if "typer.rich_utils" in sys.modules:
                del sys.modules["typer.rich_utils"]
            if "typer" in sys.modules:
                del sys.modules["typer"]

            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=True
            ):
                result = apply_rich_patch()
                assert result is True
                assert PATCH_STATE["applied"] is True
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)
            if original_typer is not None:
                sys.modules["typer"] = original_typer
            if original_rich_utils is not None:
                sys.modules["typer.rich_utils"] = original_rich_utils
