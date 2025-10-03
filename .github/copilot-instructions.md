# Hands Scaphoid - AI Agent Instructions

## Architecture Overview

This is a **hierarchical file system operations library** with **dual interfaces** and **extensible handler patterns**:

- **Dual APIs**: Operations classes (`File`, `Directory`, `Archive`) for direct use + Context managers (`FileContext`, `DirectoryContext`, `ArchiveContext`) for hierarchical operations
- **Separated Architecture**: Pure operations in `src/hands_scaphoid/operations/`, context managers in `src/hands_scaphoid/contexts/`, core objects in `src/hands_scaphoid/objects/`
- **Extensible Handler System**: `DynamicArchiveType` with runtime-extensible registry, Handler patterns for files/directories/executables (see `HANDLER_PATTERNS_DESIGN.md`)

## Critical Patterns

### 1. File Headers & Documentation
**Every file must include standardized headers**:
```python
"""
Module description.
---yaml
File:
    name: {{filename}}.py
    uuid: {{uuid4-generated-identifier}}  # Optional
    date: {{modification-date, YYYY-MM-DD}}

Description:
    {{Detailed description}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid
Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid
Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""
```

### 2. Import Structure (strict order)
```python
# [Standard library]
import os 

# [Project base] (always first)
from ..__base__ import (
    AbstractBaseType,
    Dict,
    List,
    logger,
    PathLike, 
    Path,
)

# [Project modules]  
from ..objects.FileObject import FileObject
from ..commands.core_commands import DynamicArchiveType
```

### 3. Handler Pattern Extensions
**When adding new handlers, follow the established pattern**:
- Abstract base class in `commands/handler_patterns.py`
- Concrete implementations with `validate()`, `read()`/`execute()`/`get_info()` methods
- Registry integration with factory functions
- Comprehensive tests in `tests/test_handler_patterns.py`

### 4. Registry-Based Extensibility  
**DynamicArchiveType usage** (replaces old CompressionType enum):
```python
# Adding new archive types
archive_type = get_archive_registry()
archive_type.add('myformat', '.myext', MyHandler())
archive_type.add_similar('variant', '.var', 'myformat')  # Reuse handler
```

## Development Workflows

### Testing Commands
```bash
# Run all tests
pytest tests/

# Run specific test suite  
pytest tests/test_handler_patterns.py -v

# Run with coverage
pytest --cov=hands_scaphoid --cov-report=term-missing
```

### Documentation Build
```bash
# Build and serve docs locally
mkdocs serve

# Deploy docs  
mkdocs gh-deploy
```

### Key Test Files
- `tests/test_archive_system.py` - Archive handler tests
- `tests/test_handler_patterns.py` - All handler pattern tests  
- `tests/test_separated_architecture.py` - Core architecture tests

## Project-Specific Conventions

### 1. Logging & Console Output
```python
from ..__base__ import logger, console

# Use structured logging
logger.debug("Handler selected: {handler}")
logger.error("Validation failed for {path}: {error}")

# Rich console for user output
console.print("[green]✓[/green] Operation completed")
```

### 2. Path Handling
```python
# Always use PathLike type hint
def process_file(path: PathLike) -> bool:
    path = Path(path)  # Convert to Path object
    # ... operations
```

### 3. Error Handling Strategy
```python
# Return False for failures, log errors
def operation(path: PathLike) -> bool:
    try:
        # ... operation
        return True
    except Exception as e:
        logger.error(f"Operation failed for {path}: {e}")
        return False
```

## Integration Points

### Handler Registry Access
```python
# Global registries (lazy-initialized)
from .handler_patterns import (
    get_file_handler_registry,
    get_directory_handler_registry, 
    get_executable_handler_registry
)

registry = get_file_handler_registry()
handler = registry.get('json')
```

### Archive System Integration
```python
# Use centralized registry
from .archive_registry import get_archive_registry

registry = get_archive_registry()
handler = registry.get_handler('zip')
```

### Context Stack Management
Context managers maintain hierarchical path resolution via internal stack - always use `with` statements for nested operations.

## Configuration Files

- **`.vscode/settings.json`**: Disables W1203 (f-string logging), enables pytest
- **`pyproject.tool.ruff`**: Ignores G201-G204 (logging format rules)  
- **`.pylintrc`**: Comprehensive linting rules with project-specific patterns

## Common Gotchas

1. **Handler Validation**: Always call `handler.validate(path)` before operations
2. **Registry Initialization**: Use factory functions, not direct instantiation  
3. **Path Resolution**: Context managers handle relative paths automatically
4. **Archive Extensions**: Use `get_file_extension()` for complex extensions like `.tar.gz`, `.drawio.png`
5. **Testing**: Mock external dependencies (subprocess, file operations) in tests