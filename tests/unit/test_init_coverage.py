"""Tests to cover the module initialisation paths that depend on environment variables."""

from __future__ import annotations

import pytest


pytestmark = pytest.mark.isolated


class TestModuleInitialisationWithEnvironment:
    """Tests for module initialisation with different environment settings"""

    def test_init_with_rich_disabled(self, subprocess_runner):
        """Test module initialisation when TYPER_EXTENSIONS_RICH=0"""
        code = """
import typer_extensions
print("Success")
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "0"})
        assert result.returncode == 0
        assert "Success" in result.stdout

    def test_init_with_rich_opt_out(self, subprocess_runner):
        """Test module initialisation when TYPER_EXTENSIONS_RICH=0"""
        code = """
import typer_extensions
print("Success")
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_RICH": "0"})
        assert result.returncode == 0
        assert "Success" in result.stdout

    def test_init_with_debug_enabled(self, subprocess_runner):
        """Test module initialisation with debug enabled"""
        code = """
import typer_extensions
print("Success")
"""
        result = subprocess_runner(code, env={"TYPER_EXTENSIONS_DEBUG": "1"})
        assert result.returncode == 0
        assert "Success" in result.stdout

    def test_basic_imports_available(self, subprocess_runner):
        """Test that all expected imports are available after initialisation"""
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
