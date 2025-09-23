"""
Test configuration and fixtures for hands-trapezium package.
"""

import os
import tempfile
from pathlib import Path

import pytest

from hands_scaphoid import ShellExecutable, ShellContext


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def temp_env_file(temp_dir):
    """Create a temporary environment file for testing."""
    env_file = temp_dir / ".env"
    env_content = """
# Test environment file
TEST_VAR=test_value
ANOTHER_VAR=another_value
PATH=/usr/bin:/bin
"""
    env_file.write_text(env_content)
    return str(env_file)


@pytest.fixture
def shell_with_temp_dir(temp_dir):
    """Create a Shell instance with a temporary directory."""
    return ShellExecutable(cwd=str(temp_dir))


@pytest.fixture
def shell_with_env(temp_dir, temp_env_file):
    """Create a Shell instance with custom environment."""
    return ShellExecutable(cwd=str(temp_dir), env_file=temp_env_file)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    return {"TEST_VAR": "test_value", "PATH": "/usr/bin:/bin", "HOME": "/home/test"}
