"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration. It also provides hierarchical context
managers for file system operations including directories, files, and archives.
"""

from .__base__ import *
from .main import (
    console,
    demo,
    exec,
    main,
)

__all__ = [
    "console",  # src\hands_scaphoid\__base__.py
    "DEBUG_MODE",  # src\hands_scaphoid\__base__.py
    "demo",  # src\hands_scaphoid\main.py
    "ENABLE_TRACEBACK",  # src\hands_scaphoid\__base__.py
    "exec",  # src\hands_scaphoid\main.py
    "G_debug",  # src\hands_scaphoid\__base__.py
    "main",  # src\hands_scaphoid\main.py
    "no",  # src\hands_scaphoid\__base__.py
    "PathLike",  # src\hands_scaphoid\__base__.py
    "yes",  # src\hands_scaphoid\__base__.py
]
