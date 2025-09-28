---
applyTo: "**/test_*.py"
---
# Testing standards for hands_scaphoid

## Test File Structure
```python
#!/usr/bin/env python3
"""
Test module description.

File:
    name: {{file-name}}.py
    uuid: {{generated-uuid}}
    date: {{modification-date, YYYY-MM-DD}}

Description:
    Comprehensive tests for ModuleName functionality

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
Abbreviations:
- {{abbreviation}}[{{context}}]:: {{description}}
- DUT[testing]: Device Under Test (the main object/function being tested)
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.hands_scaphoid.module import ClassName
```

## Fixture Patterns
- Use `temp_dir` fixture for file system tests:
```python
@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)
```

- Create sample files for testing:
```python
@pytest.fixture
def sample_json_file(temp_dir):
    """Create sample JSON file."""
    file_path = temp_dir / "sample.json"
    data = {"test": "data"}
    file_path.write_text(json.dumps(data))
    return file_path
```

## Test Organization
- Group tests by functionality using classes:
```python
class TestFileHandler:
    """Test FileHandler functionality."""
    
    def test_validation(self, sample_file):
        """Test file validation."""
        handler = TextFileHandler()
        assert handler.validate(sample_file)
```

## Mocking Patterns
- Mock external dependencies (subprocess, file operations):
```python
@patch('subprocess.run')
def test_execute_command(self, mock_run):
    mock_run.return_value = Mock(returncode=0, stdout='output')
    # ... test logic
```

## Handler Testing
- Test validation, operations, and error handling
- Include performance tests for registry lookups
- Test registry initialization and factory functions
- Mock handler dependencies appropriately

## Test Coverage
- Aim for comprehensive coverage of happy paths and error cases
- Always test for all exceptions of a function  
- Test both direct operations and context manager usage
- Include integration tests for handler patterns
- Test backward compatibility with existing APIs