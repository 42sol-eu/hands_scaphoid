#!/usr/bin/env python3
"""
Handler patterns design document and implementation suggestions.

This document outlines the proposed handler patterns for extending the core
object system with pluggable, extensible behavior similar to ArchiveHandler.
---yaml
File:
    name: handler_patterns_design.py
    date: 2025-09-28

Description:
    Design document and base classes for extensible handler patterns

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""


# [Standard library imports]
from typing import Any, Dict, List, Optional, Protocol

#%%[ Local imports]
from ..__base__ import (
    AbstractBaseClass,
    abstract_method
    logger,
    Path, 
    PathLike, 
)

#%%[ Class definitions]
# =============================================================================
# Base Handler Protocol and Classes
# =============================================================================

class Handler(Protocol):
    """Base protocol for all handler types."""
    
    def validate(self, path: PathLike) -> bool:
        """Validate that the path/object is compatible with this handler."""
        ...
    
    def get_info(self, path: PathLike) -> Dict[str, Any]:
        """Get information about the object at the given path."""
        ...


# =============================================================================
# FileHandler Pattern
# =============================================================================

class FileHandler(AbstractBaseClass):
    """
    Abstract base class for file handlers.
    
    FileHandlers manage operations on different file types, providing
    specialized behavior for opening, reading, writing, and validating
    files based on their format or purpose.
    """
    
    @abstract_method
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs) -> Any:
        """Open file with appropriate handler for the file type."""
        pass
    
    @abstract_method
    def read(self, file_path: PathLike, **kwargs) -> Any:
        """Read file content using format-specific logic."""
        pass
    
    @abstract_method
    def write(self, file_path: PathLike, content: Any, **kwargs) -> bool:
        """Write content to file using format-specific logic."""
        pass
    
    @abstract_method
    def validate(self, file_path: PathLike) -> bool:
        """Validate file format and structure."""
        pass
    
    @abstract_method
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get file-type specific metadata."""
        pass
    
    def test(self, file_path: PathLike) -> bool:
        """Test file integrity and readability."""
        try:
            return self.validate(file_path) and Path(file_path).exists()
        except Exception as e:
            logger.error(f"File test failed for {file_path}: {e}")
            return False


