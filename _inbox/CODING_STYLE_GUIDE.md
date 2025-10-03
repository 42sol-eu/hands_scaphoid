# Hands Scaphoid - Coding and Styling Rules

> Generated from codebase analysis on 2025-09-28

This document defines the coding standards, styling conventions, and architectural patterns observed and established in the Hands Scaphoid project.

## 📋 Table of Contents

1. [File Structure & Organization](#file-structure--organization)
2. [Naming Conventions](#naming-conventions)
3. [File Headers & Documentation](#file-headers--documentation)
4. [Import Organization](#import-organization)
5. [Class Design Patterns](#class-design-patterns)
6. [Method and Function Conventions](#method-and-function-conventions)
7. [Type Annotations](#type-annotations)
8. [Docstring Standards](#docstring-standards)
9. [Error Handling](#error-handling)
10. [Testing Patterns](#testing-patterns)
11. [Configuration & Tools](#configuration--tools)
12. [Architecture Patterns](#architecture-patterns)

## 🗂️ File Structure & Organization

### Directory Structure
```
src/hands_scaphoid/
├── __base__.py              # Common constants, imports, utilities
├── __init__.py              # Package exports with detailed __all__
├── main.py                  # CLI entry point
├── commands/                # Command functions (standalone operations)
│   ├── __init__.py
│   ├── core_commands.py
│   ├── file_commands.py
│   └── ...
├── objects/                 # Pure operation classes (no context management)
│   ├── __init__.py
│   ├── ObjectItem.py        # Base class
│   ├── FileObject.py        # File operations
│   ├── DirectoryObject.py   # Directory operations
│   └── ...Object.py         # Pattern: *Object.py for base classes
├── contexts/                # Context managers (hierarchical operations)
│   ├── __init__.py
│   ├── ContextCore.py       # Base context manager
│   ├── FileContext.py       # File context manager
│   └── ...Context.py        # Pattern: *Context.py for context managers
└── tests/                   # Test files mirror src structure
    ├── test_*.py           # Pattern: test_<module>.py
    └── conftest.py         # Shared test configuration
```

### File Naming Conventions
- **Core Classes**: `*Core.py` (e.g., `ItemCore.py`, `ContextCore.py`)
- **Context Managers**: `*Context.py` (e.g., `FileContext.py`, `ShellContext.py`)
- **Commands**: `*_commands.py` (e.g., `file_commands.py`, `core_commands.py`)
- **Scripts**: `*Script.py` (e.g., `FileScript.py`)
- **Enums/Types**: `type_enums.py`
- **Tests**: `test_*.py` following the module name

## 🏷️ Naming Conventions

### Classes
- **PascalCase** for all class names
- **Descriptive suffixes** indicating purpose:
  - `*Core` - Pure operation classes without context management
  - `*Context` - Context manager classes
  - `*Script` - Executable script classes
  - `*Type` - Type/enum definitions

```python
# ✅ Good
class FileObject(ObjectItem):
class DirectoryObject(Context):
class DynamicArchiveType:

# ❌ Bad
class file_handler:
class directoryManager:
```

### Functions and Methods
- **snake_case** for all function and method names
- **Descriptive verbs** indicating action
- **Private methods** prefixed with single underscore

```python
# ✅ Good
def read_content(file_path: PathLike) -> str:
def write_content(file_path: PathLike, content: str) -> None:
def _validate_path(self, path: PathLike) -> Path:

# ❌ Bad
def ReadContent(file_path):
def writeContent(file_path, content):
```

### Variables and Constants
- **snake_case** for variables and instance attributes
- **SCREAMING_SNAKE_CASE** for constants
- **Descriptive names** avoiding abbreviations

```python
# ✅ Good
DEBUG_MODE = False
ENABLE_TRACEBACK = DEBUG_MODE
file_path = Path("example.txt")
current_directory = os.getcwd()

# ❌ Bad
debug = False
fp = Path("example.txt")
curr_dir = os.getcwd()
```

## 📝 File Headers & Documentation

### Standard File Header
Every Python file must include a comprehensive header with metadata:

```python
#!/usr/bin/env python3
"""
Brief description of the module's purpose.

Longer description explaining the module's functionality, 
key classes, and usage patterns.
---yaml
File:
    name: {{file_name}}.py
    uuid: {{uuid4-generated-identifier}} 
    date: {{modification-date, YYYY-MM-DD}}

Description:
    {{Detailed description of the module's purpose}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""
```

### CLI Scripts Header
For executable scripts, include shebang and encoding:

```python
#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script description and usage information.
---yaml
File:
    name: {{script_name}}.py
    uuid: {{uuid4-generated-identifier}} 
    date: {{modification-date, YYYY-MM-DD}}

Description:
    {{Detailed description of the module's purpose}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""
```

## 📦 Import Organization

### Import Structure
Organize imports in distinct sections with clear separation:

```python
# [Standard library imports] - or just separate with comments
import os
import sys
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from enum import Enum

# [ Third-party imports]
import click
from rich.console import Console
from rich import print
import pytest

# [Local imports] - relative imports preferred for package modules
from ..__base__ import (
    console, 
    logger,
    PathLike, 
)
from ..objects import ObjectItem
from .type_enums import ItemType
```

### Import Guidelines
- **Group imports** by category (standard library, third-party, local)
- **Use parentheses** for multi-line imports
- **Relative imports** for internal package modules (`from ..module import`)
- **Absolute imports** for external packages
- **Explicit imports** preferred over wildcard imports (except for `__base__`)

## 🏗️ Class Design Patterns

### Base Class Hierarchy
```python
# Base classes provide common functionality
class ObjectItem:
    """Base class for all object types."""
    def __init__(self, name: str, path: str):
        self.name = name
        self.path = path

class FileObject(ObjectItem):
    """Pure file operations without context management."""
    def __init__(self, name: str, path: str):
        super().__init__(name, path, item_type=ItemType.FILE)
```

### Context Manager Pattern
```python
class FileContext(Context):
    """Context manager for hierarchical file operations."""
    
    def __init__(
        self,
        filename: PathLike,
        create: bool = False,
        dry_run: bool = False,
        enable_globals: bool = False,
    ):
        super().__init__(filename, create, dry_run, enable_globals)
    
    def __enter__(self):
        # Setup logic
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup logic
        pass
```

### Enum and Type Definitions
```python
class ItemType(str, Enum):
    """String-based enum for consistent type checking."""
    ITEM = "item"
    FILE = "file"
    DIRECTORY = "directory"
    ARCHIVE = "archive"

# Type aliases for common patterns
PathLike = Union[str, Path]
```

## 🔧 Method and Function Conventions

### Method Signatures
- **Type hints** for all parameters and return values
- **Default values** for optional parameters
- **Descriptive parameter names**

```python
def read_content(
    file_path: PathLike, 
    head: Optional[int] = None, 
    tail: Optional[int] = None, 
    line_separator: str = '\n', 
    do_print: bool = False
) -> str:
    """Read file content with optional head/tail limits."""
    pass
```

### Static Methods for Pure Operations
```python
class FileObject:
    @staticmethod
    def write_content(file_path: PathLike, content: str) -> None:
        """Write content to file - pure operation."""
        pass
    
    @staticmethod
    def read_content(file_path: PathLike) -> str:
        """Read content from file - pure operation."""
        pass
```

### Method Chaining Support
```python
class FileContext:
    def write_content(self, content: str) -> 'FileContext':
        """Support method chaining for fluent interface."""
        # Implementation
        return self
    
    def append_line(self, line: str) -> 'FileContext':
        """Chain-friendly line appending."""
        # Implementation
        return self
```

## 🏷️ Type Annotations

### Required Type Hints
- **All function parameters** must have type annotations
- **All return values** must be annotated
- **Class attributes** should be annotated when not obvious

```python
# ✅ Good
def process_files(
    input_dir: PathLike, 
    output_dir: PathLike,
    pattern: str = "*.py",
    recursive: bool = True
) -> List[Path]:
    """Process files with full type annotations."""
    pass

# ❌ Bad
def process_files(input_dir, output_dir, pattern="*.py", recursive=True):
    """Missing type annotations."""
    pass
```

### Common Type Patterns
```python
# [Standard library imports]
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# [Standard type aliases]
PathLike = Union[str, Path]
ConfigDict = Dict[str, Any]
FileList = List[Path]

# [Optional types]
def get_config(name: str) -> Optional[ConfigDict]:
    pass

# [Union types for multiple possibilities]
def handle_input(data: Union[str, bytes, Path]) -> str:
    pass
```

## 📚 Docstring Standards

### Google-Style Docstrings
Use Google-style docstrings consistently throughout the codebase:

```python
def example_function(param1: str, param2: int, optional_param: bool = False) -> bool:
    """
    Brief description of the function.
    
    Longer description explaining the function's purpose, behavior,
    and any important implementation details. This can span multiple
    lines and include usage examples.
    
    Args:
        param1: Description of the first parameter.
        param2: Description of the second parameter.
        optional_param: Description of optional parameter with default value.
        
    Returns:
        Description of the return value and its type.
        
    Raises:
        ValueError: When param1 is empty or invalid.
        FileNotFoundError: When required files are missing.
        TypeError: When param2 is not an integer.
        
    Example:
        Basic usage example:
        
        >>> result = example_function("hello", 42)
        >>> print(result)
        True
        
        Advanced usage:
        
        >>> result = example_function("test", 100, optional_param=True)
        >>> assert result is True
        
    Note:
        Any important notes about behavior, performance, or limitations.
    """
    pass
```

### Class Docstrings
```python
class FileObject(ObjectItem):
    """
    Pure file operations class without context management.

    This class provides static methods for file operations that can be used
    independently of any context manager. All methods operate on explicit
    file paths and do not maintain any state.

    The class is designed for scenarios where you need direct file operations
    without the overhead of context management or hierarchical path resolution.

    Attributes:
        name: The name of the file.
        path: The filesystem path to the file.
        item_type: The type of item (always ItemType.FILE).

    Example:
        Direct file operations:
        
        >>> FileObject.write_content(Path("config.txt"), "setting=value")
        >>> content = FileObject.read_content(Path("config.txt"))
        >>> FileObject.append_line(Path("log.txt"), "New log entry")
        
        Creating file instances:
        
        >>> file_obj = FileObject("config.txt", "/path/to/config.txt")
        >>> print(file_obj.name)
        config.txt
    """
    pass
```

## ⚠️ Error Handling

### Exception Handling Patterns
```python
def safe_file_operation(file_path: PathLike) -> Optional[str]:
    """Demonstrate proper exception handling."""
    try:
        # Main operation
        return read_file_content(file_path)
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error reading {file_path}: {e}")
        if DEBUG_MODE:
            raise
        return None
```

### Custom Exceptions
```python
class HandsScaphoidError(Exception):
    """Base exception for hands-scaphoid package."""
    pass

class InvalidPathError(HandsScaphoidError):
    """Raised when path validation fails."""
    pass

class OperationError(HandsScaphoidError):
    """Raised when file operations fail."""
    pass
```

## 🧪 Testing Patterns

### Test Organization
```python
class TestShellInitialization:
    """Test Shell class initialization."""

    def test_init_default_values(self):
        """Test Shell initialization with default values."""
        shell = Shell()
        assert shell.cwd == os.getcwd()
        assert isinstance(shell.env, dict)
        assert shell.allow_commands == []

    def test_init_with_custom_cwd(self, temp_dir):
        """Test Shell initialization with custom working directory."""
        shell = Shell(cwd=str(temp_dir))
        assert shell.cwd == str(temp_dir)
```

### Test Naming
- **Class names**: `Test<ClassName><Aspect>` (e.g., `TestShellInitialization`)
- **Method names**: `test_<feature>_<scenario>` (e.g., `test_init_with_custom_cwd`)
- **Descriptive docstrings** for each test method

### Fixtures and Mocking
```python
@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)

@pytest.fixture
def mock_env_vars():
    """Mock environment variables."""
    return {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}
```

## ⚙️ Configuration & Tools

### Linting Configuration
```toml
[tool.pylint]
disable = [
    "W1203",  # logging-fstring-interpolation
]

[tool.ruff]
ignore = [
    "G201", "G202", "G203", "G204"  # Logging-related rules
]
line-length = 88
target-version = "py311"

[tool.ruff.lint]
ignore = [
    "G204",  # logging-fstring-interpolation
]
```

### Development Dependencies
```toml
[dependency-groups]
dev = [
    "pytest>=8.4.2",
    "pytest-cov>=7.0.0", 
    "pytest-mock>=3.15.0",
]
```

## 🏛️ Architecture Patterns

### Separation of Concerns
1. **Commands** (`commands/`) - Pure functions for operations
2. **Objects** (`objects/`) - Classes for data and operations without context
3. **Contexts** (`contexts/`) - Context managers for hierarchical operations

### Design Principles
1. **Single Responsibility** - Each class has one clear purpose
2. **Open/Closed** - Extensible through inheritance and composition
3. **Dependency Inversion** - Depend on abstractions, not concretions
4. **Interface Segregation** - Small, focused interfaces

### Method Chaining Pattern
```python
# Support fluent interfaces where appropriate
result = (FileContext("report.txt", create=True)
         .write_content("# Report")
         .add_heading("Summary") 
         .append_line("Key findings...")
         .append_line("Recommendations..."))
```

### Context Manager Pattern
```python
# Hierarchical context management
with DirectoryContext('projects') as projects:
    with DirectoryContext('myproject') as project:
        with FileContext('README.md', create=True) as readme:
            readme.write_content("# My Project")
```

## 📋 Code Review Checklist

Before submitting code, ensure:

- [ ] **File header** with proper metadata is present
- [ ] **Type annotations** for all function parameters and returns
- [ ] **Google-style docstrings** for all public methods/classes
- [ ] **Import organization** follows the established pattern
- [ ] **Naming conventions** are consistent
- [ ] **Error handling** is appropriate and consistent
- [ ] **Tests** are included for new functionality
- [ ] **Method chaining** support where appropriate
- [ ] **Context manager** pattern for hierarchical operations
- [ ] **Logging** uses f-string interpolation (W1203 disabled)

## 🔄 Continuous Improvement

This style guide is a living document that should be updated as the codebase evolves. Regular reviews should ensure consistency and identify opportunities for improvement.

---

*Generated from codebase analysis on September 28, 2025*
*Project: Hands Scaphoid - Hierarchical File System Operations with Context Management*
