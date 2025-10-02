"""
TextFileHandler class module.
---yaml
File:
    name:   TextFileHandler.py
    uuid:   n8o4p0q6-7r2s-3t9u-hi0j-2n3o4p5q6r7s
    date:   2025-09-30

Description:
    Handler for plain text files with encoding support

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, Dict

#%% [Project base imports]
from ....__base__ import logger, Path, PathLike

#%% [Local imports]
from ..FileHandler import FileHandler


class TextFileHandler(FileHandler):
    """Handler for plain text files."""
    
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
    
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs):
        """Open text file with specified encoding."""
        return open(file_path, mode, encoding=self.encoding, **kwargs)
    
    def read(self, file_path: PathLike, **kwargs) -> str:
        """Read text file content."""
        with self.open(file_path, 'r', **kwargs) as f:
            return f.read()
    
    def write(self, file_path: PathLike, content: str, **kwargs) -> bool:
        """Write text content to file."""
        try:
            with self.open(file_path, 'w', **kwargs) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write text file {file_path}: {e}")
            return False
    
    def validate(self, file_path: PathLike) -> bool:
        """Validate text file by attempting to read it."""
        try:
            with self.open(file_path, 'r') as f:
                f.read(1024)  # Read first chunk to test encoding
            return True
        except (UnicodeDecodeError, OSError):
            return False
    
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get text file metadata."""
        path = Path(file_path)
        try:
            content = self.read(file_path)
            return {
                'encoding': self.encoding,
                'size_bytes': path.stat().st_size,
                'line_count': content.count('\n') + 1 if content else 0,
                'char_count': len(content),
                'word_count': len(content.split()) if content else 0,
                'is_empty': len(content.strip()) == 0
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return {'error': str(e)}