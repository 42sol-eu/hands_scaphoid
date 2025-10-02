"""
Handler protocol module.
---yaml
File:
    name: Handler.py
    uuid: k6l2m8n4-5o9p-1q7r-ef8g-0k1l2m3n4o5p
    date: 2025-09-30

Description:
    Base protocol for all handler types

Project:
    name: hands_scraphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, Dict, Protocol

#%% [Project base imports]
from ...__base__ import PathLike


class Handler(Protocol):
    """Base protocol for all handler types."""
    
    def validate(self, path: PathLike) -> bool:
        """Validate that the path/object is compatible with this handler."""
        ...
    
    def get_info(self, path: PathLike) -> Dict[str, Any]:
        """Get information about the object at the given path."""
        ...