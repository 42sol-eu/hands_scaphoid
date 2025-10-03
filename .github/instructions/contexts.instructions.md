---
applyTo: "**/contexts/*.py"
---
# Context manager implementation standards

## Context Manager Structure
```python
"""
Context manager module description.
---yaml
File:
    name: {{ContextName}}.py
    uuid: {{uuid4-generated-identifier}}
    date: {{modification-date, YYYY-MM-DD}}

Description:
    Hierarchical context manager for {{specific operations}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- {{abbreviation}}[{{context}}]:: {{description}}
- DUT[testing]: Device Under Test (the main object/function being tested)
"""

# [Standard library imports]
# - none

# [Local imports]
from ..__base__ import (
    Any,
    context_manager
    Dict,
    List,
    logger,
    Optional,
    Path, 
    PathLike,
)
from .ContextCore import ContextCore
```

## Context Manager Implementation
```python
class SpecificContext(ContextCore):
    """Context manager for hierarchical operations."""
    
    def __init__(self, path: PathLike, **kwargs):
        """Initialize context with path and options."""
        super().__init__(path)
        self._specific_state = None
    
    def __enter__(self):
        """Enter context and setup hierarchical path resolution."""
        super().__enter__()
        # Setup specific context state
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and cleanup."""
        # Cleanup specific state
        super().__exit__(exc_type, exc_val, exc_tb)
```

## Hierarchical Path Resolution
- Use context stack for relative path resolution
- Delegate operations to corresponding operations classes
- Maintain backward compatibility with direct operations

## Operations Delegation
```python
def operation_method(self, *args, **kwargs):
    """Delegate to operations class with resolved path."""
    resolved_path = self.resolve_path(self.path)
    return OperationsClass.operation_method(resolved_path, *args, **kwargs)
```

## Handler Integration
- Use handler registries for format detection
- Support automatic handler selection based on content
- Provide fallback to default handlers

## Error Handling
- Log context entry/exit operations
- Handle path resolution failures gracefully
- Maintain context stack integrity on errors
- Use Rich console for user-friendly error messages

## Testing Patterns
- Test nested context behavior
- Verify path resolution correctness
- Mock operations class dependencies
- Test error conditions and cleanup