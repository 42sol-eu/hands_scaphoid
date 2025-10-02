"""
FileHandler abstract base class module.
---yaml
File:
    name:   FileHandler.py
    uuid:   m7n3o9p5-6q1r-2s8t-gh9i-1m2n3o4p5q6r
    date:   2025-09-30

Description:
    Abstract base class for file handlers managing operations on different file types

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, Dict

#%% [Project base imports]
from ...__base__ import (
    AbstractBaseClass,
    abstract_method,
    logger,
    Path,
    PathLike,
)


class FileHandler(AbstractBaseClass):
    """
    Abstract base class for file handlers.
    
    FileHandlers manage operations on different file types, providing
    specialized behavior for opening, reading, writing, and validating
    files based on their format or purpose.
    """
    
    @abstract_method
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs) -> Any:
        """Open file with appropriate handler for the file type."""
        pass
    
    @abstract_method
    def read(self, file_path: PathLike, **kwargs) -> Any:
        """Read file content using format-specific logic."""
        pass
    
    @abstract_method
    def write(self, file_path: PathLike, content: Any, **kwargs) -> bool:
        """Write content to file using format-specific logic."""
        pass
    
    @abstract_method
    def validate(self, file_path: PathLike) -> bool:
        """Validate file format and structure."""
        pass
    
    @abstract_method
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get file-type specific metadata."""
        pass
    
    def test(self, file_path: PathLike) -> bool:
        """Test file integrity and readability."""
        try:
            return self.validate(file_path) and Path(file_path).exists()
        except Exception as e:
            logger.error(f"File test failed for {file_path}: {e}")
            return False