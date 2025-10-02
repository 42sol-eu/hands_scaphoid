# Getting Started with Hands Scaphoid

This guide will help you get started with Hands Scaphoid for hierarchical file system operations.

## Installation

```bash
pip install hands-scaphoid
```

## Basic Concepts

### Operations vs Context Classes

Hands Scaphoid provides two ways to work with files, directories, and archives:

1. **Operations Classes**: Direct static methods for simple operations
   - `FileObject.read_content(path)`
   - `DirectoryObject.create_directory(path)`
   - `ArchiveFile.create_zip_archive(target, source)`

2. **Context Classes**: Context managers for hierarchical operations
   - `FileContext(path)` - for file operations with context
   - `DirectoryContext(path)` - for directory operations with context  
   - `ArchiveContext(source, target)` - for archive operations with context

### Path Resolution

Context managers maintain a stack of current directories. All paths are resolved relative to the current context:

```python
from hands_scaphoid.contexts import DirectoryContext, FileContext

with DirectoryContext('~/projects') as projects:
    # Current context: ~/projects
    
    with DirectoryContext('myproject') as project:
        # Current context: ~/projects/myproject
        
        with FileContext('config.txt') as config:
            # File path resolves to: ~/projects/myproject/config.txt
            config.write_content('debug=true')
```

## File Operations

### Reading Files

```python
from hands_scaphoid.contexts import FileContext
from hands_scaphoid.objects import FileObject

# Using context manager
with FileContext('data.txt') as f:
    content = f.read_content()
    lines = f.read_lines()

# Using operations class directly
from hands_scaphoid.objects import FileObject
content = FileObject.read_content('data.txt')
lines = FileObject.read_lines('data.txt')
```

### Writing Files

```python
# Context manager approach
with FileContext('output.txt') as f:
    f.write_content('Hello, World!')
    f.append_line('New line')
    f.add_heading('Section 1')

# Direct operations
FileObject.write_content('output.txt', 'Hello, World!')
FileObject.append_line('output.txt', 'New line')
```

### Method Chaining

Context classes support method chaining for fluent operations:

```python
with FileContext('report.txt') as report:
    report.write_content('Report Data')\
          .add_heading('Summary')\
          .append_line('Total: 100')\
          .append_line('Average: 25')
```

## Directory Operations

### Creating Directory Structures

```python
from hands_scaphoid.contexts import DirectoryContext
from hands_scaphoid.objects import DirectoryObject

# Using context manager for hierarchical operations
with DirectoryContext('~/projects') as projects:
    with DirectoryContext('newproject', create=True) as project:
        # Create subdirectories
        project.create_directory('src')
        project.create_directory('tests')
        project.create_directory('docs')
        
        # Navigate and create files
        with DirectoryContext('src') as src:
            src.create_file('main.py', '#!/usr/bin/env python3\nprint("Hello!")')

# Direct operations
DirectoryObject.create_directory('path/to/new/directory')
DirectoryObject.create_file('path/to/file.txt', 'content')
```

### Directory Navigation

```python
with DirectoryContext('~') as home:
    # List contents of home directory
    files = home.list_contents()
    print(f"Home contains: {files}")
    
    with DirectoryContext('Documents') as docs:
        # Now in ~/Documents
        doc_files = docs.list_contents()
        
        # Create a new subdirectory
        docs.create_directory('Projects')
```

### Copying and Moving

```python
# Copy directories with context
with DirectoryContext('~/projects') as projects:
    projects.copy_directory('template', 'new_project')
    
    # Move into the new project
    with DirectoryContext('new_project') as project:
        # Customize the project
        project.create_file('config.json', '{"name": "My Project"}')

# Direct operations
DirectoryObject.copy_directory('source_dir', 'destination_dir')
```

## Archive Operations

### Creating Archives

