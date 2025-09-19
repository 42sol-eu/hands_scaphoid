"""
Hands Scaphoid - A secure shell execution context manager.

This package provides secure shell command execution with environment management,
command allowlisting, and Docker integration. It also provides hierarchical context
managers for file system operations including directories, files, and archives.
----
file:
    name:        __init__.py  
    uuid:        b718787f-85b1-4ac9-a136-ea01cf4f8545
description:     init
authors:         felix@42sol.eu
project:
project:
    name:        hands_scaphoid
    uuid:        TODO_uuid_scaphoid
    url:         https://github.com/42sol-eu/hands_scaphoid
"""


__version__ = "2025.0.3"
__author__ = "Andreas Felix Häberle"

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
