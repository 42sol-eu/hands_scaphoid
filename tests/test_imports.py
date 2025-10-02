"""
Test for import statements in hands_scaphoid.
---yaml
File:
    name: test_imports.py
    uuid: 2e2b8e7c-7c8e-4e3d-9b1a-3c1f8b2e4a1d
    date: 2025-09-30

Description:
    This file tests the importability of modules in the hands_scaphoid project.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

def unload_modules(module_names):
    """
    Unload specified modules from sys.modules to ensure fresh imports.
    """
    import sys
    for module_name in module_names:
        if module_name in sys.modules:
            del sys.modules[module_name]
            
def test_import_cli():
    """
    Test importing the CLI module.
    """
    unload_modules(['hands_scaphoid.cli'])
    from hands_scaphoid.cli import main as cli_main
    assert callable(cli_main), "cli.main should be callable"

def test_import_base():
    """
    Test importing the base module.
    """
    unload_modules(['hands_scaphoid.__base__'])
    from hands_scaphoid.__base__ import (
        DEBUG_MODE,
        ENABLE_TRACEBACK,
        PathLike,
        AbstractBaseClass,
        abstract_method,
        logger,
        console,
        yes, no, true, false,
    )
    assert isinstance(DEBUG_MODE, bool), "DEBUG_MODE should be a boolean"
    assert isinstance(ENABLE_TRACEBACK, bool), "ENABLE_TRACEBACK should be a boolean"
    assert PathLike is not None, "PathLike should be defined"
    assert callable(abstract_method), "abstract_method should be callable"
    assert logger is not None, "logger should be defined"
    assert console is not None, "console should be defined"
    assert isinstance(yes, bool), "yes should be a boolean"
    assert isinstance(no, bool), "no should be a boolean"
    assert isinstance(true, bool), "true should be a boolean"
    assert isinstance(false, bool), "false should be a boolean"