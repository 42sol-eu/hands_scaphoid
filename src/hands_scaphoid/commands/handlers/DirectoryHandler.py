"""
DirectoryHandler abstract base class module.
---yaml
File:
    name:   DirectoryHandler.py
    uuid:   p0q6r2s8-9t4u-5v1w-lm2n-4p5q6r7s8t9u
    date:   2025-09-30

Description:
    Abstract base class for directory handlers managing operations on different directory types

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, Dict, List

#%% [Project base imports]
from ...__base__ import (
    AbstractBaseClass,
    abstract_method,
    Path,
    PathLike,
)


class DirectoryHandler(AbstractBaseClass):
    """
    Abstract base class for directory handlers.
    
    DirectoryHandlers manage operations on different directory types,
    providing specialized behavior for projects, repositories, and
    special directory structures.
    """
    
    @abstract_method
    def validate(self, dir_path: PathLike) -> bool:
        """Validate directory structure and contents."""
        pass
    
    @abstract_method
    def initialize(self, dir_path: PathLike, **kwargs) -> bool:
        """Initialize directory with required structure."""
        pass
    
    @abstract_method
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get information about directory structure."""
        pass
    
    @abstract_method
    def list_contents(self, dir_path: PathLike, pattern: str = "*") -> List[Path]:
        """List directory contents with optional filtering."""
        pass
    
    def scan(self, dir_path: PathLike, recursive: bool = True) -> Dict[str, Any]:
        """Scan directory and return comprehensive information."""
        return {
            'is_valid': self.validate(dir_path),
            'structure': self.get_structure_info(dir_path),
            'contents': self.list_contents(dir_path) if recursive else []
        }