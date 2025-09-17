# API Reference: Hierarchical File System Context Managers

## Overview

The hands-scaphoid package provides hierarchical file system context managers that allow working with directories, files, and archives in a structured, chainable manner with support for global function access.

## Base Classes

### Context

The `Context` class is the abstract base class for all hierarchical file system operations.

```python
from hands_scaphoid.Context import Context
```

#### Constructor

```python
Context(path: PathLike, create: bool = True, dry_run: bool = False, enable_globals: bool = False)
```

**Parameters:**
- `path`: The file system path (relative or absolute)
- `create`: Whether to create the path if it doesn't exist (default: True)
- `dry_run`: Whether to simulate operations without making actual changes (default: False)
- `enable_globals`: Whether to enable global function access within context (default: False)

#### Key Methods

- `resolve_path() -> Path`: Resolve the absolute path for this context
- `__enter__()`: Enter the context manager
- `__exit__()`: Exit the context manager and cleanup

---

## Directory Class

The `Directory` class provides directory context management with automatic working directory changes.

```python
from hands_scaphoid.Directory import Directory
```

### Constructor

```python
Directory(path: PathLike, create: bool = True, dry_run: bool = False, enable_globals: bool = False)
```

### Context Manager Usage

```python
with Directory('~/projects') as home_projects:
    with Directory('myproject') as project:
        # Now working in ~/projects/myproject
        project.list_contents()
        project.create_subdirectory('src')
```

### Global Functions Usage

When `enable_globals=True`, methods can be called without object prefix:

```python
with Directory('~/projects', enable_globals=True):
    list_contents()  # Instead of directory.list_contents()
    create_subdirectory('src')
    list_contents()
```

### Methods

#### `list_contents() -> List[str]`
List all items in the directory.

**Returns:** List of file and directory names

**Example:**
```python
with Directory('/home/user') as home:
    contents = home.list_contents()
    print(contents)  # ['Documents', 'Downloads', 'Pictures', ...]
```

#### `create_subdirectory(name: str) -> 'Directory'`
Create a subdirectory within the current context.

**Parameters:**
- `name`: Name of the subdirectory to create

**Returns:** New Directory instance for method chaining

**Example:**
```python
with Directory('/tmp') as temp:
    temp.create_subdirectory('project').create_subdirectory('src')
```

#### `list_files(extension: str = None) -> List[str]`
List files in the directory, optionally filtered by extension.

**Parameters:**
- `extension`: File extension filter (optional, without dot)

**Returns:** List of filenames

**Example:**
```python
with Directory('/home/user/documents') as docs:
    python_files = docs.list_files('py')
    all_files = docs.list_files()
```

### Standalone Methods

#### `Directory.create_directory(path: PathLike) -> None`
Create a directory without using context manager.

**Parameters:**
- `path`: Directory path to create

**Example:**
```python
Directory.create_directory('/tmp/standalone_dir')
```

---

## File Class

The `File` class provides file context management with automatic file handle management.

```python
from hands_scaphoid.File import File
```

### Constructor

```python
File(path: PathLike, create: bool = True, mode: str = 'r+', 
     encoding: str = 'utf-8', dry_run: bool = False, enable_globals: bool = False)
```

**Parameters:**
- `path`: The file path (relative or absolute)
- `create`: Whether to create the file if it doesn't exist (default: True)
- `mode`: File open mode (default: 'r+' for read/write)
- `encoding`: File encoding (default: 'utf-8')
- `dry_run`: Whether to simulate operations without making actual changes
- `enable_globals`: Whether to enable global function access within context

### Context Manager Usage

```python
with File('config.txt') as config:
    config.write_line('# Configuration file')
    config.add_heading('Database Settings')
    config.write_line('host=localhost')
    config.write_line('port=5432')
```

### Global Functions Usage

```python
with File('config.txt', enable_globals=True):
    write_line('# Configuration file')
    add_heading('Database Settings')
    write_content('host=localhost\nport=5432')
```

### Methods

#### `write_line(content: str) -> 'File'`
Write a line to the file with automatic newline.

**Parameters:**
- `content`: Text content to write

**Returns:** Self for method chaining

#### `write_content(content: str) -> 'File'`
Write content to the file without automatic newline.

**Parameters:**
- `content`: Text content to write

**Returns:** Self for method chaining

#### `add_heading(title: str, level: int = 1) -> 'File'`
Add a markdown-style heading to the file.

**Parameters:**
- `title`: Heading text
- `level`: Heading level (1-6, default: 1)

**Returns:** Self for method chaining

#### `read_content() -> str`
Read the entire file content.

**Returns:** File content as string

#### `read_lines() -> List[str]`
Read all lines from the file.

**Returns:** List of lines

### Standalone Methods

#### `File.write_file(path: PathLike, content: str) -> None`
Write content to a file without using context manager.

**Parameters:**
- `path`: File path
- `content`: Content to write

#### `File.read_file(path: PathLike) -> str`
Read content from a file without using context manager.

**Parameters:**
- `path`: File path

**Returns:** File content

---

## Archive Class

The `Archive` class provides archive context management supporting ZIP, TAR, TAR.GZ, and TAR.BZ2 formats.

```python
from hands_scaphoid.Archive import Archive
```

### Constructor

```python
Archive(source: Optional[PathLike] = None, target: Optional[PathLike] = None, 
        archive_type: str = 'zip', create: bool = True, dry_run: bool = False, 
        enable_globals: bool = False)
```