class TextFileHandler(FileHandler):
    """Handler for plain text files."""
    
    def __init__(self, encoding: str = 'utf-8'):
        self.encoding = encoding
    
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs):
        """Open text file with specified encoding."""
        return open(file_path, mode, encoding=self.encoding, **kwargs)
    
    def read(self, file_path: PathLike, **kwargs) -> str:
        """Read text file content."""
        with self.open(file_path, 'r', **kwargs) as f:
            return f.read()
    
    def write(self, file_path: PathLike, content: str, **kwargs) -> bool:
        """Write text content to file."""
        try:
            with self.open(file_path, 'w', **kwargs) as f:
                f.write(content)
            return True
        except Exception as e:
            logger.error(f"Failed to write text file {file_path}: {e}")
            return False
    
    def validate(self, file_path: PathLike) -> bool:
        """Validate text file by attempting to read it."""
        try:
            with self.open(file_path, 'r') as f:
                f.read(1024)  # Read first chunk to test encoding
            return True
        except (UnicodeDecodeError, OSError):
            return False
    
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get text file metadata."""
        path = Path(file_path)
        try:
            content = self.read(file_path)
            return {
                'encoding': self.encoding,
                'size_bytes': path.stat().st_size,
                'line_count': content.count('\n') + 1 if content else 0,
                'char_count': len(content),
                'word_count': len(content.split()) if content else 0,
                'is_empty': len(content.strip()) == 0
            }
        except Exception as e:
            logger.error(f"Failed to get metadata for {file_path}: {e}")
            return {'error': str(e)}


class JsonFileHandler(FileHandler):
    """Handler for JSON files with validation and formatting."""
    
    def open(self, file_path: PathLike, mode: str = 'r', **kwargs):
        """Open JSON file."""
        return open(file_path, mode, encoding='utf-8', **kwargs)
    
    def read(self, file_path: PathLike, **kwargs) -> Dict[str, Any]:
        """Read and parse JSON content."""
        import json
        with self.open(file_path, 'r') as f:
            return json.load(f)
    
    def write(self, file_path: PathLike, content: Dict[str, Any], 
              indent: int = 2, **kwargs) -> bool:
        """Write formatted JSON content."""
        import json
        try:
            with self.open(file_path, 'w') as f:
                json.dump(content, f, indent=indent, **kwargs)
            return True
        except Exception as e:
            logger.error(f"Failed to write JSON file {file_path}: {e}")
            return False
    
    def validate(self, file_path: PathLike) -> bool:
        """Validate JSON syntax."""
        import json
        try:
            with self.open(file_path, 'r') as f:
                json.load(f)
            return True
        except (json.JSONDecodeError, OSError):
            return False
    
    def get_metadata(self, file_path: PathLike) -> Dict[str, Any]:
        """Get JSON file metadata including structure info."""
        path = Path(file_path)
        try:
            data = self.read(file_path)
            return {
                'size_bytes': path.stat().st_size,
                'json_type': type(data).__name__,
                'key_count': len(data) if isinstance(data, dict) else None,
                'array_length': len(data) if isinstance(data, list) else None,
                'is_valid': True,
                'structure_depth': self._get_json_depth(data)
            }
        except Exception as e:
            return {'is_valid': False, 'error': str(e)}
    
    def _get_json_depth(self, obj, depth=0):
        """Calculate JSON structure depth."""
        if isinstance(obj, dict):
            return max([self._get_json_depth(v, depth + 1) for v in obj.values()], default=depth)
        elif isinstance(obj, list):
            return max([self._get_json_depth(item, depth + 1) for item in obj], default=depth)
        return depth


# =============================================================================
# DirectoryHandler Pattern
# =============================================================================

class DirectoryHandler(AbstractBaseClass):
    """
    Abstract base class for directory handlers.
    
    DirectoryHandlers manage operations on different directory types,
    providing specialized behavior for projects, repositories, and
    special directory structures.
    """
    
    @abstract_method
    def validate(self, dir_path: PathLike) -> bool:
        """Validate directory structure and contents."""
        pass
    
    @abstract_method
    def initialize(self, dir_path: PathLike, **kwargs) -> bool:
        """Initialize directory with required structure."""
        pass
    
    @abstract_method
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get information about directory structure."""
        pass
    
    @abstract_method
    def list_contents(self, dir_path: PathLike, pattern: str = "*") -> List[Path]:
        """List directory contents with optional filtering."""
        pass
    
    def scan(self, dir_path: PathLike, recursive: bool = True) -> Dict[str, Any]:
        """Scan directory and return comprehensive information."""
        return {
            'is_valid': self.validate(dir_path),
            'structure': self.get_structure_info(dir_path),
            'contents': self.list_contents(dir_path) if recursive else []
        }


