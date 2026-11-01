"""Tests for typer_extensions.__init__ module initialisation."""

import pytest


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
        import typer

        import typer_extensions

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
        import typer

        import typer_extensions

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

    def test_core_module_components_available(self):
        """Test that core module components are available through the package"""
        import typer_extensions
        from typer_extensions.core import Context, ExtendedTyper

        # These should be available from the main package
        assert typer_extensions.ExtendedTyper is ExtendedTyper
        assert typer_extensions.Context is Context


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
        from typer_extensions import Context, ExtendedTyper

        # Should be able to use them
        app = ExtendedTyper(name="test")
        assert app is not None

        # Context should be available
        assert Context is not None


class TestInitModuleAttributeAccess:
    """Test __getattr__ function in __init__.py"""

    def test_getattr_forwards_to_typer(self):
        """Test that __getattr__ forwards undefined attributes to Typer"""
        import typer

        import typer_extensions

        # Access an attribute that's not explicitly exported
        attr = typer_extensions.__getattr__("Argument")
        assert attr is typer.Argument
