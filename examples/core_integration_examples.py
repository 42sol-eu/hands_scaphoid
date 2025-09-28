#!/usr/bin/env python3
"""
Core object integration examples with Handler patterns.

This module demonstrates how to integrate the new Handler patterns
with existing FileCore, DirectoryCore, and ExecutableCore objects.
---yaml
File:
    name: core_integration_examples.py
    date: 2025-09-28

Description:
    Example implementations showing Handler pattern integration

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import json
import subprocess

from ..__base__ import PathLike, logger
from .handler_patterns import (
    FileHandler, DirectoryHandler, ExecutableHandler,
    get_file_handler_registry, get_directory_handler_registry, get_executable_handler_registry
)


# =============================================================================
# Enhanced FileCore with Handler Support
# =============================================================================

class EnhancedFileCore:
    """
    Enhanced FileCore that uses Handler patterns for extensible file operations.
    
    This class demonstrates how to integrate FileHandler patterns with the
    existing FileCore functionality while maintaining backward compatibility.
    """
    
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handler = None
        self._metadata_cache = None
    
    @property
    def handler(self) -> FileHandler:
        """Get the appropriate handler for this file."""
        if self._handler is None:
            self._handler = self._detect_handler()
        return self._handler
    
    def _detect_handler(self) -> FileHandler:
        """Detect and return the most appropriate handler for this file."""
        registry = get_file_handler_registry()
        
        # Try handlers in priority order based on file extension and content
        handler_priority = self._get_handler_priority()
        
        for handler_name in handler_priority:
            handler = registry.get(handler_name)
            if handler and handler.validate(self.path):
                logger.debug(f"Selected {handler_name} handler for {self.path}")
                return handler
        
        # Fallback to default handler
        default_handler = registry.get_default()
        logger.debug(f"Using default handler for {self.path}")
        return default_handler
    
    def _get_handler_priority(self) -> List[str]:
        """Determine handler priority based on file extension."""
        suffix = self.path.suffix.lower()
        
        # Extension-based priority mapping
        extension_map = {
            '.json': ['json', 'text'],
            '.txt': ['text'],
            '.md': ['text'],
            '.py': ['text'],
            '.xml': ['xml', 'text'],  # Future handler
            '.csv': ['csv', 'text'],  # Future handler
            '.yaml': ['yaml', 'text'], # Future handler
            '.yml': ['yaml', 'text'],  # Future handler
        }
        
        return extension_map.get(suffix, ['text'])
    
    # Enhanced file operations using handlers
    def read_content(self, **kwargs) -> Any:
        """Read file content using the appropriate handler."""
        try:
            return self.handler.read(self.path, **kwargs)
        except Exception as e:
            logger.error(f"Failed to read {self.path}: {e}")
            raise
    
    def write_content(self, content: Any, **kwargs) -> bool:
        """Write content using the appropriate handler."""
        try:
            return self.handler.write(self.path, content, **kwargs)
        except Exception as e:
            logger.error(f"Failed to write {self.path}: {e}")
            return False
    
    def validate_format(self) -> bool:
        """Validate file format using the handler."""
        return self.handler.validate(self.path)
    
    def get_metadata(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get comprehensive file metadata."""
        if self._metadata_cache is None or not use_cache:
            basic_metadata = self._get_basic_metadata()
            handler_metadata = self.handler.get_metadata(self.path)
            
            self._metadata_cache = {
                **basic_metadata,
                **handler_metadata,
                'handler_type': type(self.handler).__name__
            }
        
        return self._metadata_cache
    
    def _get_basic_metadata(self) -> Dict[str, Any]:
        """Get basic file system metadata."""
        stat = self.path.stat()
        return {
            'path': str(self.path),
            'name': self.path.name,
            'stem': self.path.stem,
            'suffix': self.path.suffix,
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime,
            'created_time': stat.st_ctime,
            'is_file': self.path.is_file(),
            'exists': self.path.exists(),
            'permissions': oct(stat.st_mode)[-3:]
        }
    
    def convert_format(self, target_handler: str, output_path: Optional[PathLike] = None) -> bool:
        """Convert file to different format using different handler."""
        registry = get_file_handler_registry()
        target = registry.get(target_handler)
        
        if not target:
            logger.error(f"Handler '{target_handler}' not found")
            return False
        
        try:
            # Read with current handler
            content = self.read_content()
            
            # Write with target handler
            output_path = output_path or self.path
            return target.write(output_path, content)
            
        except Exception as e:
            logger.error(f"Format conversion failed: {e}")
            return False
    
    # Backward compatibility methods
    def read(self) -> str:
        """Backward compatible read method."""
        content = self.read_content()
        return str(content) if not isinstance(content, str) else content
    
    def write(self, content: str) -> bool:
        """Backward compatible write method."""
        return self.write_content(content)


