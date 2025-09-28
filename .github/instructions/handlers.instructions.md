---
applyTo: "**/handler_*.py"
---
# Handler pattern implementation standards

## Base Handler Classes
```python
from abc import ABC as AbstractBaseClass
from abc import abstract_method as abstract_method
from typing import Dict, Any, List
from ..__base__ import PathLike, logger

class BaseHandler(AbstractBaseClass):
    """Abstract base class for all handlers."""
    
    @abstract_method
    def validate(self, path: PathLike) -> bool:
        """Validate compatibility with this handler."""
        pass
    
    @abstract_method
    def get_info(self, path: PathLike) -> Dict[str, Any]:
        """Get information about the handled object."""
        pass
```

## Concrete Handler Implementation
```python
class ConcreteHandler(BaseHandler):
    """Concrete handler implementation."""
    
    def validate(self, path: PathLike) -> bool:
        """Validate specific format requirements."""
        try:
            # Validation logic
            return True
        except Exception:
            return False
    
    def get_info(self, path: PathLike) -> Dict[str, Any]:
        """Extract format-specific metadata."""
        return {
            'type': 'handler_type',
            'is_valid': self.validate(path),
            # Additional metadata
        }
```

## Registry Integration
- Use factory functions for registry access
- Implement lazy initialization patterns
- Support runtime handler registration:
```python
def get_handler_registry() -> HandlerRegistry:
    """Get global handler registry."""
    global _handlers
    if _handlers is None:
        _handlers = create_handler_registry()
    return _handlers
```

## Error Handling
- Return `False` for validation failures
- Log errors with appropriate severity
- Provide error details in metadata when possible
- Handle missing dependencies gracefully

## Testing Requirements
- Test validation logic thoroughly  
- Mock external dependencies (subprocess, file I/O)
- Include performance tests for registry operations
- Test error conditions and edge cases