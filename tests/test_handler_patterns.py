#!/usr/bin/env python3
"""
Comprehensive test suite for Handler patterns.

This module provides complete test coverage for the new Handler patterns
including FileHandler, DirectoryHandler, ExecutableHandler, and their
concrete implementations.
---yaml
File:
    name: test_handler_patterns.py
    uuid: 2c3d4e5f-6789-0abc-def1-234567890abc
    date: 2025-09-28

Description:
    Complete test suite for all Handler pattern components

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

import pytest
import tempfile
import json
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.hands_scaphoid.commands.handler_patterns import (
    # Base classes
    FileHandler, DirectoryHandler, ExecutableHandler,
    
    # Concrete implementations
    TextFileHandler, JsonFileHandler,
    GitProjectHandler, PythonProjectHandler,
    PythonScriptHandler,
    
    # Registry classes
    HandlerRegistry,
    
    # Factory functions
    create_file_handler_registry, create_directory_handler_registry,
    create_executable_handler_registry,
    get_file_handler_registry, get_directory_handler_registry,
    get_executable_handler_registry
)


# =============================================================================
# Test Fixtures
# =============================================================================

@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_text_file(temp_dir):
    """Create sample text file."""
    file_path = temp_dir / "sample.txt"
    file_path.write_text("Hello, World!\nThis is a test file.\n", encoding='utf-8')
    return file_path


@pytest.fixture
def sample_json_file(temp_dir):
    """Create sample JSON file."""
    file_path = temp_dir / "sample.json"
    data = {
        "name": "test",
        "version": "1.0.0",
        "items": [1, 2, 3],
        "nested": {"key": "value"}
    }
    file_path.write_text(json.dumps(data, indent=2), encoding='utf-8')
    return file_path


@pytest.fixture
def invalid_json_file(temp_dir):
    """Create invalid JSON file."""
    file_path = temp_dir / "invalid.json"
    file_path.write_text('{"invalid": json syntax}', encoding='utf-8')
    return file_path


@pytest.fixture
def sample_python_script(temp_dir):
    """Create sample Python script."""
    script_path = temp_dir / "test_script.py"
    script_content = '''#!/usr/bin/env python3
"""Test script for executable handling."""
import sys
import os

def main():
    print(f"Python version: {sys.version_info.major}.{sys.version_info.minor}")
    print(f"Arguments: {sys.argv[1:]}")
    print(f"Working directory: {os.getcwd()}")
    return 0

if __name__ == "__main__":
    exit(main())
'''
    script_path.write_text(script_content, encoding='utf-8')
    return script_path


@pytest.fixture
def invalid_python_script(temp_dir):
    """Create invalid Python script."""
    script_path = temp_dir / "invalid.py"
    script_path.write_text('def invalid_syntax(\n    print("missing parenthesis")', encoding='utf-8')
    return script_path


@pytest.fixture
def git_project_dir(temp_dir):
    """Create mock Git project directory."""
    git_dir = temp_dir / ".git"
    git_dir.mkdir()
    (git_dir / "config").write_text("[core]\n    repositoryformatversion = 0")
    
    (temp_dir / "README.md").write_text("# Test Project")
    (temp_dir / ".gitignore").write_text("*.pyc\n__pycache__/")
    
    return temp_dir


@pytest.fixture
def python_project_dir(temp_dir):
    """Create mock Python project directory."""
    (temp_dir / "pyproject.toml").write_text("""
[build-system]
requires = ["setuptools>=45", "wheel"]
build-backend = "setuptools.build_meta"

