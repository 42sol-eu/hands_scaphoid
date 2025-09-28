#!/usr/bin/env python3
"""
Unit tests for the __init__ module.
---yaml
File:
    name: test_init.py
    uuid: f1e2d3c4-b5a6-7890-1234-567890abcdef
    date: 2025-09-28

Description:
    Comprehensive tests for module imports and exports

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

import pytest

from hands_scaphoid import Shell, ShellContext, __version__, __author__, __all__


class TestModuleImports:
    """Test module imports and exports."""

    def test_shell_import(self):
        """Test that Shell class is importable."""
        assert Shell is not None
        assert callable(Shell)

    def test_shell_context_import(self):
        """Test that ShellContext is importable."""
        assert ShellContext is not None
        assert callable(ShellContext)

    def test_version_info(self):
        """Test version information."""
        assert isinstance(__version__, str)
        assert len(__version__) > 0
        assert "." in __version__  # Should be semantic version

    def test_author_info(self):
        """Test author information."""
        assert isinstance(__author__, str)
        assert len(__author__) > 0

    def test_all_exports(self):
        """Test __all__ exports."""
        assert isinstance(__all__, list)
        assert "Shell" in __all__
        assert "ShellContext" in __all__
        assert "__version__" in __all__
        assert "__author__" in __all__
        assert len(__all__) > 10  # Should have many exports


class TestModuleIntegration:
    """Test module integration."""

    def test_can_create_shell_instance(self):
        """Test that we can create a Shell instance."""
        shell = Shell()
        assert shell is not None
        assert hasattr(shell, "run")
        assert hasattr(shell, "allow")
        assert hasattr(shell, "cd")

    def test_can_use_shell_context(self, temp_dir):
        """Test that we can use ShellContext."""
        with ShellContext(cwd=str(temp_dir)) as shell:
            assert shell is not None
            assert isinstance(shell, Shell)
