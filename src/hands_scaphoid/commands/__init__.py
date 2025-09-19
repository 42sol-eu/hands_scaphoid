"""
Init commands module for package.

This module contains command functions used throughout the package.
----
file:
    name:        __init__.py  
    uuid:        c7151963-72d1-4661-bec3-accb29f39c85
description:     init commands
authors:         felix@42sol.eu
project:
project:
    name:        hands_scaphoid
    uuid:        TODO_uuid_scaphoid
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from .core_commands import get_file_extension

__all__ = [
    "get_file_extension",
]
