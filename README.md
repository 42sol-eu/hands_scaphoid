# Hands Scaphoid - Hierarchical File System Operations with Context Management

[![PyPI version](https://badge.fury.io/py/hands-scaphoid.svg)](https://badge.fury.io/py/hands-scaphoid)
[![Python Support](https://img.shields.io/pypi/pyversions/hands-scaphoid.svg)](https://pypi.org/project/hands-scaphoid/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/42sol-eu/hands_scaphoid/workflows/Tests/badge.svg)](https://github.com/42sol-eu/hands_scaphoid/actions)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://42sol-eu.github.io/hands_scaphoid/)

A Python library for hierarchical file system operations with context management. Provides both standalone operations classes and context managers for files, directories, and archives with path resolution and rich console output.

## 🚀 Features

- **� File Operations**: Read, write, append, and manipulate files with context management
- **📂 Directory Operations**: Create, navigate, copy, and manage directories hierarchically
- **📦 Archive Support**: Create, extract, and manipulate ZIP and TAR archives
- **🔗 Hierarchical Context**: Automatic path resolution based on context stack
- **✨ Rich Output**: Beautiful console output using Rich library
- **🔄 Method Chaining**: Fluent API for chaining operations
- **🔍 Type Safety**: Full type hints for better development experience
- **🎯 Dual Interface**: Both operations classes and context managers
- **🧪 Dry Run Mode**: Test operations without making changes
- **🌍 Global Functions**: Optional global function injection for script-like usage

## 📦 Installation

```bash
pip install hands-scaphoid
```

## 🏃‍♂️ Quick Start

### File Operations

```python
from hands_scaphoid import FileContext, File

# Using context manager for hierarchical operations
with DirectoryContext('~') as home:
    with DirectoryContext('projects/myproject') as project:
        # Context-aware file operations
        with FileContext('config.txt') as config:
            config.write_content('debug=true\nversion=1.0')
            config.add_heading('Settings')
            
        # Read file with automatic path resolution
        with FileContext('README.md') as readme:
            content = readme.read_content()
            print(content)

# Using operations class directly
File.write_content('path/to/file.txt', 'Hello, World!')
content = File.read_content('path/to/file.txt')
```

### Directory Operations

```python
from hands_scaphoid import DirectoryContext, Directory

# Context manager with hierarchical navigation
with DirectoryContext('~') as home:
    with DirectoryContext('projects') as projects:
        # All operations are relative to current context
        projects.create_directory('newproject')
        
        with DirectoryContext('newproject') as project:
            # Nested context - operations are relative to projects/newproject
            project.create_file('main.py', '#!/usr/bin/env python3\nprint("Hello, World!")')
            
            files = project.list_contents()
            print(f"Project files: {files}")

# Direct operations without context
Directory.create_directory('path/to/new/dir')
contents = Directory.list_contents('path/to/dir')
```

### Archive Operations

```python
from hands_scaphoid import ArchiveContext, Archive

# Context manager for archive operations
with DirectoryContext('~/projects') as projects:
    # Create a ZIP archive
    with ArchiveContext(source='myproject', target='backup.zip') as archive:
        archive.add_file('README.md')
        archive.add_directory('src')
        
        # List archive contents
        contents = archive.list_contents()
        print(f"Archive contains: {contents}")
    
    # Extract archive
    with ArchiveContext(target='backup.zip') as archive:
        archive.extract_all('restored_project')

# Direct archive operations
Archive.create_zip_archive('backup.zip', 'source_directory')
Archive.extract_archive('backup.zip', 'extracted_files')
```

### Script-style Usage with Global Functions

```python
from hands_scaphoid import DirectoryContext

# Use global functions for script-like experience
with DirectoryContext('~/projects', enable_globals=True):
    # Functions are available globally within the context
    create_directory('newproject')
    change_directory('newproject')
    
    # Create files with content
    create_file('setup.py', '''
from setuptools import setup, find_packages

setup(
    name="myproject",
    version="0.1.0",
    packages=find_packages(),
)
''')
    
    # Create project structure
    create_directory('src/myproject')
    create_file('src/myproject/__init__.py', '# My Project Package')
    create_file('README.md', '# My Project\n\nA sample project.')
    
    # List project structure
    files = list_contents('.')
    print(f"Project structure: {files}")
```

### Archive Management

```python
from hands_scaphoid import DirectoryContext, ArchiveContext

# Create project backups with compression
with DirectoryContext('~/projects') as projects:
    # Create multiple archive formats
    with ArchiveContext(source='myproject', target='backup.tar.gz', archive_type='tar.gz') as archive:
        # Archive automatically includes the entire directory
        info = archive.get_archive_info()
        print(f"Compression ratio: {info['compression_ratio']:.2f}")
    
    # Selective archiving
    with ArchiveContext(target='important_files.zip') as archive:
        archive.add_file('myproject/README.md')
        archive.add_file('myproject/setup.py')
        archive.add_directory('myproject/src')
```

## 🏗️ Architecture

Hands Scaphoid follows a clean separation of concerns:

### Operations Classes (Pure Functions)
- **`File`**: Static methods for file I/O operations
- **`Directory`**: Static methods for directory operations  
- **`Archive`**: Static methods for archive operations

### Context Classes (Context Managers)
- **`FileContext`**: Context manager that delegates to File operations
- **`DirectoryContext`**: Context manager that delegates to Directory operations
- **`ArchiveContext`**: Context manager that delegates to Archive operations

This design allows you to use either approach:
- **Direct operations**: `File.read_content('path')` for simple tasks
- **Context managers**: `with FileContext('path') as f: f.read_content()` for hierarchical operations

## 🎯 Use Cases

- **Project Setup**: Create consistent project structures with files and directories
- **File Processing**: Read, process, and write files with automatic path resolution
- **Backup Systems**: Create and manage archive files with compression
- **Build Tools**: Automate file operations in build processes
- **Data Processing**: Handle file operations in data pipelines
- **Configuration Management**: Manage configuration files across different environments

## 📚 Documentation

For comprehensive documentation, visit: **[https://42sol-eu.github.io/hands_scaphoid](https://42sol-eu.github.io/hands_scaphoid)**

### Key Concepts

- **Hierarchical Contexts**: Context managers maintain a stack of current directories
- **Path Resolution**: All paths are resolved relative to the current context
- **Method Chaining**: Most operations return `self` for fluent interfaces
- **Rich Output**: Operations provide colored console feedback
- **Dry Run Mode**: Test operations without making file system changes

## Example: Project Generator

```python
#!/usr/bin/env python3
"""
Project generator using Hands/Scaphoid
"""
from hands_scaphoid import DirectoryContext, FileContext

def create_python_project(project_name: str, base_dir: str = "~/projects"):
    """Create a new Python project structure."""
    
    with DirectoryContext(base_dir) as projects:
        with DirectoryContext(project_name, create=True) as project:
            # Create project structure
            project.create_directory('src')
            project.create_directory('tests')
            project.create_directory('docs')
            
            # Create setup files
            with FileContext('pyproject.toml') as pyproject:
                pyproject.write_content(f'''[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "{project_name}"
version = "0.1.0"
description = "A new Python project"
authors = [{{name = "Your Name", email = "your.email@example.com"}}]
''')
            
            with FileContext('README.md') as readme:
                readme.write_content(f'# {project_name.title()}\n\nA new Python project.')
            
            # Create source package
            with DirectoryContext('src') as src:
                with DirectoryContext(project_name, create=True) as pkg:
                    with FileContext('__init__.py') as init:
                        init.write_content(f'"""The {project_name} package."""\n__version__ = "0.1.0"')
                    
                    with FileContext('main.py') as main:
                        main.write_content('''#!/usr/bin/env python3
"""Main module."""

def main():
    """Main function."""
    print("Hello from {project_name}!")

if __name__ == "__main__":
    main()
''')
            
            # Create test file
            with DirectoryContext('tests') as tests:
                with FileContext('test_main.py') as test:
                    test.write_content(f'''"""Tests for {project_name}."""
import pytest
from {project_name} import main

def test_main():
    """Test the main function."""
    # Test implementation here
    pass
''')
            
            print(f"✅ Created Python project: {project_name}")
            
            # Create backup
            with ArchiveContext(source='.', target=f'{project_name}_backup.zip') as backup:
                print(f"✅ Created backup: {project_name}_backup.zip")

if __name__ == "__main__":
    create_python_project("my_awesome_project")
```

## 🔧 Requirements

- Python 3.11+
- Rich library for console output
- pathlib for path operations

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/42sol-eu/hands_scaphoid.git
cd hands_scaphoid
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
mkdocs serve
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Andreas Häberle** - [42sol-eu](https://github.com/42sol-eu)

## 🌟 Support

If you find this project helpful, please consider giving it a star on GitHub! ⭐

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.

# Rersouces (more)
- https://pypi.org/project/rich-click/