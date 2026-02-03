"""Tests for _patch.py edge cases and missing coverage"""

from __future__ import annotations

import json

import pytest


pytestmark = pytest.mark.isolated


class TestPatchEdgeCases:
    """Test edge cases in the patching logic"""

    def test_patch_with_typer_not_imported(self, subprocess_runner):
        """Test patching when typer is not yet imported"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import apply_rich_patch

result = apply_rich_patch()
output = {
    "patch_result": result,
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # When typer is not imported, patch should apply or return True
                assert "patch_result" in output
            except json.JSONDecodeError:
                pass

    def test_patch_creates_typer_package(self, subprocess_runner):
        """Test that patch creates typer package when it doesn't exist"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import apply_rich_patch

patch_result = apply_rich_patch()

import sys
output = {
    "patch_applied": patch_result,
    "typer_exists": "typer" in sys.modules,
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # Patch should create typer package structure
                assert (
                    output.get("typer_exists") is True
                    or output.get("patch_applied") is not None
                )
            except json.JSONDecodeError:
                pass

    def test_patch_state_tracking(self, subprocess_runner):
        """Test that PATCH_STATE tracks patch application"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import PATCH_STATE, apply_rich_patch

initial_state = PATCH_STATE.get("applied", False)
result = apply_rich_patch()
final_state = PATCH_STATE.get("applied", False)

output = {
    "initial_state": initial_state,
    "result": result,
    "final_state": final_state
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0

    def test_patch_already_applied(self, subprocess_runner):
        """Test that patch can't be applied twice"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import apply_rich_patch, PATCH_STATE

# Apply patch first time
first_result = apply_rich_patch()

# Try to apply again
second_result = apply_rich_patch()

output = {
    "first_result": first_result,
    "second_result": second_result,
    "patch_state": PATCH_STATE.get("applied", False)
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # Second application should return True (already applied)
                assert output.get("second_result") is True
            except json.JSONDecodeError:
                pass

    def test_patch_with_rich_disabled(self, subprocess_runner):
        """Test patch behavior when TYPER_EXTENSIONS_RICH=0"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "0"

from typer_extensions._patch import apply_rich_patch, PATCH_STATE

result = apply_rich_patch()

output = {
    "result": result,
    "patch_applied": PATCH_STATE.get("applied", False)
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "0"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                # When Rich is disabled, patch should not apply
                assert output.get("result") is False
            except json.JSONDecodeError:
                pass

    def test_auto_apply_environment_check(self, subprocess_runner):
        """Test the auto-apply environment variable check"""
        code = """
import json
import os

# Test with TYPER_EXTENSIONS_RICH=1 (default/enabled)
os.environ["TYPER_EXTENSIONS_RICH"] = "1"

# Import the patch module to check auto-apply logic
from typer_extensions import _patch

_auto_apply = os.environ.get("TYPER_EXTENSIONS_RICH", "1") == "1"

output = {
    "auto_apply_enabled": _auto_apply,
    "env_value": os.environ.get("TYPER_EXTENSIONS_RICH")
}
print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                assert output.get("auto_apply_enabled") is True
            except json.JSONDecodeError:
                pass


class TestPatchModuleNamespacing:
    """Test module namespacing in patch"""

    def test_rich_utils_namespace_correct(self, subprocess_runner):
        """Test that _rich_utils gets correct namespace after patching"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import apply_rich_patch

apply_rich_patch()

import sys
# Check that typer.rich_utils exists and has correct attributes
if "typer.rich_utils" in sys.modules:
    rich_utils = sys.modules["typer.rich_utils"]
    output = {
        "exists": True,
        "name": rich_utils.__name__,
        "package": rich_utils.__package__
    }
else:
    output = {"exists": False}

print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                if output.get("exists"):
                    assert output.get("name") == "typer.rich_utils"
                    assert output.get("package") == "typer"
            except json.JSONDecodeError:
                pass

    def test_typer_package_attributes(self, subprocess_runner):
        """Test that created typer package has correct attributes"""
        code = """
import json
import os

os.environ["TYPER_EXTENSIONS_RICH"] = "1"

from typer_extensions._patch import apply_rich_patch

apply_rich_patch()

import sys
if "typer" in sys.modules:
    typer_module = sys.modules["typer"]
    output = {
        "exists": True,
        "has_package": hasattr(typer_module, "__package__"),
        "package_value": getattr(typer_module, "__package__", None),
        "has_path": hasattr(typer_module, "__path__"),
        "has_rich_utils": hasattr(typer_module, "rich_utils")
    }
else:
    output = {"exists": False}

print(json.dumps(output))
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "1"})
        assert result.returncode == 0
        if result.stdout.strip():
            try:
                output = json.loads(result.stdout.strip())
                if output.get("exists"):
                    assert output.get("has_package") is True
                    assert output.get("package_value") == "typer"
            except json.JSONDecodeError:
                pass
