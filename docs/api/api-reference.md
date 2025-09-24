# API Reference

This is the complete API reference for Hands Scaphoid, covering all modules, classes, and functions.

## Core Components

### Context Managers
- [ShellContext](../objects/shell-context.md) - Primary context manager for shell operations
- [Shell Executable](../objects/shell-executable.md) - Core shell execution class

### Command Modules

#### File Commands
**Module**: `hands_scaphoid.commands.file_commands`

| Function | Status | Description |
|----------|--------|-------------|
| `read(file_path, head=None, tail=None, line_separator='\n', do_print=False)` | ✅ Available | Read file content with optional head/tail limits |
| `filter(name, pattern)` | 🔄 Planned | Filter files by pattern |
| `write(name, data)` | 🔄 Planned | Write data to file |
| `append(name, data)` | 🔄 Planned | Append data to file |
| `create(name, data)` | 🔄 Planned | Create new file with data |

#### Archive Commands  
**Module**: `hands_scaphoid.commands.archive_commands`

| Function | Status | Description |
|----------|--------|-------------|
| `is_archive_file(file_path)` | ✅ Available | Check if file is an archive |
| `create_zip_archive(archive_name, source)` | ✅ Available | Create ZIP archive |
| `create_tar_archive(archive_name, source, compression=None)` | ✅ Available | Create TAR archive |
| `create_7z_archive(archive_name, source)` | ✅ Available | Create 7Z archive |
| `create_rar_archive(archive_name, source)` | ✅ Available | Create RAR archive |
| `extract(archive_path, target_dir)` | ✅ Available | Extract any supported archive |
| `extract_zip_archive(archive_path, target_dir)` | ✅ Available | Extract ZIP archive |
| `extract_tar_archive(archive_path, target_dir, compression=None)` | ✅ Available | Extract TAR archive |
| `extract_7z_archive(archive_path, target_dir)` | ✅ Available | Extract 7Z archive |
| `extract_rar_archive(archive_path, target_dir)` | ✅ Available | Extract RAR archive |
| `list_contents(archive_path)` | ✅ Available | List archive contents |

#### Core Commands
**Module**: `hands_scaphoid.commands.core_commands`

| Function | Status | Description |
|----------|--------|-------------|
| `exists(path)` | ✅ Available | Check if path exists |
| `does_not_exists(path)` | ✅ Available | Check if path does not exist |
| `is_file(path)` | ✅ Available | Check if path is a file |
| `is_directory(path)` | ✅ Available | Check if path is a directory |
| `is_link(path)` | ✅ Available | Check if path is a symbolic link |
| `is_object(path)` | ✅ Available | Check if path is any file system object |
| `is_variable(var)` | ✅ Available | Check if environment variable is defined |
| `is_item(p)` | ✅ Available | Check if item is a file system object or variable |
| `is_git_project(path)` | ✅ Available | Check if directory is a Git project |
| `is_vscode_project(path)` | ✅ Available | Check if directory is a VS Code project |
| `is_hands_project(path)` | ✅ Available | Check if directory is a Hands project |
| `is_project(path)` | ✅ Available | Check if directory is any type of project |
| `get_file_extension(filename)` | ✅ Available | Get file extension (supports complex extensions) |
| `which(executable)` | ✅ Available | Find executable in system PATH |
| `filter(path, filter)` | ✅ Available | Filter directory contents by glob pattern |

### Data Types

#### CompressionType Enum
**Module**: `hands_scaphoid.commands.core_commands`

Supported compression types:
- `ZIP` - ZIP format
- `TAR` - TAR format  
- `GZIP`/`GZ` - GZIP compression
- `BZIP2` - BZIP2 compression
- `XZ` - XZ compression
- `SEVEN_Z` - 7Z format
- `RAR` - RAR format
- `TAR_GZ` - TAR with GZIP compression
- `TAR_BZ2` - TAR with BZIP2 compression
- `TAR_XZ` - TAR with XZ compression

#### PathLike Type
**Module**: `hands_scaphoid.__base__`

Type alias for path-like objects: `Union[str, Path]`

## Object Classes

### [Archive File](objects/archive-file.md)
Object representation of archive files with built-in operations.

### [Directory Core](objects/directory-core.md) 
Object representation of directories with file system operations.

### [Executable Core](objects/executable-core.md)
Object representation of executable files.

### [File Core](objects/file-core.md)
Object representation of regular files with read/write operations.

### [File Script](objects/file-script.md)
Object representation of script files.

### [Item Core](objects/item-core.md)
Base class for all file system items.

### [Object Core](objects/object-core.md)
Base class for file system objects.

### [Shell Executable](objects/shell-executable.md)
Main shell execution class with command allowlisting.

### [Variable Core](objects/variable-core.md)
Object representation of environment variables.

### [Windows Shells](objects/windows-shells.md)
Windows-specific shell implementations (PowerShell, WSL).

## Context Managers

### [Context Managers](contexts/context-managers.md)
Overview of context management functionality.

### [Shell Context](contexts/shell-context.md)
Primary context manager for secure shell operations.

## Testing

Comprehensive test coverage is available for all command modules. See the [Testing Guide](../user-guide/testing.md) for detailed information about:

- Test structure and organization
- Running tests locally
- Coverage reports
- Mocking strategies for external dependencies

## Usage Examples

### Basic File Operations
```python
from hands_scaphoid.commands.file_commands import read
from hands_scaphoid.commands.core_commands import exists, get_file_extension

# Check if file exists
if exists("README.md"):
    # Read file content
    content = read("README.md")
    print(content)

# Get file extension
ext = get_file_extension("archive.tar.gz")
print(f"Extension: {ext}")  # Output: tar.gz
```

### Archive Operations
```python
from hands_scaphoid.commands.archive_commands import (
    create_zip_archive, 
    extract, 
    list_contents
)

# Create archive
if create_zip_archive("backup", "source_directory"):
    print("Archive created successfully")

# List archive contents
files = list_contents("backup.zip")
for file in files:
    print(f"  {file}")

# Extract archive
if extract("backup.zip", "restored_files"):
    print("Archive extracted successfully")
```

### Project Detection
```python
from hands_scaphoid.commands.core_commands import (
    is_git_project,
    is_vscode_project,
    is_project
)

project_dir = "/path/to/project"

if is_git_project(project_dir):
    print("This is a Git repository")

if is_vscode_project(project_dir):
    print("This is a VS Code project")

if is_project(project_dir):
    print("This is some kind of project")
```

## Status Legend

- ✅ **Available**: Fully implemented and tested
- 🔄 **Planned**: Marked as TODO in source code
- 🟢 **Complete**: Full test coverage
- 🟡 **Partial**: Some test coverage
- 🔴 **Needs Work**: Requires attention

For detailed implementation status, see the [Operations Summary](../operations/summary.md).