#!/usr/bin/env python3
"""
Shell context manager for hands-scaphoid package.

File:
    name: ShellContext.py
    uuid: e70a4d0b-2ae4-4fb2-a183-24ba99f1e65b
    date: 2025-09-12

Description:
    Provides a context manager that exposes shell functions globally
    for easy script-like usage while maintaining proper cleanup.

Project:
    name: hands/palm/scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4

Authors: ["Andreas Häberle"]
Projects: ["hands/palm/scaphoid"]
"""

from __future__ import annotations

import builtins
from contextlib import contextmanager
from typing import Dict, Generator, Optional, Union
from pathlib import Path

from ..objects.ShellExecutable import Shell


@contextmanager
def ShellContext(
    cwd: Optional[Union[str, Path]] = None,
    env: Optional[Dict[str, str]] = None,
    env_file: str = "~/.env"
) -> Generator[Shell, None, None]:
    """
    Context manager that provides global shell functions.
    
    This context manager creates a Shell instance and exposes its methods
    as global functions for convenient script-like usage. The functions
    are automatically cleaned up when exiting the context.
    
    Args:
        cwd: Working directory for command execution.
        env: Environment variables dictionary.
        env_file: Path to environment file to load variables from.
        
    Yields:
        Shell: The Shell instance for advanced usage.
        
    Example:
        with ShellContext() as shell:
            allow("ls")
            allow("echo")
            result = run("ls -la")
            cd("/tmp")
            run("echo 'Hello World'")
    """
    ctx = Shell(cwd, env, env_file)
    
    # Store original functions if they exist
    original_functions = {}
    function_names = ["cd", "run", "run_in", "sleep", "allow", "depends_on"]
    
    for func_name in function_names:
        if hasattr(builtins, func_name):
            original_functions[func_name] = getattr(builtins, func_name)
    
    # Set global functions
    builtins.cd = ctx.cd
    builtins.run = ctx.run
    builtins.run_in = ctx.run_in
    builtins.sleep = ctx.sleep
    builtins.allow = ctx.allow
    builtins.depends_on = ctx.depends_on
    
    try:
        yield ctx
    finally:
        # Restore original functions or delete if they didn't exist
        for func_name in function_names:
            if func_name in original_functions:
                setattr(builtins, func_name, original_functions[func_name])
            elif hasattr(builtins, func_name):
                delattr(builtins, func_name)


# Legacy function name for backward compatibility
ShellContextManager = ShellContext
