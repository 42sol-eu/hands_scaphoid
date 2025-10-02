# Handler Patterns Integration Design

## Overview

This document outlines the integration of extensible Handler patterns with the existing core object system in `hands_scaphoid`. The Handler patterns provide pluggable, extensible behavior for different file types, directory structures, and executable formats.

## Design Philosophy

### Consistency with ArchiveHandler
All handler patterns follow the same design principles established by `ArchiveHandler`:

1. **Abstract Base Classes**: Define clear interfaces and common behavior
2. **Concrete Implementations**: Provide specific handlers for different types
3. **Registry Pattern**: Centralized management with runtime extensibility
4. **Validation Focus**: Strong emphasis on validating compatibility
5. **Error Handling**: Comprehensive error handling with logging
6. **Metadata Rich**: Provide detailed information about handled objects

### Integration with Core Objects

The handler patterns integrate with the existing core objects (`FileObject`, `DirectoryObject`, `ExecutableCore`) by:

- **Composition over Inheritance**: Handlers are used by core objects, not inherited
- **Strategy Pattern**: Core objects can switch handlers based on content type
- **Runtime Discovery**: Handlers are selected dynamically based on validation
- **Backward Compatibility**: Existing functionality remains unchanged

## FileHandler Pattern

### Purpose
Handle different file formats with specialized operations for reading, writing, and validation.

### Core Interface
```python
class FileHandler(ABC):
    @abstract_method
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs) -> Any
    @abstract_method
    def read(self, file_path: PathLike, **kwargs) -> Any
    @abstract_method
    def write(self, file_path: PathLike, content: Any, **kwargs) -> bool
    @abstract_method
    def validate(self, file_path: PathLike) -> bool
    @abstract_method
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]
```

### Implementations

#### TextFileHandler
- **Purpose**: Handle plain text files with encoding support
- **Features**: Configurable encoding, line/word counting, empty file detection
- **Use Cases**: Configuration files, source code, documentation

#### JsonFileHandler  
- **Purpose**: Handle JSON files with validation and formatting
- **Features**: Syntax validation, pretty printing, structure analysis
- **Use Cases**: Configuration files, API responses, data storage

#### Planned Implementations
- **XmlFileHandler**: XML parsing and validation
- **CsvFileHandler**: CSV reading/writing with dialect detection
- **ImageFileHandler**: Image metadata and basic operations
- **BinaryFileHandler**: Binary file operations with hex viewing

### Integration with FileObject

```python
class FileObject:
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handler = None
    
    @property
    def handler(self) -> FileHandler:
        if self._handler is None:
            self._handler = self._detect_handler()
        return self._handler
    
    def _detect_handler(self) -> FileHandler:
        registry = get_file_handler_registry()
        
        # Try handlers in priority order
        for handler_name in ['json', 'text']:  # extensible priority
            handler = registry.get(handler_name)
            if handler and handler.validate(self.path):
                return handler
        
        # Fallback to default
        return registry.get_default()
    
    def read_content(self, **kwargs):
        """Read file using appropriate handler."""
        return self.handler.read(self.path, **kwargs)
    
    def write_content(self, content, **kwargs):
        """Write file using appropriate handler."""
        return self.handler.write(self.path, content, **kwargs)
```

## DirectoryHandler Pattern

### Purpose
Handle different directory types with specialized structure management and validation.

### Core Interface
```python
class DirectoryHandler(ABC):
    @abstract_method
    def validate(self, dir_path: PathLike) -> bool
    @abstract_method
    def initialize(self, dir_path: PathLike, **kwargs) -> bool
    @abstract_method
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]
    @abstract_method
    def list_contents(self, dir_path: PathLike, pattern: str = "*") -> List[Path]
```

### Implementations

#### GitProjectHandler
- **Purpose**: Handle Git repositories
- **Features**: Repository validation, branch detection, .gitignore awareness
- **Use Cases**: Source control operations, project analysis

#### PythonProjectHandler
- **Purpose**: Handle Python project structures
- **Features**: Package detection, dependency analysis, project initialization
- **Use Cases**: Python development, package management

#### Planned Implementations
- **NodeProjectHandler**: NPM/Yarn project handling
- **DockerProjectHandler**: Docker container projects
- **WebProjectHandler**: Web application projects
- **GenericProjectHandler**: Fallback for unknown project types

### Integration with DirectoryObject

```python
class DirectoryObject:
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handlers = []
    
    @property
    def handlers(self) -> List[DirectoryHandler]:
        """Get all applicable handlers for this directory."""
        if not self._handlers:
            self._handlers = self._detect_handlers()
        return self._handlers
    
    def _detect_handlers(self) -> List[DirectoryHandler]:
        registry = get_directory_handler_registry()
        applicable = []
        
        for handler_name in registry.list_handlers():
            handler = registry.get(handler_name)
            if handler and handler.validate(self.path):
                applicable.append(handler)
        
        return applicable
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get comprehensive project information."""
        info = {'handlers': []}
        for handler in self.handlers:
            handler_info = handler.get_structure_info(self.path)
            info['handlers'].append(handler_info)
        return info
```