```python
from hands_scaphoid.contexts import ArchiveContext
from hands_scaphoid.objects import ArchiveFile

# Create ZIP archive with context
with DirectoryContext('~/projects') as projects:
    with ArchiveContext(source='myproject', target='backup.zip') as archive:
        # Archive is automatically created with the source directory
        contents = archive.list_contents()
        print(f"Archive contains: {contents}")

# Create TAR.GZ archive
with ArchiveContext(source='myproject', target='backup.tar.gz', archive_type='tar.gz') as archive:
    info = archive.get_archive_info()
    print(f"Compression ratio: {info['compression_ratio']:.2f}")

# Direct operations
ArchiveFile.create_zip_archive('backup.zip', 'source_directory')
ArchiveFile.create_tar_archive('backup.tar.gz', 'source_directory', 'gz')
```

### Extracting Archives

```python
# Extract with context
with DirectoryContext('~/backups') as backups:
    with ArchiveContext(target='project_backup.zip') as archive:
        # Extract all contents
        archive.extract_all('restored_project')
        
        # Or extract specific files
        archive.extract_file('README.md', 'extracted_readme')

# Direct operations
ArchiveFile.extract_archive('backup.zip', 'output_directory')
```

### Selective Archiving

```python
# Create archive by adding files selectively
with ArchiveContext(target='selective_backup.zip') as archive:
    archive.add_file('important_config.json')
    archive.add_file('critical_data.csv')
    archive.add_directory('essential_scripts')
    
    # Check what we've added
    contents = archive.list_contents()
    print(f"Selective archive contains: {contents}")
```

## Global Functions Mode

For script-like usage, enable global functions within contexts:

```python
from hands_scaphoid.contexts import DirectoryContext

# Enable global functions
with DirectoryContext('~/projects', enable_globals=True):
    # Functions are now available globally
    create_directory('newproject')
    change_directory('newproject')
    
    # Create project structure
    create_file('README.md', '# My Project')
    create_directory('src')
    create_directory('tests')
    
    # Navigate and create more files
    change_directory('src')
    create_file('main.py', '''#!/usr/bin/env python3
"""Main module for my project."""

def main():
    print("Hello from my project!")

if __name__ == "__main__":
    main()
''')
    
    # Go back and list contents
    change_directory('..')
    files = list_contents('.')
    print(f"Project structure: {files}")
```

## Dry Run Mode

Test operations without making actual changes:

```python
# Dry run mode shows what would happen
with DirectoryContext('~/test', dry_run=True) as test:
    test.create_directory('newdir')  # Shows: [DRY RUN] Would create directory
    test.create_file('test.txt', 'content')  # Shows: [DRY RUN] Would create file

with FileContext('test.txt', dry_run=True) as f:
    f.write_content('new content')  # Shows: [DRY RUN] Would write to file
    f.append_line('extra line')  # Shows: [DRY RUN] Would append to file
```

## Error Handling

Hands Scaphoid provides clear error handling:

```python
from pathlib import Path

try:
    with DirectoryContext('/nonexistent/path') as ctx:
        ctx.create_file('test.txt', 'content')
except FileNotFoundError as e:
    print(f"Directory not found: {e}")

try:
    content = File.read_content('missing_file.txt')
except FileNotFoundError as e:
    print(f"File not found: {e}")

# Check if paths exist before operations
if Directory.directory_exists('path/to/check'):
    with DirectoryContext('path/to/check') as ctx:
        # Safe to proceed
        files = ctx.list_contents()
```

## Rich Console Output

All operations provide beautiful colored console output:

- ✅ **Green**: Successful operations
- ❌ **Red**: Errors and failures  
- ⚠️ **Yellow**: Warnings and notes
- 📁 **Blue**: Directory operations
- 📄 **Cyan**: File operations
- 📦 **Magenta**: Archive operations
- 🔄 **Dim**: Dry run operations

## Complete Example

Here's a complete example that demonstrates multiple features:

