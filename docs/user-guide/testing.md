# Testing

This guide covers the comprehensive test suite for Hands Scaphoid command modules, ensuring reliability and maintainability of the codebase.

## Test Structure

The test suite is organized into separate test modules that mirror the main command modules:

```
tests/commands/
├── test_file_commands.py      # Tests for file operations
├── test_archive_commands.py   # Tests for archive operations  
├── test_core_commands.py      # Tests for core utility functions
└── conftest.py               # Shared test fixtures
```

## Test Coverage Overview

### File Commands (`test_file_commands.py`)

The file commands test suite covers:

- **File Reading Operations**:
  - Reading entire file content
  - Reading with head/tail limits
  - Custom line separators
  - Error handling for non-existent files
  - Encoding handling

- **Placeholder Tests**: Ready for future file operations like:
  - `filter()` - Pattern-based file filtering
  - `write()` - File writing operations
  - `append()` - File appending operations
  - `create()` - File creation operations

Example test:
```python
def test_read_entire_file(self, tmp_path):
    """Test reading entire file content."""
    test_file = tmp_path / "test.txt"
    content = "Line 1\nLine 2\nLine 3"
    test_file.write_text(content)
    
    result = read(test_file)
    assert result == content
```

### Archive Commands (`test_archive_commands.py`)

Comprehensive testing for all archive formats:

- **Archive Detection**:
  - File extension validation
  - Support for `.zip`, `.tar`, `.7z`, `.rar`, `.tar.gz`, etc.

- **Archive Creation**:
  - ZIP archive creation and validation
  - TAR archives (with/without compression)
  - 7Z archives (mocked py7zr library)
  - RAR archives (via external command)

- **Archive Extraction**:
  - All supported formats
  - Target directory validation
  - Error handling for corrupted archives

- **Content Listing**:
  - Listing files in archives
  - Support for all archive formats
  - Error handling for invalid archives

Example test:
```python
def test_create_zip_archive(self, tmp_path):
    """Test creating ZIP archives."""
    source_dir = tmp_path / "source"
    source_dir.mkdir()
    (source_dir / "file1.txt").write_text("content1")
    
    archive_name = str(tmp_path / "test_archive")
    result = create_zip_archive(archive_name, source_dir)
    assert result is True
    
    # Verify archive was created
    archive_path = Path(f"{archive_name}.zip")
    assert archive_path.exists()
```

### Core Commands (`test_core_commands.py`)

Testing for core utility functions:

- **Path Operations**:
  - File/directory existence checking
  - Path type validation (file, directory, link, object)
  - Project type detection (git, vscode, hands projects)

- **Compression Types**:
  - Enum value validation
  - Type listing functionality

- **File Extensions**:
  - Simple extensions (`.txt`, `.py`)
  - Complex extensions (`.tar.gz`, `.drawio.png`)
  - Edge cases and special handling

- **System Integration**:
  - Executable discovery with `which()`
  - Environment variable checking
  - Filter operations with glob patterns

Example test:
```python
@pytest.mark.parametrize("filename,expected", [
    ("file.txt", "txt"),
    ("archive.tar.gz", "tar.gz"),
    ("drawing.drawio.png", "drawio.png"),
    ("no_extension", ""),
])
def test_get_file_extension(filename, expected):
    assert get_file_extension(filename) == expected
```

## Running Tests

### Basic Test Execution

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/commands/test_file_commands.py

# Run with verbose output
pytest -v

# Run with coverage
pytest --cov=hands_scaphoid
```

### Advanced Test Options

```bash
# Run tests matching pattern
pytest -k "test_archive"

# Run tests for specific functionality
pytest tests/commands/test_core_commands.py::test_get_file_extension

# Run with detailed output
pytest --tb=long -v
```

## Test Fixtures

The test suite uses pytest fixtures defined in `conftest.py`:

```python
@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def shell_with_temp_dir(temp_dir):
    """Create a Shell instance with a temporary directory."""
    return ShellExecutable(cwd=str(temp_dir))
```

## Mocking Strategy

For external dependencies, the tests use comprehensive mocking:

### Archive Libraries
```python
@patch('hands_scaphoid.commands.archive_commands.py7zr')
def test_create_7z_archive(self, mock_py7zr, tmp_path):
    """Test creating 7Z archives with mocked library."""
    mock_archive = MagicMock()
    mock_py7zr.SevenZipFile.return_value.__enter__.return_value = mock_archive
    # Test implementation...
```

### System Commands
```python
@patch('hands_scaphoid.commands.archive_commands.subprocess.run')
def test_create_rar_archive(self, mock_run, tmp_path):
    """Test RAR creation with mocked subprocess."""
    mock_run.return_value.returncode = 0
    # Test implementation...
```

## Test Categories

### Unit Tests
- Individual function testing
- Edge case handling
- Error condition validation
- Input validation

### Integration Tests
- File system operations
- Archive format handling
- Cross-module functionality

### Security Tests
- Path validation
- File access controls
- Command execution safety

## Best Practices

### Test Organization
- One test class per module
- Descriptive test method names
- Comprehensive docstrings
- Parametrized tests for variations

### Error Testing
```python
def test_read_nonexistent_file(self, tmp_path):
    """Test reading a file that doesn't exist."""
    nonexistent_file = tmp_path / "nonexistent.txt"
    result = read(nonexistent_file)
    assert result == ""
```

### Performance Testing
```python
def test_performance_with_large_directory(self, tmp_path):
    """Test performance with larger directory structures."""
    test_dir = tmp_path / "large_dir"
    test_dir.mkdir()
    
    # Create 100 test files
    for i in range(100):
        (test_dir / f"file_{i:03d}.txt").write_text(f"content {i}")
    
    # Test filtering performance
    txt_files = filter(test_dir, "*.txt")
    assert len(txt_files) == 100
```

### Platform Compatibility
```python
def test_symlink_operations(self, tmp_path):
    """Test operations with symbolic links."""
    try:
        link.symlink_to(original)
        # Test symlink operations...
    except OSError:
        pytest.skip("Symbolic links not supported on this system")
```

## Future Test Enhancements

### Planned Test Areas
- **File Commands**: Complete testing when remaining functions are implemented
- **Performance**: Load testing with large file sets
- **Concurrency**: Multi-threaded operation testing  
- **Platform**: Enhanced Windows/macOS specific testing

### Test Metrics Goals
- **Coverage**: >95% code coverage
- **Performance**: Sub-second test suite execution
- **Reliability**: Zero flaky tests
- **Documentation**: 100% test documentation coverage

## Continuous Integration

The test suite integrates with CI/CD pipelines:

```yaml
# GitHub Actions example
- name: Run Tests
  run: |
    pytest --cov=hands_scaphoid --cov-report=xml
    
- name: Upload Coverage
  uses: codecov/codecov-action@v1
  with:
    file: ./coverage.xml
```

This comprehensive test coverage ensures that Hands Scaphoid maintains high quality and reliability across all supported operations and platforms.