"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration. It also provides hierarchical context
managers for file system operations including directories, files, and archives.
"""

__version__ = "2025.0.3"
__author__ = "Andreas Felix Häberle"

from .__base__ import *
from .objects import (
    type_enums,
    ItemCore,
    ObjecCore,
    VariableCore,
    FileCore,
    ArchiveFile,
    DirectoryCore,
    ShellExecutable,
    PowerShell,
    WslShell,
)
from .contexts import (
    Context,
    ShellContext,
)
from .main import (
    console,
    demo,
    exec,
    main,
)

__all__ = [
    # Version and author info
    "__version__",
    "__author__",
    
    # Objects
    "type_enums",
    "Item",
    "Object", 
    "Variable",
    "File",
    "Archive",
    "Directory",
    "Shell",
    "PowerShell",
    "WslShell",
    
    # Contexts
    "Context",
    "ShellContext",
    
    # Main functions
    "console",
    "demo",
    "exec",
    "main",
    
    # Base utilities
    "DEBUG_MODE",
    "ENABLE_TRACEBACK", 
    "G_debug",
    "no",
    "PathLike",
    "yes",
]