## ExecutableHandler Pattern

### Purpose
Handle different executable types with specialized execution and validation.

### Core Interface
```python
class ExecutableHandler(ABC):
    @abstract_method
    def execute(self, exe_path: PathLike, args: List[str] = None, **kwargs) -> Dict[str, Any]
    @abstract_method
    def validate(self, exe_path: PathLike) -> bool
    @abstract_method
    def get_info(self, exe_path: PathLike) -> Dict[str, Any]
```

### Implementations

#### PythonScriptHandler
- **Purpose**: Handle Python script execution
- **Features**: Syntax validation, import analysis, shebang detection
- **Use Cases**: Script execution, Python development

#### Planned Implementations
- **ShellScriptHandler**: Bash/PowerShell script handling
- **BinaryExecutableHandler**: Native binary execution
- **NodeScriptHandler**: Node.js script execution
- **ContainerHandler**: Docker/Podman container execution

### Integration with ExecutableCore

```python
class ExecutableCore:
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handler = None
    
    @property
    def handler(self) -> ExecutableHandler:
        if self._handler is None:
            self._handler = self._detect_handler()
        return self._handler
    
    def execute(self, args: List[str] = None, **kwargs):
        """Execute using appropriate handler."""
        return self.handler.execute(self.path, args, **kwargs)
    
    def get_execution_info(self):
        """Get executable information."""
        return self.handler.get_info(self.path)
```

## Registry System

### Handler Registry
Each handler type has its own registry following the same pattern as `ArchiveRegistry`:

```python
# Global registries with lazy initialization
_file_handlers = None
_directory_handlers = None
_executable_handlers = None

def get_file_handler_registry() -> HandlerRegistry:
    global _file_handlers
    if _file_handlers is None:
        _file_handlers = create_file_handler_registry()
    return _file_handlers
```

### Registration API
Users can register custom handlers:

```python
# Custom file handler
class MyCustomFileHandler(FileHandler):
    # Implementation...
    pass

# Register it
registry = get_file_handler_registry()
registry.register('mycustom', MyCustomFileHandler())
```

## Testing Strategy

### Unit Tests
Each handler pattern includes comprehensive unit tests:

```python
class TestFileHandlers:
    def test_text_handler_read_write(self, tmp_path):
        handler = TextFileHandler()
        test_file = tmp_path / "test.txt"
        content = "Hello, World!"
        
        assert handler.write(test_file, content)
        assert handler.read(test_file) == content
        assert handler.validate(test_file)
```

### Integration Tests
Test handler integration with core objects:

```python
class TestFileHandlerIntegration:
    def test_core_uses_appropriate_handler(self, tmp_path):
        json_file = tmp_path / "test.json"
        json_file.write_text('{"key": "value"}')
        
        file_core = FileObject(json_file)
        assert isinstance(file_core.handler, JsonFileHandler)
        
        content = file_core.read_content()
        assert content == {"key": "value"}
```

## Migration Plan

### Phase 1: Handler Implementation
1. Implement base handler classes ✓
2. Create concrete handler implementations ✓
3. Set up registry system ✓
4. Write comprehensive tests ✓

### Phase 2: Core Integration
1. Modify `FileObject` to use `FileHandler`
2. Modify `DirectoryObject` to use `DirectoryHandler`
3. Modify `ExecutableCore` to use `ExecutableHandler`
4. Update existing tests

### Phase 3: Documentation and Examples
1. Update API documentation
2. Create usage examples
3. Write migration guide for existing code
4. Update coding style guide

### Phase 4: Extended Handlers
1. Implement additional file handlers (XML, CSV, Image)
2. Implement additional directory handlers (Node, Docker)
3. Implement additional executable handlers (Shell, Binary)
4. Add performance optimizations

## Benefits

### For Users
- **Extensibility**: Easy to add support for new file types
- **Consistency**: Uniform API across different object types
- **Validation**: Robust format validation and error handling
- **Metadata**: Rich information about handled objects

### For Developers
- **Modularity**: Clean separation of concerns
- **Testability**: Each handler can be tested independently
- **Maintainability**: Changes to one handler don't affect others
- **Reusability**: Handlers can be shared across projects

### For the Project
- **Scalability**: Easy to add new formats without core changes
- **Flexibility**: Runtime handler selection and configuration
- **Robustness**: Comprehensive error handling and validation
- **Performance**: Optimized handlers for specific formats

## Implementation Notes

### Error Handling
All handlers follow consistent error handling patterns:
- Return `False` for boolean operations that fail
- Return empty/default values for failed data operations
- Log errors with appropriate severity levels
- Provide error details in metadata when appropriate

### Performance Considerations
- Lazy initialization of registries and handlers
- Caching of detected handlers where appropriate
- Minimal overhead for handler selection
- Efficient validation methods

### Backward Compatibility
- Existing `FileObject`, `DirectoryObject`, `ExecutableCore` APIs remain unchanged
- New functionality is additive
- Default handlers maintain current behavior
- Migration is optional and gradual