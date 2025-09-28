---
applyTo: "**/objects/*.py"
---
# Core object implementation standards

## Object Class Structure
```python
"""
Core object module description.
---yaml
File:
    name: ObjectCore.py
    uuid: generated-uuid
    date: YYYY-MM-DD

Description:
    Core object representation with [specific functionality]

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

from pathlib import Path
from typing import Optional, Dict, Any

from ..__base__ import PathLike, logger, console
from .ItemCore import ItemCore
from ..commands.core_commands import get_file_extension
```

## Core Object Implementation
```python
class ObjectCore(ItemCore):
    """Core object with handler pattern integration."""
    
    def __init__(self, path: PathLike):
        """Initialize core object."""
        super().__init__(path)
        self._handler = None
        self._metadata_cache = None
    
    @property
    def handler(self):
        """Get appropriate handler for this object."""
        if self._handler is None:
            self._handler = self._detect_handler()
        return self._handler
    
    def _detect_handler(self):
        """Detect and return appropriate handler."""
        # Handler detection logic
        pass
```

## Handler Integration Patterns
- Use composition over inheritance for handler support
- Implement lazy handler detection and caching
- Support multiple applicable handlers where appropriate
- Provide fallback to default handlers

## Metadata and Information
```python
def get_metadata(self, use_cache: bool = True) -> Dict[str, Any]:
    """Get comprehensive object metadata."""
    if self._metadata_cache is None or not use_cache:
        basic_info = self._get_basic_info()
        handler_info = self.handler.get_info(self.path)
        
        self._metadata_cache = {
            **basic_info,
            **handler_info,
            'handler_type': type(self.handler).__name__
        }
    
    return self._metadata_cache
```

## Backward Compatibility
- Maintain existing method signatures
- Provide compatibility shims for deprecated methods
- Support both old and new handler-based approaches
- Clear migration path documentation

## Error Handling
- Use established error handling patterns
- Return meaningful error information
- Log operations with appropriate severity
- Handle handler detection failures gracefully

## Static Methods for Direct Operations
- Provide static methods for direct operations without objects
- Delegate to command modules for actual implementation
- Maintain separation between object and operations concerns