"""Tests for the typer_extensions._compat Click compatibility shim."""

from __future__ import annotations

import builtins
import importlib
import sys
import types as pytypes

import typer_extensions._compat as compat


class TestVendoredClick:
    """Test the Typer >= 0.26 path, where Click is vendored as typer._click."""

    def test_resolves_vendored_click(self):
        """Test the shim resolves Click from typer._click"""
        assert compat.click.__name__ == "typer._click"
        assert compat.Command is compat.click.Command
        assert compat.Context is compat.click.Context
        assert compat.HelpFormatter is compat.click.HelpFormatter
        assert compat.types is not None


class TestStandaloneClickFallback:
    """Test the Typer < 0.26 path, where the standalone click package is used."""

    def test_falls_back_to_standalone_click(self, monkeypatch):
        """Test the shim falls back to standalone click when typer._click is absent

        Typer >= 0.26 is installed, so the fallback is reached by making the
        vendored import fail and standing in a fake standalone click package.
        """
        fake_click = pytypes.ModuleType("click")
        fake_types = pytypes.ModuleType("click.types")

        class FakeCommand:
            pass

        class FakeContext:
            pass

        class FakeHelpFormatter:
            pass

        fake_click.__dict__.update(
            Command=FakeCommand,
            Context=FakeContext,
            HelpFormatter=FakeHelpFormatter,
            types=fake_types,
        )

        real_import = builtins.__import__

        def fake_import(name, globals=None, locals=None, fromlist=(), level=0):
            if name == "typer._click" or (
                name == "typer" and fromlist and "_click" in fromlist
            ):
                raise ImportError("no vendored click")

            return real_import(name, globals, locals, fromlist, level)

        monkeypatch.setitem(sys.modules, "click", fake_click)
        monkeypatch.setitem(sys.modules, "click.types", fake_types)
        monkeypatch.setattr(builtins, "__import__", fake_import)
        try:
            importlib.reload(compat)

            assert compat.click is fake_click
            assert compat.Command is FakeCommand
            assert compat.Context is FakeContext
            assert compat.HelpFormatter is FakeHelpFormatter
            assert compat.types is fake_types

        finally:
            # _print_options_panel re-imports types from _compat on every call,
            # so the module must be restored before any later test runs; undo
            # explicitly rather than at teardown, so the reload sees real typer
            monkeypatch.undo()
            importlib.reload(compat)

        assert compat.click.__name__ == "typer._click"
        assert compat.Command is compat.click.Command
