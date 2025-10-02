# Hands Scaphoid - Style Configuration Summary

# This file contains the key style rules in a format suitable for tooling and quick reference

## File Naming Patterns
- Core classes: *Core.py (FileObject.py, ObjectItem.py)
- Context managers: *Context.py (FileContext.py, ShellContext.py)  
- Commands: *_commands.py (file_commands.py, core_commands.py)
- Scripts: *Script.py (FileScript.py)
- Tests: test_*.py (test_shell.py, test_main.py)

## Class Naming
- PascalCase for all classes
- Descriptive suffixes: Core, Context, Script, Type
- Examples: FileObject, DirectoryContext, DynamicArchiveType

## Function/Method Naming
- snake_case for all functions and methods
- Descriptive verbs: read_content, write_content, create_directory
- Private methods: _validate_path, _setup_environment

## Variable Naming
- snake_case for variables: file_path, current_directory
- SCREAMING_SNAKE_CASE for constants: DEBUG_MODE, ENABLE_TRACEBACK
- Descriptive names, avoid abbreviations

## Type Annotations (Required)
- All function parameters: def func(param: str) -> None:
- All return values: -> str, -> Optional[Dict[str, Any]]
- Common patterns: PathLike = Union[str, Path]

## Import Organization
1. Standard library imports
2. Third-party imports (click, rich, pytest)
3. Local imports with relative paths (from ..module import)
4. Group with parentheses for multi-line imports

## Docstring Standard
- Google-style docstrings for all public methods/classes
- Include Args:, Returns:, Raises:, Example: sections
- Brief description + longer explanation for complex functionality

## File Header Template
```python
#!/usr/bin/env python3
"""
Brief module description.
---yaml
File:
    name: filename.py
    date: YYYY-MM-DD

Description:
    Detailed purpose

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""
```

## Architecture Patterns
- Separation: commands/ (functions), objects/ (classes), contexts/ (context managers)
- Method chaining support: return self for fluent interface
- Context managers for hierarchical operations
- Static methods for pure operations (FileObject.read_content)

## Error Handling
- Specific exceptions with descriptive messages
- Proper logging with f-string interpolation (W1203 disabled)
- Graceful handling with DEBUG_MODE flag for verbose errors

## Testing Patterns
- Class names: TestClassName<Aspect>
- Method names: test_feature_scenario
- Descriptive docstrings for each test
- Use fixtures for common test data