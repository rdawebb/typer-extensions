"""Tests for __init__.py import paths in a fresh interpreter"""

from __future__ import annotations

import json

import pytest

pytestmark = pytest.mark.isolated


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