# =============================================================================
# Enhanced DirectoryCore with Handler Support
# =============================================================================

class EnhancedDirectoryCore:
    """
    Enhanced DirectoryCore that uses Handler patterns for project-aware operations.
    
    This class can detect and work with different project types (Git, Python, Node, etc.)
    using specialized handlers.
    """
    
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handlers = None
        self._primary_handler = None
        self._structure_cache = None
    
    @property
    def handlers(self) -> List[DirectoryHandler]:
        """Get all applicable handlers for this directory."""
        if self._handlers is None:
            self._handlers = self._detect_handlers()
        return self._handlers
    
    @property
    def primary_handler(self) -> Optional[DirectoryHandler]:
        """Get the primary (most specific) handler for this directory."""
        if self._primary_handler is None and self.handlers:
            self._primary_handler = self._select_primary_handler()
        return self._primary_handler
    
    def _detect_handlers(self) -> List[DirectoryHandler]:
        """Detect all applicable handlers for this directory."""
        registry = get_directory_handler_registry()
        applicable = []
        
        for handler_name in registry.list_handlers():
            handler = registry.get(handler_name)
            if handler and handler.validate(self.path):
                applicable.append(handler)
                logger.debug(f"Directory {self.path} matches {handler_name} handler")
        
        return applicable
    
    def _select_primary_handler(self) -> Optional[DirectoryHandler]:
        """Select the most specific handler as primary."""
        if not self.handlers:
            return None
        
        # Priority order (most specific first)
        handler_priority = ['python', 'git', 'node', 'docker', 'web']
        
        for priority_type in handler_priority:
            for handler in self.handlers:
                if priority_type in type(handler).__name__.lower():
                    return handler
        
        # Return first handler if no priority match
        return self.handlers[0]
    
    def get_project_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get comprehensive project information from all handlers."""
        if self._structure_cache is None or not use_cache:
            info = {
                'path': str(self.path),
                'name': self.path.name,
                'handler_count': len(self.handlers),
                'primary_handler': type(self.primary_handler).__name__ if self.primary_handler else None,
                'handlers': {}
            }
            
            # Get information from each handler
            for handler in self.handlers:
                handler_name = type(handler).__name__
                try:
                    handler_info = handler.get_structure_info(self.path)
                    info['handlers'][handler_name] = handler_info
                except Exception as e:
                    logger.error(f"Handler {handler_name} failed to get info: {e}")
                    info['handlers'][handler_name] = {'error': str(e)}
            
            self._structure_cache = info
        
        return self._structure_cache
    
    def initialize_project(self, project_type: str, **kwargs) -> bool:
        """Initialize directory as specific project type."""
        registry = get_directory_handler_registry()
        handler = registry.get(project_type)
        
        if not handler:
            logger.error(f"No handler found for project type: {project_type}")
            return False
        
        try:
            success = handler.initialize(self.path, **kwargs)
            if success:
                # Clear cache to refresh handler detection
                self._handlers = None
                self._primary_handler = None
                self._structure_cache = None
            return success
        except Exception as e:
            logger.error(f"Project initialization failed: {e}")
            return False
    
    def list_project_files(self, pattern: str = "*") -> List[Path]:
        """List files using the primary handler's logic."""
        if self.primary_handler:
            try:
                return self.primary_handler.list_contents(self.path, pattern)
            except Exception as e:
                logger.error(f"Primary handler file listing failed: {e}")
        
        # Fallback to simple glob
        return list(self.path.glob(pattern))
    
    def scan_directory(self, recursive: bool = True) -> Dict[str, Any]:
        """Perform comprehensive directory scan."""
        scan_results = {
            'basic_info': self._get_basic_directory_info(),
            'project_info': self.get_project_info(),
            'file_summary': self._get_file_summary() if recursive else {}
        }
        
        return scan_results
    
    def _get_basic_directory_info(self) -> Dict[str, Any]:
        """Get basic directory information."""
        try:
            stat = self.path.stat()
            return {
                'exists': self.path.exists(),
                'is_dir': self.path.is_dir(),
                'modified_time': stat.st_mtime,
                'created_time': stat.st_ctime,
                'permissions': oct(stat.st_mode)[-3:],
                'item_count': len(list(self.path.iterdir())) if self.path.exists() else 0
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _get_file_summary(self) -> Dict[str, Any]:
        """Get summary of files in directory."""
        if not self.path.exists():
            return {}
        
        file_types = {}
        total_size = 0
        file_count = 0
        
        try:
            for item in self.path.rglob('*'):
                if item.is_file():
                    file_count += 1
                    size = item.stat().st_size
                    total_size += size
                    
                    ext = item.suffix.lower() or 'no_extension'
                    if ext not in file_types:
                        file_types[ext] = {'count': 0, 'total_size': 0}
                    
                    file_types[ext]['count'] += 1
                    file_types[ext]['total_size'] += size
        except Exception as e:
            logger.error(f"File summary failed: {e}")
            return {'error': str(e)}
        
        return {
            'total_files': file_count,
            'total_size_bytes': total_size,
            'file_types': file_types
        }


# =============================================================================
# Enhanced ExecutableCore with Handler Support
# =============================================================================

class EnhancedExecutableCore:
    """
    Enhanced ExecutableCore that uses Handler patterns for format-aware execution.
    
    This class can detect and execute different executable types using
    specialized handlers.
    """
    
    def __init__(self, path: PathLike):
        self.path = Path(path)
        self._handler = None
        self._info_cache = None
    
    @property
    def handler(self) -> ExecutableHandler:
        """Get the appropriate handler for this executable."""
        if self._handler is None:
            self._handler = self._detect_handler()
        return self._handler
    
    def _detect_handler(self) -> ExecutableHandler:
        """Detect and return the most appropriate handler."""
        registry = get_executable_handler_registry()
        
        # Try handlers based on file extension and content
        handler_candidates = self._get_handler_candidates()
        
        for handler_name in handler_candidates:
            handler = registry.get(handler_name)
            if handler and handler.validate(self.path):
                logger.debug(f"Selected {handler_name} handler for {self.path}")
                return handler
        
        # Fallback to default
        default_handler = registry.get_default()
        logger.debug(f"Using default handler for {self.path}")
        return default_handler
    
    def _get_handler_candidates(self) -> List[str]:
        """Get candidate handlers based on file characteristics."""
        candidates = []
        
        # Extension-based detection
        suffix = self.path.suffix.lower()
        extension_map = {
            '.py': ['python'],
            '.sh': ['shell'],
            '.ps1': ['powershell'],
            '.js': ['node'],
            '.exe': ['binary'],
            '.msi': ['installer'],
        }
        
        candidates.extend(extension_map.get(suffix, []))
        
        # Content-based detection for scripts
        if suffix in ['.py', '.sh', '.js']:
            try:
                with open(self.path, 'r', encoding='utf-8', errors='ignore') as f:
                    first_line = f.readline().strip()
                    if first_line.startswith('#!'):
                        if 'python' in first_line:
                            candidates.insert(0, 'python')
                        elif 'bash' in first_line or 'sh' in first_line:
                            candidates.insert(0, 'shell')
                        elif 'node' in first_line:
                            candidates.insert(0, 'node')
            except Exception:
                pass
        
        return candidates or ['python']  # Default fallback
    
    def execute(self, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute using the appropriate handler."""
        try:
            return self.handler.execute(self.path, args, **kwargs)
        except Exception as e:
            logger.error(f"Execution failed for {self.path}: {e}")
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'error': str(e)
            }
    
    def test_executable(self) -> bool:
        """Test if executable can run successfully."""
        return self.handler.test(self.path)
    
    def get_executable_info(self, use_cache: bool = True) -> Dict[str, Any]:
        """Get comprehensive executable information."""
        if self._info_cache is None or not use_cache:
            basic_info = self._get_basic_executable_info()
            handler_info = self.handler.get_info(self.path)
            
            self._info_cache = {
                **basic_info,
                **handler_info,
                'handler_type': type(self.handler).__name__,
                'is_executable': self.test_executable()
            }
        
        return self._info_cache
    
    def _get_basic_executable_info(self) -> Dict[str, Any]:
        """Get basic executable file information."""
        stat = self.path.stat()
        return {
            'path': str(self.path),
            'name': self.path.name,
            'size_bytes': stat.st_size,
            'permissions': oct(stat.st_mode)[-3:],
            'is_executable_permission': bool(stat.st_mode & 0o111),
            'modified_time': stat.st_mtime,
            'exists': self.path.exists()
        }
    
    def run_with_timeout(self, args: List[str] = None, timeout: int = 30, **kwargs) -> Dict[str, Any]:
        """Execute with timeout protection."""
        kwargs['timeout'] = timeout
        return self.execute(args, **kwargs)
    
    def get_version(self) -> Optional[str]:
        """Try to get version information from executable."""
        version_args = ['--version', '-v', '-V', 'version']
        
        for arg in version_args:
            try:
                result = self.execute([arg])
                if result.get('success') and result.get('stdout'):
                    return result['stdout'].strip()
            except Exception:
                continue
        
        return None


# =============================================================================
# Usage Examples and Factory Functions
# =============================================================================

def create_enhanced_file(path: PathLike) -> EnhancedFileCore:
    """Factory function to create enhanced file objects."""
    return EnhancedFileCore(path)


def create_enhanced_directory(path: PathLike) -> EnhancedDirectoryCore:
    """Factory function to create enhanced directory objects."""
    return EnhancedDirectoryCore(path)


def create_enhanced_executable(path: PathLike) -> EnhancedExecutableCore:
    """Factory function to create enhanced executable objects."""
    return EnhancedExecutableCore(path)


# Example usage functions
def demonstrate_file_handling():
    """Demonstrate enhanced file handling capabilities."""
    print("=== Enhanced File Handling Demo ===")
    
    # Create a JSON file
    json_file = Path("demo.json")
    data = {"name": "Demo", "version": "1.0", "features": ["handlers", "validation"]}
    
    # Create enhanced file object
    file_obj = create_enhanced_file(json_file)
    
    # Write using JSON handler
    if file_obj.write_content(data, indent=2):
        print(f"✓ JSON file written using {type(file_obj.handler).__name__}")
    
    # Read back using JSON handler
    read_data = file_obj.read_content()
    print(f"✓ JSON data read: {read_data}")
    
    # Get metadata
    metadata = file_obj.get_metadata()
    print(f"✓ File metadata: handler={metadata['handler_type']}, size={metadata['size_bytes']} bytes")
    
    # Validate format
    is_valid = file_obj.validate_format()
    print(f"✓ JSON validation: {is_valid}")
    
    # Clean up
    json_file.unlink(missing_ok=True)


def demonstrate_directory_handling():
    """Demonstrate enhanced directory handling capabilities."""
    print("\n=== Enhanced Directory Handling Demo ===")
    
    # Assume we're in a project directory
    current_dir = Path.cwd()
    dir_obj = create_enhanced_directory(current_dir)
    
    # Get project information
    project_info = dir_obj.get_project_info()
    print(f"✓ Detected {project_info['handler_count']} project types")
    print(f"✓ Primary handler: {project_info['primary_handler']}")
    
    # List handlers
    for handler_name, info in project_info['handlers'].items():
        print(f"  - {handler_name}: {info.get('type', 'unknown type')}")
    
    # Scan directory
    scan_result = dir_obj.scan_directory(recursive=False)
    print(f"✓ Directory scan completed: {scan_result['basic_info']['item_count']} items")


def demonstrate_executable_handling():
    """Demonstrate enhanced executable handling capabilities."""
    print("\n=== Enhanced Executable Handling Demo ===")
    
    # Create a simple Python script
    script_path = Path("demo_script.py")
    script_content = '''#!/usr/bin/env python3
"""Demo script for executable handling."""
import sys
print(f"Hello from Python {sys.version_info.major}.{sys.version_info.minor}!")
print("Arguments:", sys.argv[1:])
'''
    
    script_path.write_text(script_content)
    
    # Create enhanced executable object
    exe_obj = create_enhanced_executable(script_path)
    
    # Get executable info
    exe_info = exe_obj.get_executable_info()
    print(f"✓ Executable info: handler={exe_info['handler_type']}")
    print(f"✓ Has shebang: {exe_info.get('has_shebang', False)}")
    print(f"✓ Import count: {len(exe_info.get('imports', []))}")
    
    # Test execution
    if exe_obj.test_executable():
        print("✓ Executable test passed")
        
        # Execute with arguments
        result = exe_obj.execute(['arg1', 'arg2'])
        if result['success']:
            print(f"✓ Execution successful:")
            print(f"  Output: {result['stdout'].strip()}")
    
    # Clean up
    script_path.unlink(missing_ok=True)


if __name__ == "__main__":
    """Run all demonstrations."""
    demonstrate_file_handling()
    demonstrate_directory_handling()
    demonstrate_executable_handling()
    print("\n=== All demonstrations completed ===")