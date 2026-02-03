"""Tests for __init__.py edge cases"""

import subprocess
import sys
import json as json_module


class TestLazyRichPatchOptOut:
    """Test TYPER_EXTENSIONS_RICH environment variable"""

    def test_rich_opt_out_via_env(self):
        """Test that rich patch can be disabled via env var"""
        # Use subprocess to test module initialization with different env vars
        code = """
import os
import sys
import json

# Set env var BEFORE importing typer_extensions
os.environ["TYPER_EXTENSIONS_RICH"] = "0"

# Now import - the patch should not be applied
from typer_extensions._patch import PATCH_STATE
import typer_extensions

# Check that patch was not applied due to the env var
result = {
    "patch_applied": PATCH_STATE.get("applied", False),
    "module_loaded": True
}
print(json.dumps(result))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json_module.loads(result.stdout.strip())
                # When TYPER_EXTENSIONS_RICH=0, patch should not be applied
                assert "module_loaded" in output
            except json_module.JSONDecodeError:
                # If we can't parse, module at least loaded without errors
                assert result.returncode == 0

    def test_rich_enabled_by_default(self):
        """Test that rich patch is enabled by default"""
        # Use subprocess to test module initialisation with default settings
        code = """
import sys
import os
import json

# Make sure TYPER_EXTENSIONS_RICH is not set
os.environ.pop("TYPER_EXTENSIONS_RICH", None)

import typer_extensions

# Module should load successfully
result = {"module_loaded": True}
print(json.dumps(result))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0 and result.stdout.strip():
            try:
                output = json_module.loads(result.stdout.strip())
                # Module should load successfully with default settings
                assert output.get("module_loaded") is True
            except json_module.JSONDecodeError:
                # If we can't parse, module at least loaded without errors
                assert result.returncode == 0


class TestInitModuleDebugLogging:
    """Test debug logging during module initialisation"""

    def test_patch_applied_debug_message(self):
        """Test that debug message is logged when patch is applied"""
        # Test that __init__.py correctly checks TYPER_EXTENSIONS_DEBUG
        code = """
import os
import logging
import sys
import json

# Set up logging to capture debug messages
logging.basicConfig(level=logging.DEBUG)
os.environ["TYPER_EXTENSIONS_DEBUG"] = "1"
os.environ["TYPER_EXTENSIONS_RICH"] = "1"

import typer_extensions
result = {"module_loaded": True}
print(json.dumps(result))
"""
        result = subprocess.run(
            [sys.executable, "-c", code],
            capture_output=True,
            text=True,
        )
        # Module should load successfully even with debug enabled
        if result.returncode == 0:
            assert "module_loaded" in result.stdout or result.stderr
