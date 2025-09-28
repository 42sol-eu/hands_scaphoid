---
applyTo: "**/commands/*.py"
---
# Command module implementation standards

## Module Structure
```python
"""
Command module description.

This module provides core command functions for [specific functionality].
---yaml
File:
    name: {{module}}_commands.py
    uuid: {{uuid4-generated-identifier}}
    date: {{modification-date, YYYY-MM-DD}}

Description:
    {{Detailed description of command functions}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- {{abbreviation}}[{{context}}]:: {{description}}
- DUT[testing]: Device Under Test (the main object/function being tested)
"""

#%% [Standard library imports]
import os 

#%% [Local imports]
from ..__base__ import (
    Any,
    Dict,
    List,
    logger, 
    PathLike, 
    Path,
)
```

## Command Function Patterns
```python
def command_function(path: PathLike, **kwargs) -> bool:
    """
    Command function with consistent interface.
    
    Args:
        path: Target path for operation
        **kwargs: Additional parameters
        
    Returns:
        bool: Success status
        
    Raises:
        FileNotFoundError: If path doesn't exist
    """
    path = Path(path)  # Always convert to Path
    
    try:
        # Command logic
        logger.debug(f"Executing command on {path}")
        return True
    except Exception as e:
        logger.error(f"Command failed for {path}: {e}")
        return False
```

## Registry-Based Commands
- Use DynamicArchiveType for extensible archive operations
- Integrate with handler registries for format detection
- Support runtime extension of supported types:
```python
def get_archive_handler(path: PathLike) -> Optional[ArchiveHandler]:
    """Get appropriate handler for archive file."""
    registry = get_archive_registry()
    archive_type = detect_archive_type(path)
    return registry.get_handler(archive_type)
```

## Path Utilities
- Use `get_file_extension()` for complex extensions (`.tar.gz`, `.drawio.png`)
- Support both simple and compound extensions
- Handle edge cases like files without extensions

## Integration Points
- Import from centralized registries
- Use established error handling patterns  
- Follow PathLike type conventions
- Maintain backward compatibility with existing APIs