[project]
name = "test-project"
version = "0.1.0"
""")
    
    src_dir = temp_dir / "src" / "test_project"
    src_dir.mkdir(parents=True)
    (src_dir / "__init__.py").write_text('"""Test project package."""\n__version__ = "0.1.0"')
    
    tests_dir = temp_dir / "tests"
    tests_dir.mkdir()
    (tests_dir / "__init__.py").touch()
    
    (temp_dir / "README.md").write_text("# Test Python Project")
    (temp_dir / "requirements.txt").write_text("pytest>=7.0.0\nrequests>=2.28.0")
    
    return temp_dir


# =============================================================================
# FileHandler Tests
# =============================================================================

class TestTextFileHandler:
    """Test TextFileHandler functionality."""
    
    def test_initialization(self):
        """Test TextFileHandler initialization."""
        handler = TextFileHandler()
        assert handler.encoding == 'utf-8'
        
        handler_ascii = TextFileHandler('ascii')
        assert handler_ascii.encoding == 'ascii'
    
    def test_read_write_text(self, temp_dir):
        """Test reading and writing text files."""
        handler = TextFileHandler()
        file_path = temp_dir / "test.txt"
        content = "Hello, World!\nLine 2"
        
        # Test write
        assert handler.write(file_path, content)
        assert file_path.exists()
        
        # Test read
        read_content = handler.read(file_path)
        assert read_content == content
    
    def test_validate_text_file(self, sample_text_file):
        """Test text file validation."""
        handler = TextFileHandler()
        assert handler.validate(sample_text_file)
    
    def test_validate_invalid_encoding(self, temp_dir):
        """Test validation with invalid encoding."""
        handler = TextFileHandler('ascii')
        file_path = temp_dir / "unicode.txt"
        file_path.write_bytes("Hello, 世界!".encode('utf-8'))
        
        # Should fail validation due to encoding mismatch
        assert not handler.validate(file_path)
    
    def test_get_metadata(self, sample_text_file):
        """Test metadata extraction."""
        handler = TextFileHandler()
        metadata = handler.get_metadata(sample_text_file)
        
        assert metadata['encoding'] == 'utf-8'
        assert metadata['line_count'] == 2
        assert metadata['char_count'] > 0
        assert metadata['word_count'] > 0
        assert not metadata['is_empty']
    
    def test_write_failure(self, temp_dir):
        """Test write failure handling."""
        handler = TextFileHandler()
        invalid_path = temp_dir / "nonexistent" / "file.txt"
        
        result = handler.write(invalid_path, "content")
        assert not result
    
    def test_open_context_manager(self, sample_text_file):
        """Test open method as context manager."""
        handler = TextFileHandler()
        
        with handler.open(sample_text_file, 'r') as f:
            content = f.read()
            assert "Hello, World!" in content


class TestJsonFileHandler:
    """Test JsonFileHandler functionality."""
    
    def test_read_valid_json(self, sample_json_file):
        """Test reading valid JSON file."""
        handler = JsonFileHandler()
        data = handler.read(sample_json_file)
        
        assert isinstance(data, dict)
        assert data['name'] == 'test'
        assert data['version'] == '1.0.0'
        assert len(data['items']) == 3
    
    def test_write_json(self, temp_dir):
        """Test writing JSON file."""
        handler = JsonFileHandler()
        file_path = temp_dir / "output.json"
        data = {"test": True, "count": 42}
        
        assert handler.write(file_path, data)
        
        # Verify written content
        with open(file_path, 'r') as f:
            written_data = json.load(f)
        assert written_data == data
    
    def test_write_with_formatting(self, temp_dir):
        """Test JSON writing with formatting options."""
        handler = JsonFileHandler()
        file_path = temp_dir / "formatted.json"
        data = {"nested": {"key": "value"}}
        
        assert handler.write(file_path, data, indent=4, sort_keys=True)
        
        content = file_path.read_text()
        assert "    " in content  # Check indentation
    
    def test_validate_valid_json(self, sample_json_file):
        """Test validation of valid JSON."""
        handler = JsonFileHandler()
        assert handler.validate(sample_json_file)
    
    def test_validate_invalid_json(self, invalid_json_file):
        """Test validation of invalid JSON."""
        handler = JsonFileHandler()
        assert not handler.validate(invalid_json_file)
    
    def test_get_metadata_dict(self, sample_json_file):
        """Test metadata for JSON object."""
        handler = JsonFileHandler()
        metadata = handler.get_metadata(sample_json_file)
        
        assert metadata['json_type'] == 'dict'
        assert metadata['key_count'] == 4
        assert metadata['array_length'] is None
        assert metadata['is_valid']
        assert metadata['structure_depth'] > 0
    
    def test_get_metadata_array(self, temp_dir):
        """Test metadata for JSON array."""
        handler = JsonFileHandler()
        file_path = temp_dir / "array.json"
        data = [1, 2, {"nested": "value"}]
        
        handler.write(file_path, data)
        metadata = handler.get_metadata(file_path)
        
        assert metadata['json_type'] == 'list'
        assert metadata['key_count'] is None
        assert metadata['array_length'] == 3
    
    def test_get_metadata_invalid(self, invalid_json_file):
        """Test metadata for invalid JSON."""
        handler = JsonFileHandler()
        metadata = handler.get_metadata(invalid_json_file)
        
        assert not metadata['is_valid']
        assert 'error' in metadata
    
    def test_json_depth_calculation(self):
        """Test JSON depth calculation."""
        handler = JsonFileHandler()
        
        shallow = {"key": "value"}
        assert handler._get_json_depth(shallow) == 0
        
        nested = {"level1": {"level2": {"level3": "value"}}}
        assert handler._get_json_depth(nested) == 3
        
        mixed = {"array": [{"nested": "value"}]}
        assert handler._get_json_depth(mixed) == 2


# =============================================================================
# DirectoryHandler Tests
# =============================================================================

class TestGitProjectHandler:
    """Test GitProjectHandler functionality."""
    
    def test_validate_git_project(self, git_project_dir):
        """Test validation of Git project."""
        handler = GitProjectHandler()
        assert handler.validate(git_project_dir)
    
    def test_validate_non_git_directory(self, temp_dir):
        """Test validation of non-Git directory."""
        handler = GitProjectHandler()
        assert not handler.validate(temp_dir)
    
    @patch('subprocess.run')
    def test_initialize_git_project(self, mock_run, temp_dir):
        """Test Git project initialization."""
        mock_run.return_value = Mock(returncode=0)
        
        handler = GitProjectHandler()
        assert handler.initialize(temp_dir)
        
        mock_run.assert_called_once_with(
            ['git', 'init', str(temp_dir)],
            capture_output=True, text=True, check=True
        )
    
    @patch('subprocess.run')
    def test_initialize_git_project_failure(self, mock_run, temp_dir):
        """Test Git project initialization failure."""
        mock_run.side_effect = subprocess.CalledProcessError(1, 'git')
        
        handler = GitProjectHandler()
        assert not handler.initialize(temp_dir)
    
    def test_get_structure_info(self, git_project_dir):
        """Test Git structure information."""
        handler = GitProjectHandler()
        info = handler.get_structure_info(git_project_dir)
        
        assert info['type'] == 'git_repository'
        assert info['has_git_dir']
        assert info['has_gitignore']
        assert info['has_readme']
    
    @patch('subprocess.run')
    def test_get_structure_info_with_git_commands(self, mock_run, git_project_dir):
        """Test structure info with Git command results."""
        # Mock git branch command
        mock_run.side_effect = [
            Mock(returncode=0, stdout='main\n'),  # git branch --show-current
            Mock(returncode=0, stdout='origin\thttps://github.com/user/repo.git (fetch)\n')  # git remote -v
        ]
        
        handler = GitProjectHandler()
        info = handler.get_structure_info(git_project_dir)
        
        assert info['current_branch'] == 'main'
        assert info['has_remote']
    
    @patch('subprocess.run')
    def test_list_contents_with_git_ls_files(self, mock_run, git_project_dir):
        """Test listing contents using git ls-files."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='README.md\n.gitignore\nsrc/main.py\n'
        )
        
        handler = GitProjectHandler()
        contents = handler.list_contents(git_project_dir)
        
        assert len(contents) == 3
        assert any(path.name == 'README.md' for path in contents)
    
    def test_list_contents_fallback(self, git_project_dir):
        """Test fallback to regular directory listing."""
        handler = GitProjectHandler()
        
        with patch('subprocess.run', side_effect=Exception("Git not available")):
            contents = handler.list_contents(git_project_dir)
            assert len(contents) >= 2  # At least .git and README.md


