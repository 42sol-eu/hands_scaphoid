#!/usr/bin/env python3
"""
Test configuration and fixtures for hands_scaphoid package.
---yaml
File:
    name: conftest.py
    uuid: 638e5d46-ac46-410b-8991-e8a23b7c57f3
    date: 2025-09-28

Description:
    Global pytest configuration and fixtures for testing hands_scaphoid
    functionality including temporary directories, mock environments,
    and shell instances.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import os
import tempfile
from pathlib import Path

#%% [ Third-party imports]
import pytest

#%% [Project imports]
from hands_scaphoid import ShellExecutable


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
    """Create a shell instance with a temporary directory."""
    return ShellExecutable(cwd=str(temp_dir))


@pytest.fixture
def shell_with_env(temp_dir, temp_env_file):
    """Create a shell instance with custom environment."""
    return ShellExecutable(cwd=str(temp_dir), env_file=temp_env_file)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    return {"TEST_VAR": "test_value", "PATH": "/usr/bin:/bin", "HOME": "/home/test"}