class GitProjectHandler(DirectoryHandler):
    """Handler for Git repositories."""
    
    def validate(self, dir_path: PathLike) -> bool:
        """Check if directory is a valid Git repository."""
        git_dir = Path(dir_path) / '.git'
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())
    
    def initialize(self, dir_path: PathLike, **kwargs) -> bool:
        """Initialize Git repository."""
        import subprocess
        try:
            result = subprocess.run(['git', 'init', str(dir_path)], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Initialized Git repository at {dir_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to initialize Git repository: {e}")
            return False
    
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get Git repository information."""
        import subprocess
        path = Path(dir_path)
        info = {
            'type': 'git_repository',
            'has_git_dir': (path / '.git').exists(),
            'has_gitignore': (path / '.gitignore').exists(),
            'has_readme': any((path / f).exists() for f in ['README.md', 'README.txt', 'README'])
        }
        
        if self.validate(dir_path):
            try:
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      cwd=dir_path, capture_output=True, text=True)
                info['current_branch'] = result.stdout.strip() if result.returncode == 0 else None
                
                # Get remote info
                result = subprocess.run(['git', 'remote', '-v'], 
                                      cwd=dir_path, capture_output=True, text=True)
                info['has_remote'] = bool(result.stdout.strip()) if result.returncode == 0 else False
                
            except Exception as e:
                logger.warning(f"Failed to get Git info for {dir_path}: {e}")
        
        return info
    
    def list_contents(self, dir_path: PathLike, pattern: str = "*") -> List[Path]:
        """List Git repository contents, respecting .gitignore."""
        import subprocess
        try:
            # Use git ls-files to respect .gitignore
            result = subprocess.run(['git', 'ls-files'], 
                                  cwd=dir_path, capture_output=True, text=True)
            if result.returncode == 0:
                files = [Path(dir_path) / f.strip() for f in result.stdout.split('\n') if f.strip()]
                return [f for f in files if f.match(pattern)]
        except Exception:
            pass
        
        # Fallback to regular directory listing
        return list(Path(dir_path).glob(pattern))


class PythonProjectHandler(DirectoryHandler):
    """Handler for Python projects."""
    
    def validate(self, dir_path: PathLike) -> bool:
        """Check if directory is a Python project."""
        path = Path(dir_path)
        python_indicators = [
            'setup.py', 'pyproject.toml', 'requirements.txt', 
            'Pipfile', 'setup.cfg', 'environment.yml'
        ]
        return any((path / indicator).exists() for indicator in python_indicators)
    
    def initialize(self, dir_path: PathLike, project_name: str = None, **kwargs) -> bool:
        """Initialize Python project structure."""
        path = Path(dir_path)
        project_name = project_name or path.name
        
        try:
            # Create basic structure
            (path / 'src' / project_name).mkdir(parents=True, exist_ok=True)
            (path / 'tests').mkdir(exist_ok=True)
            (path / 'docs').mkdir(exist_ok=True)
            
            # Create basic files
            (path / 'src' / project_name / '__init__.py').touch()
            (path / 'README.md').write_text(f'# {project_name}\n\nA Python project.')
            (path / 'requirements.txt').touch()
            
            logger.info(f"Initialized Python project structure at {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Python project: {e}")
            return False
    
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get Python project information."""
        path = Path(dir_path)
        
        return {
            'type': 'python_project',
            'has_setup_py': (path / 'setup.py').exists(),
            'has_pyproject_toml': (path / 'pyproject.toml').exists(),
            'has_requirements': (path / 'requirements.txt').exists(),
            'has_src_layout': (path / 'src').exists(),
            'has_tests': (path / 'tests').exists(),
            'has_docs': (path / 'docs').exists(),
            'python_files_count': len(list(path.rglob('*.py'))),
            'package_directories': [d.name for d in path.rglob('*') if d.is_dir() and (d / '__init__.py').exists()]
        }
    
    def list_contents(self, dir_path: PathLike, pattern: str = "*.py") -> List[Path]:
        """List Python files in project."""
        return list(Path(dir_path).rglob(pattern))


# =============================================================================
# ExecutableHandler Pattern
# =============================================================================

class ExecutableHandler(AbstractBaseClass):
    """
    Abstract base class for executable handlers.
    
    ExecutableHandlers manage different types of executable files,
    providing specialized behavior for running, validating, and
    managing executable programs.
    """
    
    @abstract_method
    def execute(self, exe_path: PathLike, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute the program with given arguments."""
        pass
    
    @abstract_method
    def validate(self, exe_path: PathLike) -> bool:
        """Validate that the file is a valid executable."""
        pass
    
    @abstract_method
    def get_info(self, exe_path: PathLike) -> Dict[str, Any]:
        """Get executable information (version, dependencies, etc.)."""
        pass
    
    def test(self, exe_path: PathLike) -> bool:
        """Test executable by running with --help or --version."""
        try:
            result = self.execute(exe_path, ['--version'])
            return result.get('returncode') == 0
        except Exception:
            try:
                result = self.execute(exe_path, ['--help'])
                return result.get('returncode') == 0
            except Exception:
                return False


class PythonScriptHandler(ExecutableHandler):
    """Handler for Python scripts."""
    
    def execute(self, exe_path: PathLike, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute Python script."""
        import subprocess
        cmd = ['python', str(exe_path)] + (args or [])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'error': str(e)
            }
    
    def validate(self, exe_path: PathLike) -> bool:
        """Validate Python script syntax."""
        try:
            with open(exe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, exe_path, 'exec')
            return True
        except (SyntaxError, OSError, UnicodeDecodeError):
            return False
    
    def get_info(self, exe_path: PathLike) -> Dict[str, Any]:
        """Get Python script information."""
        path = Path(exe_path)
        info = {
            'type': 'python_script',
            'size_bytes': path.stat().st_size,
            'is_valid': self.validate(exe_path),
            'has_shebang': False,
            'imports': []
        }
        
        try:
            with open(exe_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!') and 'python' in first_line:
                    info['has_shebang'] = True
                
                # Simple import detection
                f.seek(0)
                content = f.read()
                import ast
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        info['imports'].extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            info['imports'].append(node.module)
        except Exception as e:
            info['parse_error'] = str(e)
        
        return info


# =============================================================================
# Handler Registry Pattern
# =============================================================================

class HandlerRegistry:
    """Generic registry for managing handlers of any type."""
    
    def __init__(self, handler_type: type):
        self.handler_type = handler_type
        self.handlers = {}
        self.default_handler = None
    
    def register(self, name: str, handler: Any, is_default: bool = False):
        """Register a handler."""
        if not isinstance(handler, self.handler_type):
            raise TypeError(f"Handler must be instance of {self.handler_type}")
        
        self.handlers[name] = handler
        if is_default:
            self.default_handler = handler
        
        logger.debug(f"Registered {self.handler_type.__name__}: {name}")
    
    def get(self, name: str) -> Optional[Any]:
        """Get handler by name."""
        return self.handlers.get(name)
    
    def get_default(self) -> Optional[Any]:
        """Get default handler."""
        return self.default_handler
    
    def list_handlers(self) -> List[str]:
        """List all registered handler names."""
        return list(self.handlers.keys())


# =============================================================================
# Factory Functions and Convenience APIs
# =============================================================================

def create_file_handler_registry() -> HandlerRegistry:
    """Create and populate file handler registry."""
    registry = HandlerRegistry(FileHandler)
    
    # Register default handlers
    registry.register('text', TextFileHandler(), is_default=True)
    registry.register('json', JsonFileHandler())
    registry.register('utf8', TextFileHandler('utf-8'))
    registry.register('ascii', TextFileHandler('ascii'))
    
    return registry


def create_directory_handler_registry() -> HandlerRegistry:
    """Create and populate directory handler registry."""
    registry = HandlerRegistry(DirectoryHandler)
    
    # Register default handlers
    registry.register('git', GitProjectHandler())
    registry.register('python', PythonProjectHandler())
    
    return registry


def create_executable_handler_registry() -> HandlerRegistry:
    """Create and populate executable handler registry."""
    registry = HandlerRegistry(ExecutableHandler)
    
    # Register default handlers
    registry.register('python', PythonScriptHandler(), is_default=True)
    
    return registry


# Global registries (lazy initialization)
_file_handlers = None
_directory_handlers = None
_executable_handlers = None


def get_file_handler_registry() -> HandlerRegistry:
    """Get global file handler registry."""
    global _file_handlers
    if _file_handlers is None:
        _file_handlers = create_file_handler_registry()
    return _file_handlers


def get_directory_handler_registry() -> HandlerRegistry:
    """Get global directory handler registry."""
    global _directory_handlers
    if _directory_handlers is None:
        _directory_handlers = create_directory_handler_registry()
    return _directory_handlers


def get_executable_handler_registry() -> HandlerRegistry:
    """Get global executable handler registry."""
    global _executable_handlers
    if _executable_handlers is None:
        _executable_handlers = create_executable_handler_registry()
    return _executable_handlers