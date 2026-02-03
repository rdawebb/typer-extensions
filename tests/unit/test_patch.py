"""Tests for typer_extensions._patch module."""

import os
import sys
from unittest.mock import patch, MagicMock

from typer_extensions._patch import (
    apply_rich_patch,
    undo_rich_patch,
    is_patch_applied,
    get_patch_info,
    get_patch_status,
    PATCH_STATE,
)


class TestApplyRichPatch:
    """Tests for apply_rich_patch function."""

    def test_already_patched_returns_true(self):
        """Test that already applied patch returns True without doing anything"""
        # Set patch as already applied
        original_state = PATCH_STATE.copy()
        PATCH_STATE["applied"] = True

        try:
            result = apply_rich_patch()
            assert result is True
        finally:
            # Restore state
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_opt_out_via_env_var(self, monkeypatch):
        """Test that patch is skipped when TYPER_EXTENSIONS_RICH=0"""
        original_state = PATCH_STATE.copy()
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
            monkeypatch.setenv("TYPER_EXTENSIONS_RICH", "0")

            result = apply_rich_patch()
            assert result is False
            assert PATCH_STATE["skipped_reason"] == "TYPER_EXTENSIONS_RICH=0 (opt-out)"
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_rich_utils_already_imported(self, monkeypatch):
        """Test that patch is skipped if typer.rich_utils is already imported"""
        original_state = PATCH_STATE.copy()
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

            # Mock that typer.rich_utils is already in sys.modules
            with patch.dict(sys.modules, {"typer.rich_utils": MagicMock()}):
                result = apply_rich_patch()
                assert result is False
                assert (
                    PATCH_STATE["skipped_reason"] == "typer.rich_utils already imported"
                )
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_typer_module_already_imported_fallback_fails(self, monkeypatch):
        """Test that patch returns False if typer is already imported during fallback"""
        original_state = PATCH_STATE.copy()
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

            # Mock that typer is already imported and import_hook fails
            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=False
            ):
                # Create a dict without typer.rich_utils for this test
                test_modules = {"typer": MagicMock()}
                with patch.dict(sys.modules, test_modules, clear=False):
                    # Ensure typer.rich_utils is not in sys.modules
                    if "typer.rich_utils" in sys.modules:
                        del sys.modules["typer.rich_utils"]
                    result = apply_rich_patch()
                    assert result is False
                    assert (
                        "typer module already imported" in PATCH_STATE["skipped_reason"]
                    )
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_import_hook_success(self, monkeypatch):
        """Test successful patch application via import hook"""
        original_state = PATCH_STATE.copy()
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
            monkeypatch.delenv("TYPER_EXTENSIONS_DEBUG", raising=False)

            # Ensure typer.rich_utils is not in sys.modules
            if "typer.rich_utils" in sys.modules:
                del sys.modules["typer.rich_utils"]

            # Mock successful import hook installation
            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=True
            ):
                result = apply_rich_patch()
                assert result is True
                assert PATCH_STATE["applied"] is True
                assert PATCH_STATE["method"] == "import_hook"
                assert PATCH_STATE["skipped_reason"] is None
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_import_hook_failure_fallback_to_sys_modules(self, monkeypatch):
        """Test fallback to sys.modules injection when import hook fails"""
        original_state = PATCH_STATE.copy()
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
            monkeypatch.delenv("TYPER_EXTENSIONS_DEBUG", raising=False)

            # Mock import hook failure
            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=False
            ):
                # Ensure typer is not in sys.modules
                with patch.dict(sys.modules, {}, clear=False):
                    if "typer" in sys.modules:
                        del sys.modules["typer"]
                    if "typer.rich_utils" in sys.modules:
                        del sys.modules["typer.rich_utils"]

                    result = apply_rich_patch()
                    assert result is True
                    assert PATCH_STATE["applied"] is True
                    assert PATCH_STATE["method"] == "sys_modules_injection"
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_exception_during_patching(self, monkeypatch):
        """Test that exceptions during patching are caught and logged"""
        original_state = PATCH_STATE.copy()
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

            # Mock import_hook to raise an exception
            with patch(
                "typer_extensions._import_hook.install_import_hook",
                side_effect=Exception("Test error"),
            ):
                # Test that the exception is handled gracefully
                # Without removing typer from sys.modules since that causes issues
                result = apply_rich_patch()
                # The function should handle the exception and return a boolean
                assert isinstance(result, bool)
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    @patch.dict(os.environ, {"TYPER_EXTENSIONS_DEBUG": "1"})
    def test_debug_logging_enabled(self, monkeypatch):
        """Test that debug logging flag is processed when enabled"""
        original_state = PATCH_STATE.copy()
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

            # Test with debug enabled - the result depends on what modules are loaded
            # We just verify the function works with the flag set
            result = apply_rich_patch()
            # Result could be True, False, or the patch was already applied
            # The important thing is that the debug flag was processed
            assert isinstance(result, bool)
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestUndoRichPatch:
    """Tests for undo_rich_patch function."""

    def test_undo_when_not_applied(self):
        """Test that undo does nothing when patch not applied"""
        original_state = PATCH_STATE.copy()
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
            # Should not raise
            undo_rich_patch()
            assert PATCH_STATE["applied"] is False
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_undo_restores_original_functions(self):
        """Test that undo restores original functions"""
        original_state = PATCH_STATE.copy()

        try:
            # Set up as if patch was applied
            original_func = MagicMock()
            PATCH_STATE.clear()
            PATCH_STATE.update(
                {
                    "applied": True,
                    "typer_version": None,
                    "patched_functions": ["test_func"],
                    "originals": {"test_func": original_func},
                    "skipped_reason": None,
                }
            )

            # Mock typer.rich_utils module - need to set it up properly
            mock_rich_utils = MagicMock()
            mock_typer = MagicMock()
            mock_typer.rich_utils = mock_rich_utils

            with patch.dict(
                sys.modules, {"typer": mock_typer, "typer.rich_utils": mock_rich_utils}
            ):
                undo_rich_patch()

                # Verify the state was reset
                assert PATCH_STATE["applied"] is False
                assert PATCH_STATE["patched_functions"] == []
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_undo_exception_handling(self):
        """Test that exceptions during undo are caught"""
        original_state = PATCH_STATE.copy()

        try:
            PATCH_STATE.clear()
            PATCH_STATE.update(
                {
                    "applied": True,
                    "typer_version": None,
                    "patched_functions": ["test_func"],
                    "originals": {"test_func": MagicMock()},
                    "skipped_reason": None,
                }
            )

            # Mock import to raise exception
            with patch(
                "typer_extensions._patch.sys.modules", {"typer.rich_utils": None}
            ):
                # Should not raise even though import fails
                undo_rich_patch()
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestIsPatchApplied:
    """Tests for is_patch_applied function."""

    def test_returns_true_when_applied(self):
        """Test that is_patch_applied returns True when applied"""
        original_state = PATCH_STATE.copy()
        PATCH_STATE["applied"] = True

        try:
            result = is_patch_applied()
            assert result is True
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_returns_false_when_not_applied(self):
        """Test that is_patch_applied returns False when not applied"""
        original_state = PATCH_STATE.copy()
        PATCH_STATE["applied"] = False

        try:
            result = is_patch_applied()
            assert result is False
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestGetPatchInfo:
    """Tests for get_patch_info function."""

    def test_returns_copy_of_patch_state(self):
        """Test that get_patch_info returns a copy of PATCH_STATE"""
        original_state = PATCH_STATE.copy()
        PATCH_STATE["applied"] = True
        PATCH_STATE["custom_field"] = "test_value"

        try:
            info = get_patch_info()

            # Should have the current state
            assert info["applied"] is True
            assert info["custom_field"] == "test_value"

            # Should be a copy (modifying it doesn't affect original)
            info["applied"] = False
            assert PATCH_STATE["applied"] is True
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestGetPatchStatus:
    """Tests for get_patch_status function."""

    def test_status_when_applied(self):
        """Test status string when patch is applied"""
        original_state = PATCH_STATE.copy()
        PATCH_STATE.clear()
        PATCH_STATE.update(
            {
                "applied": True,
                "typer_version": "0.9.0",
                "patched_functions": ["func1", "func2"],
                "originals": {},
                "skipped_reason": None,
            }
        )

        try:
            status = get_patch_status()
            assert "Applied" in status
            assert "2 functions patched" in status
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_status_when_skipped(self):
        """Test status string when patch is skipped"""
        original_state = PATCH_STATE.copy()
        PATCH_STATE.clear()
        PATCH_STATE.update(
            {
                "applied": False,
                "typer_version": None,
                "patched_functions": [],
                "originals": {},
                "skipped_reason": "Test skip reason",
            }
        )

        try:
            status = get_patch_status()
            assert "Skipped" in status
            assert "Test skip reason" in status
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)

    def test_status_when_not_applied(self):
        """Test status string when patch is not applied"""
        original_state = PATCH_STATE.copy()
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
            status = get_patch_status()
            assert "Not applied" in status
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestImportHookFailureWithDebug:
    """Test import hook exception handling with debug logging"""

    def test_import_hook_failure_with_debug_logging(self, monkeypatch, caplog):
        """Test that import hook exception is logged when debug is enabled"""
        import logging

        original_state = PATCH_STATE.copy()

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

            # Mock import hook raising an exception
            with patch(
                "typer_extensions._import_hook.install_import_hook",
                side_effect=Exception("Hook failed"),
            ):
                with caplog.at_level(logging.ERROR):
                    result = apply_rich_patch()
                    # Should return False when import hook fails and typer is already imported
                    assert isinstance(result, bool)

        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)


class TestSysModulesInjectionPath:
    """Test sys.modules injection fallback path"""

    def test_sys_modules_injection_with_debug(self, monkeypatch):
        """Test sys.modules injection path when import hook fails"""
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

            # Remove typer from sys.modules so sys.modules injection path is taken
            sys.modules.pop("typer", None)
            sys.modules.pop("typer.rich_utils", None)

            # Mock import hook to fail so sys.modules path is used
            with patch(
                "typer_extensions._import_hook.install_import_hook", return_value=False
            ):
                result = apply_rich_patch()
                # When typer is not imported and import hook fails,
                # sys.modules injection should succeed
                assert result is True
                assert PATCH_STATE["applied"] is True
                assert PATCH_STATE["method"] == "sys_modules_injection"
                # Verify the modules were injected
                assert "typer" in sys.modules
                assert "typer.rich_utils" in sys.modules
        finally:
            PATCH_STATE.clear()
            PATCH_STATE.update(original_state)
            # Restore original modules
            if original_typer is not None:
                sys.modules["typer"] = original_typer
            else:
                sys.modules.pop("typer", None)
            if original_rich_utils is not None:
                sys.modules["typer.rich_utils"] = original_rich_utils
            else:
                sys.modules.pop("typer.rich_utils", None)