```python
#!/usr/bin/env python3
"""
Complete project setup example using Hands Scaphoid.
"""

from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext

def setup_python_project(project_name: str):
    """Set up a complete Python project structure."""
    
    with DirectoryContext('~/projects') as projects:
        # Create project directory
        with DirectoryContext(project_name, create=True) as project:
            print(f"Setting up Python project: {project_name}")
            
            # Create project structure
            project.create_directory('src')
            project.create_directory('tests')
            project.create_directory('docs')
            
            # Create main package
            with DirectoryContext('src') as src:
                with DirectoryContext(project_name, create=True) as pkg:
                    # Package __init__.py
                    with FileContext('__init__.py') as init:
                        init.write_content(f'"""The {project_name} package."""')\
                            .append_line(f'__version__ = "0.1.0"')
                    
                    # Main module
                    with FileContext('main.py') as main:
                        main.write_content('#!/usr/bin/env python3')\
                            .append_line(f'"""Main module for {project_name}."""')\
                            .append_line('')\
                            .append_line('def main():')\
                            .append_line(f'    print("Hello from {project_name}!")')\
                            .append_line('')\
                            .append_line('if __name__ == "__main__":')\
                            .append_line('    main()')
            
            # Create tests
            with DirectoryContext('tests') as tests:
                with FileContext('test_main.py') as test:
                    test.write_content(f'"""Tests for {project_name}."""')\
                        .append_line('import pytest')\
                        .append_line(f'from {project_name} import main')\
                        .append_line('')\
                        .append_line('def test_main():')\
                        .append_line('    """Test the main function."""')\
                        .append_line('    # Test implementation here')\
                        .append_line('    pass')
            
            # Create documentation
            with DirectoryContext('docs') as docs:
                with FileContext('README.md') as readme:
                    readme.write_content(f'# {project_name.title()}')\
                          .append_line('')\
                          .append_line('A Python project created with Hands Scaphoid.')\
                          .append_line('')\
                          .add_heading('Installation')\
                          .append_line('```bash')\
                          .append_line('pip install -e .')\
                          .append_line('```')\
                          .append_line('')\
                          .add_heading('Usage')\
                          .append_line('```python')\
                          .append_line(f'from {project_name} import main')\
                          .append_line('main()')\
                          .append_line('```')
            
            # Create pyproject.toml
            with FileContext('pyproject.toml') as pyproject:
                pyproject.write_content('[build-system]')\
                         .append_line('requires = ["setuptools>=45", "wheel"]')\
                         .append_line('build-backend = "setuptools.build_meta"')\
                         .append_line('')\
                         .append_line('[project]')\
                         .append_line(f'name = "{project_name}"')\
                         .append_line('version = "0.1.0"')\
                         .append_line('description = "A Python project"')\
                         .append_line('authors = [{name = "Your Name", email = "your@email.com"}]')
            
            # Create .gitignore
            with FileContext('.gitignore') as gitignore:
                gitignore.write_content('__pycache__/')\
                        .append_line('*.pyc')\
                        .append_line('*.pyo')\
                        .append_line('*.egg-info/')\
                        .append_line('dist/')\
                        .append_line('build/')\
                        .append_line('.pytest_cache/')
            
            print(f"✅ Project structure created for {project_name}")
            
            # Create backup
            with ArchiveContext(source='.', target=f'{project_name}_initial.zip') as backup:
                print(f"✅ Initial backup created: {project_name}_initial.zip")
                
                # Show backup info
                info = backup.get_archive_info()
                print(f"📦 Backup contains {info['file_count']} files")

if __name__ == "__main__":
    setup_python_project("my_awesome_project")
```

## Next Steps

Now that you understand the basics, explore these advanced topics:

- [Basic Usage](user-guide/basic-usage.md) - More detailed usage examples
- [API Reference](api/api-reference.md) - Complete API documentation
- [Examples](examples.md) - Real-world usage examples

Happy coding! 🚀
    
    # Execute commands in containers
    result = shell.run_in("mycontainer", "ls /app")
    
    # Check if containers are running
    shell.depends_on(["web", "database"])
```

## Installation

```bash
pip install hands-trapezium
```

## Requirements

- Python 3.11+
- Rich library for console output
- Click for CLI interface

## Documentation

For comprehensive documentation, visit: [https://42sol-eu.github.io/hands_scaphoid](https://42sol-eu.github.io/hands_scaphoid)