class TestPythonProjectHandler:
    """Test PythonProjectHandler functionality."""
    
    def test_validate_python_project(self, python_project_dir):
        """Test validation of Python project."""
        handler = PythonProjectHandler()
        assert handler.validate(python_project_dir)
    
    def test_validate_non_python_directory(self, temp_dir):
        """Test validation of non-Python directory."""
        handler = PythonProjectHandler()
        assert not handler.validate(temp_dir)
    
    def test_validate_with_setup_py(self, temp_dir):
        """Test validation with setup.py."""
        (temp_dir / "setup.py").write_text("from setuptools import setup\nsetup()")
        
        handler = PythonProjectHandler()
        assert handler.validate(temp_dir)
    
    def test_initialize_python_project(self, temp_dir):
        """Test Python project initialization."""
        handler = PythonProjectHandler()
        project_name = "my_project"
        
        assert handler.initialize(temp_dir, project_name=project_name)
        
        # Check created structure
        assert (temp_dir / "src" / project_name / "__init__.py").exists()
        assert (temp_dir / "tests").is_dir()
        assert (temp_dir / "docs").is_dir()
        assert (temp_dir / "README.md").exists()
        assert (temp_dir / "requirements.txt").exists()
    
    def test_initialize_python_project_default_name(self, temp_dir):
        """Test initialization with default project name."""
        handler = PythonProjectHandler()
        
        assert handler.initialize(temp_dir)
        
        expected_name = temp_dir.name
        assert (temp_dir / "src" / expected_name / "__init__.py").exists()
    
    def test_get_structure_info(self, python_project_dir):
        """Test Python project structure information."""
        handler = PythonProjectHandler()
        info = handler.get_structure_info(python_project_dir)
        
        assert info['type'] == 'python_project'
        assert info['has_pyproject_toml']
        assert info['has_requirements']
        assert info['has_src_layout']
        assert info['has_tests']
        assert info['python_files_count'] >= 1
        assert len(info['package_directories']) >= 1
    
    def test_list_contents(self, python_project_dir):
        """Test listing Python files."""
        handler = PythonProjectHandler()
        contents = handler.list_contents(python_project_dir, "*.py")
        
        assert len(contents) >= 1
        assert all(path.suffix == '.py' for path in contents)


