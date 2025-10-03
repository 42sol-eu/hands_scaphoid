"""
Test configuration and fixtures for DNA CLI tests.

This file provides pytest configuration and shared fixtures
for testing the DNA CLI tool and its templates.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Generator
from unittest.mock import patch

# Test constants
TEST_PROJECT_NAME = "test_project"
TEST_AUTHOR = "Test Author <test@example.com>"
TEST_DESCRIPTION = "A test project"


@pytest.fixture
def temp_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for tests."""
    temp_path = Path(tempfile.mkdtemp())
    try:
        yield temp_path
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture  
def dna_commands_dir() -> Path:
    """Get the path to the DNA commands directory."""
    return Path(__file__).parent.parent / "commands"


@pytest.fixture
def templates_dir() -> Path:
    """Get the path to the templates directory."""
    return Path(__file__).parent.parent / "commands" / "_templates"


@pytest.fixture
def mock_console():
    """Mock Rich console for testing."""
    with patch('rich.console.Console') as mock:
        yield mock


@pytest.fixture
def sample_template_data():
    """Sample data for template testing."""
    return {
        'class_name': 'TestClass',
        'description': 'A test class',
        'filename': 'TestClass',
        'author': TEST_AUTHOR,
        'project_name': TEST_PROJECT_NAME,
        'current_date': '2025-10-03'
    }


@pytest.fixture
def mock_copier():
    """Mock copier.run_copy function."""
    with patch('copier.run_copy') as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def dna_cli_runner():
    """Get a CLI runner for DNA commands."""
    from click.testing import CliRunner
    return CliRunner()


@pytest.fixture
def sample_python_file(temp_dir) -> Path:
    """Create a sample Python file for testing."""
    file_path = temp_dir / "sample.py"
    content = '''#!/usr/bin/env python3
"""Sample Python file for testing."""

class SampleClass:
    """A sample class."""
    
    def __init__(self, name: str):
        self.name = name
    
    def greet(self) -> str:
        return f"Hello, {self.name}!"

def sample_function():
    """A sample function."""
    return "Hello, World!"

if __name__ == "__main__":
    obj = SampleClass("Test")
    print(obj.greet())
'''
    file_path.write_text(content)
    return file_path


@pytest.fixture
def sample_directory(temp_dir) -> Path:
    """Create a sample directory structure for testing."""
    sample_dir = temp_dir / "sample_project"
    sample_dir.mkdir()
    
    # Create some Python files
    (sample_dir / "__init__.py").write_text("")
    (sample_dir / "main.py").write_text("print('Hello, World!')")
    
    # Create subdirectory
    sub_dir = sample_dir / "utils"
    sub_dir.mkdir()
    (sub_dir / "__init__.py").write_text("")
    (sub_dir / "helpers.py").write_text("def helper(): pass")
    
    return sample_dir


# Test markers
pytest_plugins = []

# Configure pytest markers
def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "template: marks tests related to template generation"
    )
    config.addinivalue_line(
        "markers", "cli: marks tests related to CLI commands"
    )