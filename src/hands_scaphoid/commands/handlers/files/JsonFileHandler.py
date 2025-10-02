"""
JsonFileHandler class module.
---yaml
File:
    name:   JsonFileHandler.py
    uuid:   o9p5q1r7-8s3t-4u0v-jk1l-3o4p5q6r7s8t
    date:   2025-09-30

Description:
    Handler for JSON files with validation and formatting

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, Dict

#%% [Project base imports]
from ....__base__ import logger, Path, PathLike

#%% [Local imports]
from ..FileHandler import FileHandler


class JsonFileHandler(FileHandler):
    """Handler for JSON files with validation and formatting."""
    
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs):
        """Open JSON file."""
        return open(file_path, mode, encoding='utf-8', **kwargs)
    
    def read(self, file_path: PathLike, **kwargs) -> Dict[str, Any]:
        """Read and parse JSON content."""
        import json
        with self.open(file_path, 'r') as f:
            return json.load(f)
    
    def write(self, file_path: PathLike, content: Dict[str, Any], 
              indent: int = 2, **kwargs) -> bool:
        """Write formatted JSON content."""
        import json
        try:
            with self.open(file_path, 'w') as f:
                json.dump(content, f, indent=indent, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            return False
    
    def validate(self, file_path: PathLike) -> bool:
        """Validate JSON syntax."""
        import json
        try:
            with self.open(file_path, 'r') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False
    
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get JSON file metadata including structure info."""
        path = Path(file_path)
        try:
            data = self.read(file_path)
            return {
                'size_bytes': path.stat().st_size,
                'json_type': type(data).__name__,
                'key_count': len(data) if isinstance(data, dict) else None,
                'array_length': len(data) if isinstance(data, list) else None,
                'is_valid': True,
                'structure_depth': self._get_json_depth(data)
            }
        except Exception as e:
            return {'is_valid': False, 'error': str(e)}
    
    def _get_json_depth(self, obj, depth=0):
        """Calculate JSON structure depth."""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        return depth