# =============================================================================
# ExecutableHandler Tests
# =============================================================================

class TestPythonScriptHandler:
    """Test PythonScriptHandler functionality."""
    
    def test_validate_valid_script(self, sample_python_script):
        """Test validation of valid Python script."""
        handler = PythonScriptHandler()
        assert handler.validate(sample_python_script)
    
    def test_validate_invalid_script(self, invalid_python_script):
        """Test validation of invalid Python script."""
        handler = PythonScriptHandler()
        assert not handler.validate(invalid_python_script)
    
    @patch('subprocess.run')
    def test_execute_success(self, mock_run, sample_python_script):
        """Test successful script execution."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout='Hello from Python!\n',
            stderr=''
        )
        
        handler = PythonScriptHandler()
        result = handler.execute(sample_python_script, ['arg1', 'arg2'])
        
        assert result['success']
        assert result['returncode'] == 0
        assert 'Hello from Python!' in result['stdout']
        
        mock_run.assert_called_once_with(
            ['python', str(sample_python_script), 'arg1', 'arg2'],
            capture_output=True, text=True
        )
    
    @patch('subprocess.run')
    def test_execute_failure(self, mock_run, sample_python_script):
        """Test script execution failure."""
        mock_run.return_value = Mock(
            returncode=1,
            stdout='',
            stderr='Error: Something went wrong\n'
        )
        
        handler = PythonScriptHandler()
        result = handler.execute(sample_python_script)
        
        assert not result['success']
        assert result['returncode'] == 1
        assert 'Error:' in result['stderr']
    
    @patch('subprocess.run')
    def test_execute_exception(self, mock_run, sample_python_script):
        """Test script execution with exception."""
        mock_run.side_effect = Exception("Command failed")
        
        handler = PythonScriptHandler()
        result = handler.execute(sample_python_script)
        
        assert not result['success']
        assert result['returncode'] == -1
        assert 'Command failed' in result['stderr']
    
    def test_get_info(self, sample_python_script):
        """Test getting script information."""
        handler = PythonScriptHandler()
        info = handler.get_info(sample_python_script)
        
        assert info['type'] == 'python_script'
        assert info['is_valid']
        assert info['has_shebang']
        assert 'sys' in info['imports']
        assert 'os' in info['imports']
    
    def test_get_info_no_shebang(self, temp_dir):
        """Test script info without shebang."""
        script_path = temp_dir / "no_shebang.py"
        script_path.write_text('print("Hello")')
        
        handler = PythonScriptHandler()
        info = handler.get_info(script_path)
        
        assert not info['has_shebang']
    
    def test_get_info_with_parse_error(self, invalid_python_script):
        """Test script info with parse error."""
        handler = PythonScriptHandler()
        info = handler.get_info(invalid_python_script)
        
        assert not info['is_valid']
        assert 'parse_error' in info
    
    def test_test_executable(self, sample_python_script):
        """Test executable testing."""
        handler = PythonScriptHandler()
        
        with patch.object(handler, 'execute') as mock_execute:
            mock_execute.return_value = {'returncode': 0}
            assert handler.test(sample_python_script)
            
            mock_execute.return_value = {'returncode': 1}
            assert not handler.test(sample_python_script)


# =============================================================================
# Registry Tests
# =============================================================================

class TestHandlerRegistry:
    """Test HandlerRegistry functionality."""
    
    def test_registry_creation(self):
        """Test registry creation."""
        registry = HandlerRegistry(FileHandler)
        assert registry.handler_type == FileHandler
        assert len(registry.handlers) == 0
        assert registry.default_handler is None
    
    def test_register_handler(self):
        """Test handler registration."""
        registry = HandlerRegistry(FileHandler)
        handler = TextFileHandler()
        
        registry.register('text', handler)
        assert registry.get('text') == handler
        assert 'text' in registry.list_handlers()
    
    def test_register_default_handler(self):
        """Test default handler registration."""
        registry = HandlerRegistry(FileHandler)
        handler = TextFileHandler()
        
        registry.register('text', handler, is_default=True)
        assert registry.get_default() == handler
    
    def test_register_wrong_type(self):
        """Test registering wrong handler type."""
        registry = HandlerRegistry(FileHandler)
        
        with pytest.raises(TypeError):
            registry.register('wrong', "not a file handler")
    
    def test_get_nonexistent_handler(self):
        """Test getting non-existent handler."""
        registry = HandlerRegistry(FileHandler)
        assert registry.get('nonexistent') is None


class TestRegistryFactories:
    """Test registry factory functions."""
    
    def test_create_file_handler_registry(self):
        """Test file handler registry creation."""
        registry = create_file_handler_registry()
        
        assert isinstance(registry, HandlerRegistry)
        assert registry.handler_type == FileHandler
        assert 'text' in registry.list_handlers()
        assert 'json' in registry.list_handlers()
        assert registry.get_default() is not None
    
    def test_create_directory_handler_registry(self):
        """Test directory handler registry creation."""
        registry = create_directory_handler_registry()
        
        assert isinstance(registry, HandlerRegistry)
        assert registry.handler_type == DirectoryHandler
        assert 'git' in registry.list_handlers()
        assert 'python' in registry.list_handlers()
    
    def test_create_executable_handler_registry(self):
        """Test executable handler registry creation."""
        registry = create_executable_handler_registry()
        
        assert isinstance(registry, HandlerRegistry)
        assert registry.handler_type == ExecutableHandler
        assert 'python' in registry.list_handlers()
        assert registry.get_default() is not None
    
    def test_global_registry_singleton(self):
        """Test global registry singleton behavior."""
        # First call
        registry1 = get_file_handler_registry()
        
        # Second call should return same instance
        registry2 = get_file_handler_registry()
        
        assert registry1 is registry2
    
    def test_all_global_registries(self):
        """Test all global registries are accessible."""
        file_registry = get_file_handler_registry()
        dir_registry = get_directory_handler_registry()
        exe_registry = get_executable_handler_registry()
        
        assert isinstance(file_registry, HandlerRegistry)
        assert isinstance(dir_registry, HandlerRegistry)
        assert isinstance(exe_registry, HandlerRegistry)
        
        assert file_registry.handler_type == FileHandler
        assert dir_registry.handler_type == DirectoryHandler
        assert exe_registry.handler_type == ExecutableHandler


# =============================================================================
# Integration Tests
# =============================================================================

class TestHandlerIntegration:
    """Test handler integration scenarios."""
    
    def test_file_handler_auto_detection(self, temp_dir):
        """Test automatic file handler detection."""
        # Create different file types
        text_file = temp_dir / "test.txt"
        json_file = temp_dir / "test.json"
        
        text_file.write_text("Hello, World!")
        json_file.write_text('{"key": "value"}')
        
        registry = get_file_handler_registry()
        
        # Test text file detection
        text_handler = registry.get('text')
        assert text_handler.validate(text_file)
        
        # Test JSON file detection
        json_handler = registry.get('json')
        assert json_handler.validate(json_file)
        assert json_handler.validate(text_file) == False  # Text file should not validate as JSON
    
    def test_directory_handler_multiple_matches(self, temp_dir):
        """Test directory with multiple applicable handlers."""
        # Create a directory that's both Git and Python project
        git_dir = temp_dir / ".git"
        git_dir.mkdir()
        (temp_dir / "pyproject.toml").write_text("[project]\nname = 'test'")
        
        registry = get_directory_handler_registry()
        
        git_handler = registry.get('git')
        python_handler = registry.get('python')
        
        assert git_handler.validate(temp_dir)
        assert python_handler.validate(temp_dir)
    
    def test_executable_handler_shebang_detection(self, temp_dir):
        """Test executable handler detection via shebang."""
        script_path = temp_dir / "script.py"
        script_path.write_text('#!/usr/bin/env python3\nprint("Hello")')
        
        handler = PythonScriptHandler()
        assert handler.validate(script_path)
        
        info = handler.get_info(script_path)
        assert info['has_shebang']


# =============================================================================
# Performance Tests
# =============================================================================

class TestHandlerPerformance:
    """Test handler performance characteristics."""
    
    def test_registry_lookup_performance(self):
        """Test registry lookup performance."""
        registry = create_file_handler_registry()
        
        # Multiple lookups should be fast
        import time
        start_time = time.time()
        
        for _ in range(1000):
            handler = registry.get('text')
            assert handler is not None
        
        elapsed = time.time() - start_time
        assert elapsed < 0.1  # Should complete in under 100ms
    
    def test_validation_performance(self, temp_dir):
        """Test handler validation performance."""
        # Create multiple files
        files = []
        for i in range(100):
            file_path = temp_dir / f"file_{i}.txt"
            file_path.write_text(f"Content {i}")
            files.append(file_path)
        
        handler = TextFileHandler()
        
        import time
        start_time = time.time()
        
        for file_path in files:
            assert handler.validate(file_path)
        
        elapsed = time.time() - start_time
        assert elapsed < 1.0  # Should validate 100 files in under 1 second


# =============================================================================
# Error Handling Tests
# =============================================================================

class TestHandlerErrorHandling:
    """Test handler error handling scenarios."""
    
    def test_file_handler_missing_file(self, temp_dir):
        """Test file handler with missing file."""
        handler = TextFileHandler()
        missing_file = temp_dir / "missing.txt"
        
        assert not handler.validate(missing_file)
        
        with pytest.raises(FileNotFoundError):
            handler.read(missing_file)
    
    def test_directory_handler_missing_directory(self, temp_dir):
        """Test directory handler with missing directory."""
        handler = GitProjectHandler()
        missing_dir = temp_dir / "missing"
        
        assert not handler.validate(missing_dir)
    
    def test_executable_handler_permission_error(self, temp_dir):
        """Test executable handler with permission issues."""
        handler = PythonScriptHandler()
        script_path = temp_dir / "restricted.py"
        script_path.write_text('print("Hello")')
        
        # Make file non-readable
        script_path.chmod(0o000)
        
        try:
            assert not handler.validate(script_path)
        finally:
            # Restore permissions for cleanup
            script_path.chmod(0o644)


if __name__ == "__main__":
    """Run tests with pytest."""
    pytest.main([__file__, "-v"])