**Parameters:**
- `source`: Source directory, file, or existing archive to work with (optional)
- `target`: Target archive file path (defaults to source name with archive extension)
- `archive_type`: Type of archive ('zip', 'tar', 'tar.gz', 'tar.bz2')
- `create`: Whether to create the archive if it doesn't exist
- `dry_run`: Whether to simulate operations without making actual changes
- `enable_globals`: Whether to enable global function access within context

### Context Manager Usage

```python
with Archive('project.zip', create=True) as archive:
    archive.add_file('README.md')
    archive.add_directory('src')
    archive.list_contents()
```

### Global Functions Usage

```python
with Archive('project.zip', enable_globals=True):
    add_file('README.md')
    add_directory('src')
    list_contents()
```

### Methods

#### `add_file(file_path: PathLike, archive_path: str = None) -> 'Archive'`
Add a file to the archive.

**Parameters:**
- `file_path`: Path to the file to add
- `archive_path`: Path within archive (optional, defaults to filename)

**Returns:** Self for method chaining

#### `add_directory(dir_path: PathLike, archive_path: str = None) -> 'Archive'`
Add a directory and its contents to the archive.

**Parameters:**
- `dir_path`: Path to the directory to add
- `archive_path`: Path within archive (optional, defaults to directory name)

**Returns:** Self for method chaining

#### `list_contents() -> List[str]`
List contents of the archive.

**Returns:** List of file paths in the archive

#### `extract_file(archive_path: str, target_path: PathLike = None) -> 'Archive'`
Extract a specific file from the archive.

**Parameters:**
- `archive_path`: Path of file within archive
- `target_path`: Target extraction path (optional)

**Returns:** Self for method chaining

#### `extract_all(target_path: PathLike = None) -> 'Archive'`
Extract all contents from the archive.

**Parameters:**
- `target_path`: Target extraction directory (optional)

**Returns:** Self for method chaining

### Standalone Methods

#### `Archive.create_archive(archive_path: PathLike, source_path: PathLike, archive_type: str = 'zip') -> None`
Create an archive without using context manager.

**Parameters:**
- `archive_path`: Path for the new archive
- `source_path`: Source directory or file to archive
- `archive_type`: Type of archive to create

---

## Global Functions Feature

When `enable_globals=True` is set on any context manager, the context's methods become available as global functions within the context scope.

### How It Works

```python
# Traditional usage
with Directory('mydir') as d:
    d.list_contents()
    d.create_subdirectory('subdir')

# Global functions usage
with Directory('mydir', enable_globals=True):
    list_contents()        # No object prefix needed
    create_subdirectory('subdir')
```

### Nested Contexts

When contexts are nested, the inner context's global functions take precedence:

```python
with Directory('mydir', enable_globals=True):
    list_contents()  # Directory.list_contents()
    
    with File('myfile.txt', enable_globals=True):
        write_line('text')    # File.write_line()
        # list_contents() would fail here (not a File method)
    
    list_contents()  # Directory.list_contents() available again
```

### Cleanup

Global functions are automatically cleaned up when exiting contexts, preventing namespace pollution.

---

## Dry-Run Mode

All classes support dry-run mode for testing operations without making actual changes.

```python
with Directory('test', dry_run=True, enable_globals=True):
    create_subdirectory('would_create')  # Shows what would be created
    list_contents()                      # Shows what would be listed

with File('test.txt', dry_run=True, enable_globals=True):
    write_line('would write this')       # Shows what would be written
```

---

## Method Chaining

All mutation methods return `self` to enable method chaining:

```python
with File('config.txt') as config:
    config.add_heading('Settings') \
          .write_line('key=value') \
          .write_line('debug=true')

with Archive('project.zip') as archive:
    archive.add_file('README.md') \
           .add_directory('src') \
           .add_file('LICENSE')
```

---

## Error Handling

All classes provide comprehensive error handling with descriptive messages using rich console output for better visibility.

Common exceptions:
- `PermissionError`: When lacking permissions for file operations
- `FileNotFoundError`: When referenced files don't exist
- `ValueError`: When invalid parameters are provided
- `RuntimeError`: When context management rules are violated

---

## Examples

### Basic Usage

```python
from hands_scaphoid import Directory, File, Archive

# Create a project structure
with Directory('myproject', create=True) as project:
    with Directory('src') as src:
        with File('main.py') as main:
            main.add_heading('Main Application', 1)
            main.write_line('#!/usr/bin/env python3')
            main.write_line('print("Hello, World!")')
    
    with Directory('docs') as docs:
        with File('README.md') as readme:
            readme.add_heading('My Project')
            readme.write_line('This is my project description.')
    
    # Create an archive of the project
    with Archive('myproject.zip') as archive:
        archive.add_directory('src')
        archive.add_directory('docs')
```

### Global Functions Usage

```python
# Using global functions for cleaner syntax
with Directory('myproject', create=True, enable_globals=True):
    create_subdirectory('src')
    
    with File('src/main.py', enable_globals=True):
        add_heading('Main Application')
        write_line('#!/usr/bin/env python3')
        write_line('print("Hello, World!")')
    
    with Archive('project.zip', enable_globals=True):
        add_directory('src')
        list_contents()
```

### Dry-Run Testing

```python
# Test operations without making changes
with Directory('testdir', dry_run=True, enable_globals=True):
    create_subdirectory('would_create')
    
    with File('would_create.txt', dry_run=True, enable_globals=True):
        write_line('This would be written')
        add_heading('Test Heading')
```