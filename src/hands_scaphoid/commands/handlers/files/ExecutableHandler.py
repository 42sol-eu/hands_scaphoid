"""
ExecutableHandler abstract base class module.
---yaml
File:
    name:   ExecutableHandler.py
    uuid:   s3t9u5v1-2w7x-8y4z-pq5r-7s8t9u0v1w2x
    date:   2025-09-30

Description:
    Abstract base class for executable handlers managing different types of executable files

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Standard library imports]
from typing import Any, Dict, List

# [Project base imports]
from ....__base__ import (
    AbstractBaseClass,
    abstract_method,
    PathLike,
)


class ExecutableHandler(AbstractBaseClass):
    """
    Abstract base class for executable handlers.
    
    ExecutableHandlers manage different types of executable files,
    providing specialized behavior for running, validating, and
    managing executable programs.
    """
    
    @abstract_method
    def execute(self, exe_path: PathLike, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute the program with given arguments."""
        pass
    
    @abstract_method
    def validate(self, exe_path: PathLike) -> bool:
        """Validate that the file is a valid executable."""
        pass
    
    @abstract_method
    def get_info(self, exe_path: PathLike) -> Dict[str, Any]:
        """Get executable information (version, dependencies, etc.)."""
        pass