"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration.
"""

from .__base__ import *  # noqa: F401, F403
from .Shell import Shell
from .ShellContext import ShellContext
from .WindowsShells import PowerShellShell, WslShell, create_powershell_shell, create_wsl_shell

__version__ = "0.1.0"
__author__ = "Andreas Häberle"
__all__ = ["Shell", "ShellContext", "PowerShellShell", "WslShell", "create_powershell_shell", "create_wsl_shell"]