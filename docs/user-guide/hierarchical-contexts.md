# User Guide: Hierarchical File System Context Managers

## Introduction

The hands-scaphoid package provides powerful hierarchical file system context managers that simplify working with directories, files, and archives. These context managers automatically handle resource management, support method chaining, and can integrate seamlessly with existing shell operations.

## Quick Start

### Basic Directory Operations

```python
from hands_scaphoid import Directory

# Navigate and work within directories
with Directory('~/projects') as projects:
    with Directory('myproject', create=True) as project:
        # Now working in ~/projects/myproject
        project.create_subdirectory('src')
        project.create_subdirectory('docs')
        project.list_contents()
```

### Basic File Operations

```python
from hands_scaphoid import File

# Create and edit files
with File('config.txt', create=True) as config:
    config.add_heading('Configuration')
    config.write_line('debug=true')
    config.write_line('port=8080')
```

### Basic Archive Operations

```python
from hands_scaphoid import Archive

# Create archives
with Archive('backup.zip', create=True) as backup:
    backup.add_file('config.txt')
    backup.add_directory('src')
    backup.list_contents()
```

## Advanced Features

### Global Functions

One of the most powerful features is the ability to call context methods without object prefixes by enabling global functions:

```python
# Traditional approach
with Directory('mydir') as d:
    d.list_contents()
    d.create_subdirectory('subdir')

# Global functions approach
with Directory('mydir', enable_globals=True):
    list_contents()           # Much cleaner!
    create_subdirectory('subdir')
```

#### How Global Functions Work

When `enable_globals=True` is set on a context manager:

1. **Function Injection**: Context methods are temporarily added to Python's built-in namespace
2. **Automatic Cleanup**: Functions are removed when exiting the context
3. **No Pollution**: Global namespace is restored to its original state
4. **Thread-Safe**: Each thread maintains its own global function scope

#### Nested Context Behavior

When contexts are nested, the inner context's functions take precedence:

```python
with Directory('mydir', enable_globals=True):
    list_contents()  # Directory.list_contents()
    
    with File('myfile.txt', enable_globals=True):
        write_line('Hello')  # File.write_line()
        # Note: list_contents() would fail here (not available in File context)
    
    # Back in directory context
    list_contents()  # Directory.list_contents() available again
```

### ShellContext Integration

The hierarchical contexts work seamlessly with the existing `ShellContext`:

```python
from hands_scaphoid import Directory, File, ShellContext

# Combined shell and file operations
with ShellContext() as shell:
    # Shell functions available globally
    allow("git")
    allow("npm")
    
    with Directory('myproject', enable_globals=True):
        # Both shell and directory functions available
        run("git init")
        create_subdirectory('src')
        
        with File('package.json', enable_globals=True):
            write_line('{"name": "myproject"}')
        
        run("npm install")
```

**Important Notes:**
- Both contexts use the same global function injection mechanism
- Functions from the most recently entered context take precedence
- Proper cleanup ensures no conflicts between different context types

### Hierarchical Path Resolution

Contexts automatically resolve paths relative to their parent contexts:

```python
with Directory('/home/user') as home:
    with Directory('projects') as projects:      # /home/user/projects
        with Directory('myapp') as app:          # /home/user/projects/myapp
            with File('config.txt') as config:   # /home/user/projects/myapp/config.txt
                config.write_line('Setting=Value')
```

### Dry-Run Mode

Test your operations without making actual changes:

```python
# Preview what would happen
with Directory('testdir', create=True, dry_run=True, enable_globals=True):
    create_subdirectory('would_create')    # Shows: [DRY RUN] Would create...
    
    with File('test.txt', create=True, dry_run=True, enable_globals=True):
        write_line('Would write this')     # Shows: [DRY RUN] Would append...
        add_heading('Test Heading')
    
    list_contents()                        # Shows: [DRY RUN] Would list...
```

### Method Chaining

All mutation methods return `self` for fluent interfaces:

```python
with File('config.txt') as config:
    config.add_heading('Settings') \
          .write_line('debug=true') \
          .write_line('port=8080') \
          .add_heading('Database', 2) \
          .write_line('host=localhost')

with Archive('project.zip') as archive:
    archive.add_file('README.md') \
           .add_directory('src') \
           .add_file('LICENSE') \
           .list_contents()
```

## Usage Patterns

### Project Scaffolding

```python
from hands_scaphoid import Directory, File

def create_python_project(name: str):
    """Create a standard Python project structure."""
    with Directory(name, create=True, enable_globals=True):
        # Create directory structure
        create_subdirectory('src')
        create_subdirectory('tests')
        create_subdirectory('docs')
        
        # Create main module
        with File(f'src/{name}/__init__.py', enable_globals=True):
            add_heading(f'{name} Package')
            write_line(f'"""The {name} package."""')
            write_line('')
            write_line('__version__ = "0.1.0"')
        
        # Create main module
        with File(f'src/{name}/main.py', enable_globals=True):
            add_heading('Main Module')
            write_line('#!/usr/bin/env python3')
            write_line(f'"""Main module for {name}."""')
        
        # Create README
        with File('README.md', enable_globals=True):
            add_heading(name)
            write_line(f'Description of {name} project.')
        
        # Create requirements
        with File('requirements.txt', enable_globals=True):
            write_line('# Add your dependencies here')

# Usage
create_python_project('myawesome_project')
```

### Backup Creation

