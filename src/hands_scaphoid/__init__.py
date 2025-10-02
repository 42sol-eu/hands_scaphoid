"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration. It also provides hierarchical context
managers for file system operations including directories, files, and archives.
----
File:
    name:        __init__.py
    uuid:        b718787f-85b1-4ac9-a136-ea01cf4f8545
    date:        2025-09-29

Description:     init

Project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

__version__ = "2025.0.3"
__author__ = "Andreas Felix Häberle"

from .__base__ import DEBUG_MODE, ENABLE_TRACEBACK, G_debug, Path, PathLike, no, yes
from .contexts.ShellContext import ShellContext
from .objects.ShellExecutable import ShellExecutable

# Backward compatibility alias
Shell = ShellExecutable


# %% [Exports]
__all__ = [
    "console",  # src\hands_scaphoid\__base__.py
    "DEBUG_MODE",  # src\hands_scaphoid\__base__.py
    "ENABLE_TRACEBACK",  # src\hands_scaphoid\__base__.py
    "G_debug",  # src\hands_scaphoid\__base__.py
    "Path",
    "no",  # src\hands_scaphoid\__base__.py
    "PathLike",  # src\hands_scaphoid\__base__.py
    "yes",  # src\hands_scaphoid\__base__.py
    "Shell",  # Backward compatibility alias
    "ShellContext",
    "ShellExecutable"
]
