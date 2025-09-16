"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration. It also provides hierarchical context
managers for file system operations including directories, files, and archives.
"""

from .__base__ import *  # noqa: F401, F403
from .Shell import Shell
from .ShellContext import ShellContext
from .WindowsShells import PowerShell, WslShell, create_powershell_shell, create_wsl_shell
from .Context import Context
from .Directory import Directory
from .File import File
from .Archive import Archive

__version__ = "0.1.0"
__author__ = "Andreas Häberle"
__all__ = [
    "Shell", "ShellContext", "PowerShell", "WslShell", 
    "create_powershell_shell", "create_wsl_shell",
    "Context", "Directory", "File", "Archive"
]