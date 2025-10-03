"""
Test configuration for bones_validator.
"""

import pytest
import sys
from pathlib import Path

# Add src directory to path for testing
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Test fixtures and utilities
@pytest.fixture
def sample_values():
    """Common test values for validation."""
    return {
        'dotfiles': ['.bashrc', '.gitignore', '.env', '.hidden'],
        'absolute_paths': ['/usr/bin/python', '/etc/hosts', '/home/user/file.txt'],
        'relative_paths': ['./file.txt', '../parent/file', 'simple_file'],
        'invalid_chars': ['file<name>', 'path|with|pipes', 'file"quotes"'],
        'filenames': ['document.txt', 'image.png', 'script.py', 'README.md'],
        'empty_values': ['', None],
        'special_cases': ['  spaced  ', '...', '/', '\\', 'file.']
    }

@pytest.fixture
def mock_validation_context():
    """Mock evaluation context for testing."""
    from bones_validator.conditions.base_condition import EvaluationContext
    
    def create_context(value, **kwargs):
        return EvaluationContext(
            value=value,
            attributes=kwargs.get('attributes', {}),
            metadata=kwargs.get('metadata', {})
        )
    
    return create_context