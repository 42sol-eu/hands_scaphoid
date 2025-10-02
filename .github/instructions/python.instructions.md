---
applyTo: "**/*.py"
---
# Project coding standards for Python

## File Structure
- **Always include standardized file headers**:
```python
"""
Module description.

File:
    name:   {{filename}}.py
    uuid:   {{generated-uuid}} 
    date:   {{modification-date, YYYY-MM-DD}}

Description:
    Detailed description of module purpose

Project:
    name:   hands_scaphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- {{abbreviation}}[{{context}}]:: {{description}}
- 42sol[company]: 42 solutions (www.42sol.eu)
"""
```

## Import Organization (strict order)
```python
# 1. Standard library imports
from pathlib import Path
from typing import Any, Dict, List, Optional

# 2. Project base imports (ALWAYS FIRST)
from ..__base__ import PathLike, logger, console

# 3. Project internal imports
from ..objects.FileObject import FileObject
from ..commands.core_commands import DynamicArchiveType
```

## Code Style
- Follow PEP 8 with project-specific extensions
- Use `PathLike` type hint for all path parameters: `def func(path: PathLike) -> bool:`
- Always convert paths to Path objects: `path = Path(path)`
- Use f-string logging is ALLOWED (W1203 disabled): `logger.error(f"Failed: {error}")`

## Error Handling Pattern
```python
def operation(path: PathLike) -> bool:
    try:
        # ... operation logic
        return True
    except Exception as e:
        logger.error(f"Operation failed for {path}: {e}")
        return False
```

## Handler Pattern Implementation
- Abstract base classes in `commands/handler_patterns.py`
- Concrete implementations with `validate()`, `read()`/`execute()`/`get_info()` methods
- Registry integration with factory functions
- Always call `handler.validate(path)` before operations

## Registry Usage
```python
# Use factory functions, not direct instantiation
from .handler_patterns import get_file_handler_registry
registry = get_file_handler_registry()
handler = registry.get('json')
```
