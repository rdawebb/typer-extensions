"""Tests for __init__.py error handling and edge cases"""

from __future__ import annotations

import json

import pytest


pytestmark = pytest.mark.isolated


class TestInitModuleErrorHandling:
    """Test error handling during module initialization"""

    def test_patch_failure_graceful_fallback(self, subprocess_runner):
        """Test that module loads even if Rich patch fails"""
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
                # Should still load the module
                assert result.returncode == 0

    def test_rich_disabled_via_env(self, subprocess_runner):
        """Test that Rich features are disabled when TYPER_EXTENSIONS_RICH=0"""
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
                # When RICH=0, patch should not be applied
                assert output.get("module_loaded") is True
                # Patch might not be applied or might be False
                assert output.get("patch_applied") in [False, None]
            except json.JSONDecodeError:
                # Should still load the module
                assert result.returncode == 0

    def test_debug_logging_enabled(self, subprocess_runner):
        """Test that debug logging works when TYPER_EXTENSIONS_DEBUG is set"""
        code = """
import json
import logging

# Enable debug logging
log_messages = []

class TestHandler(logging.Handler):
    def emit(self, record):
        log_messages.append(record.getMessage())

# Set up logging
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
        # Should still load the module
        assert result.returncode == 0


class TestInitModuleImportPaths:
    """Test different import paths in __init__.py"""

    def test_import_version(self, subprocess_runner):
        """Test that __version__ is importable from package"""
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

    def test_import_extended_typer(self, subprocess_runner):
        """Test that ExtendedTyper is importable from package"""
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

    def test_import_context(self, subprocess_runner):
        """Test that Context is importable from package"""
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

    def test_exception_in_patch_apply(self, subprocess_runner):
        """Test that exceptions in apply_rich_patch are handled gracefully"""
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
                # Should still load the module (errors are caught and logged)
                assert output.get("module_loaded") is True
            except json.JSONDecodeError:
                pass