```python
from hands_scaphoid import Directory, Archive
from datetime import datetime

def create_backup(source_dir: str):
    """Create a timestamped backup archive."""
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_name = f'backup_{timestamp}.tar.gz'
    
    with Directory(source_dir, enable_globals=True):
        # List what will be backed up
        files = list_contents()
        print(f"Backing up {len(files)} items...")
        
        with Archive(f'../backups/{backup_name}', 
                    archive_type='tar.gz', 
                    create=True, 
                    enable_globals=True):
            # Add all files and directories
            for item in files:
                if Path(item).is_file():
                    add_file(item)
                else:
                    add_directory(item)
            
            print(f"Backup created: {backup_name}")
            list_contents()

# Usage
create_backup('/home/user/documents')
```

### Configuration Management

```python
from hands_scaphoid import File

def create_config(env: str = 'development'):
    """Create environment-specific configuration."""
    config_file = f'config/{env}.txt'
    
    with File(config_file, create=True, enable_globals=True):
        add_heading(f'{env.title()} Configuration')
        
        if env == 'development':
            write_line('debug=true')
            write_line('host=localhost')
            write_line('port=3000')
        elif env == 'production':
            write_line('debug=false')
            write_line('host=0.0.0.0')
            write_line('port=80')
        
        add_heading('Database Settings', 2)
        write_line(f'db_name=myapp_{env}')

# Create multiple environment configs
for env in ['development', 'staging', 'production']:
    create_config(env)
```

## Best Practices

### 1. Use Global Functions for Cleaner Code

```python
# ✅ Good: Clean and readable
with Directory('myproject', enable_globals=True):
    create_subdirectory('src')
    create_subdirectory('tests')
    list_contents()

# ❌ Verbose: Too many object references
with Directory('myproject') as d:
    d.create_subdirectory('src')
    d.create_subdirectory('tests')
    d.list_contents()
```

### 2. Use Dry-Run for Testing

```python
# Test your script logic without side effects
def setup_project(name: str, dry_run: bool = False):
    with Directory(name, create=True, dry_run=dry_run, enable_globals=True):
        create_subdirectory('src')
        
        with File('README.md', dry_run=dry_run, enable_globals=True):
            add_heading(name)

# Test first
setup_project('testproject', dry_run=True)
# Then execute
setup_project('testproject', dry_run=False)
```

### 3. Combine with Shell Operations

```python
from hands_scaphoid import Directory, File, ShellContext

with ShellContext() as shell:
    allow("git")
    allow("python")
    
    with Directory('newproject', enable_globals=True):
        run("git init")
        
        with File('.gitignore', enable_globals=True):
            write_line('__pycache__/')
            write_line('*.pyc')
            write_line('.env')
        
        run("git add .")
        run("git commit -m 'Initial commit'")
```

### 4. Handle Errors Gracefully

```python
try:
    with Directory('sensitive_dir', enable_globals=True):
        create_subdirectory('new_folder')
        
        with File('important.txt', enable_globals=True):
            write_line('Important data')
            
except PermissionError as e:
    print(f"Permission denied: {e}")
except FileNotFoundError as e:
    print(f"Path not found: {e}")
```

## Integration with Existing Code

### Migrating from Standard Library

```python
# Old approach with pathlib
from pathlib import Path
import os

os.chdir('/tmp')
project_dir = Path('myproject')
project_dir.mkdir(exist_ok=True)
os.chdir(project_dir)

readme = project_dir / 'README.md'
readme.write_text('# My Project\n')

# New approach with hierarchical contexts
with Directory('/tmp/myproject', create=True, enable_globals=True):
    with File('README.md', enable_globals=True):
        add_heading('My Project')
```

### Working with Existing Functions

```python
def process_files_old_way(directory: str):
    """Old way: manual path management."""
    old_cwd = os.getcwd()
    try:
        os.chdir(directory)
        # Process files...
    finally:
        os.chdir(old_cwd)

def process_files_new_way(directory: str):
    """New way: automatic context management."""
    with Directory(directory, enable_globals=True):
        # Process files...
        for file in list_files('txt'):
            with File(file, enable_globals=True):
                content = read_content()
                # Process content...
```

## Troubleshooting

### Common Issues

**Issue**: Global functions not available
```python
# ❌ Wrong: forgot enable_globals
with Directory('mydir'):
    list_contents()  # NameError: name 'list_contents' is not defined

# ✅ Correct: enable global functions
with Directory('mydir', enable_globals=True):
    list_contents()  # Works!
```

**Issue**: Functions from wrong context
```python
with Directory('mydir', enable_globals=True):
    with File('myfile.txt', enable_globals=True):
        write_line('text')      # ✅ File method available
        list_contents()         # ❌ Directory method not available here
```

**Issue**: Nested path resolution
```python
# The path is resolved relative to parent context
with Directory('/home/user'):
    with Directory('documents'):  # This is /home/user/documents
        with File('notes.txt'):   # This is /home/user/documents/notes.txt
            pass
```

### Debugging Tips

1. **Use dry-run mode** to see what operations would be performed
2. **Check resolved paths** using the `resolve_path()` method
3. **Enable verbose logging** by importing and using the rich console
4. **Test with simple operations** before building complex hierarchies

## Performance Considerations

- **Context overhead**: Minimal - contexts are lightweight
- **Global function injection**: Fast - uses Python's built-in namespace
- **Path resolution**: Cached per context for efficiency
- **File handle management**: Automatic - no need to worry about leaks

## Thread Safety

All context managers are thread-safe:
- Each thread maintains its own context stack
- Global functions are isolated per thread
- No shared mutable state between threads

```python
import threading
from hands_scaphoid import Directory

def worker(thread_id: int):
    with Directory(f'thread_{thread_id}', enable_globals=True):
        create_subdirectory('work')
        list_contents()

# Multiple threads can safely use contexts
threads = []
for i in range(5):
    t = threading.Thread(target=worker, args=(i,))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
```

This concludes the user guide for hierarchical file system context managers. The combination of automatic resource management, global function access, and seamless integration with shell operations makes these tools powerful for file system automation tasks.