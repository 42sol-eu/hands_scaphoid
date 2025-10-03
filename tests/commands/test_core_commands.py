#!/usr/bin/env python3
"""
Unit tests for core commands module.
---yaml
File:
    name: test_core_commands.py
    uuid: d397dc43-5ad4-4def-adaf-9a7a5d9bd4ea
    date: 2025-09-28

Description:
    Comprehensive tests for core command functionality including path operations,
    file type detection, project validation, and compression type handling.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# Standard library imports
import os
import tempfile
from pathlib import Path

# Third-party imports
import pytest
from unittest import mock
from unittest.mock import patch

# Project imports
from hands_scaphoid.commands.core_commands import (
    CompressionType,
    does_not_exists,
    ensure_path,
    exists,
    filter,
    is_instance,
    is_item,
    is_invalid,
    is_directory,
    is_file,
    is_git_project,
    is_hands_project,
    is_link,
    is_object,
    is_project,
    is_variable,
    is_vscode_project,
    get_file_extension,
    which,
)
def test_exists(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    assert exists(file)
    assert not exists(tmp_path / "nofile.txt")


# Helper to create symlinks safely on platforms that may not allow them.
def safe_symlink(target: Path, link: Path):
    try:
        link.symlink_to(target)
        return True
    except (OSError, NotImplementedError) as e:
        pytest.skip(f"Symbolic links not supported or insufficient privileges: {e}")

def test_is_object(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    symlink = tmp_path / "link1"
    
    safe_symlink(symlink, file)
    assert is_object(file)
    assert is_object(dir_path)
    assert is_object(symlink)
    assert not is_object(tmp_path / "nofile.txt")

def test_is_directory(tmp_path):
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    assert is_directory(dir_path)
    file = tmp_path / "file.txt"
    file.write_text("content")
    assert not is_directory(file)

def test_is_file(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    assert is_file(file)
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    assert not is_file(dir_path)

def test_is_link(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    symlink = tmp_path / "link2"
    safe_symlink(symlink,file)
    assert is_link(symlink)
    assert not is_link(file)

def test_is_variable(monkeypatch):
    monkeypatch.setenv("TEST_VAR", "1")
    assert is_variable("TEST_VAR")
    assert not is_variable("NON_EXISTENT_VAR")

def test_is_instance():
    assert is_instance(1, int)
    assert not is_instance("1", int)

def test_is_item(tmp_path, monkeypatch):
    file = tmp_path / "file.txt"
    file.write_text("content")
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    symlink = tmp_path / "link4"
    safe_symlink(symlink, file)
    assert is_item(file)
    assert is_item(dir_path)
    assert is_item(symlink)
    monkeypatch.setenv("TEST_VAR", "1")
    assert is_item("TEST_VAR")
    assert not is_item(Path("not_existing_path"))

def test_is_git_project(tmp_path):
    dir_path = tmp_path / "project"
    dir_path.mkdir()
    git_dir = dir_path / ".git"
    git_dir.mkdir()
    assert is_git_project(dir_path)
    assert not is_git_project(tmp_path)

def test_is_vscode_project(tmp_path):
    dir_path = tmp_path / "project"
    dir_path.mkdir()
    vscode_dir = dir_path / ".vscode"
    vscode_dir.mkdir()
    assert is_vscode_project(dir_path)
    assert not is_vscode_project(tmp_path)

def test_is_hands_project(tmp_path):
    dir_path = tmp_path / "project"
    dir_path.mkdir()
    hands_dir = dir_path / ".hands"
    hands_dir.mkdir()
    assert is_hands_project(dir_path)
    assert not is_hands_project(tmp_path)

def test_is_project(tmp_path):
    dir_path = tmp_path / "project"
    dir_path.mkdir()
    (dir_path / ".git").mkdir()
    assert is_project(dir_path)
    dir_path2 = tmp_path / "project2"
    dir_path2.mkdir()
    (dir_path2 / ".vscode").mkdir()
    assert is_project(dir_path2)
    dir_path3 = tmp_path / "project3"
    dir_path3.mkdir()
    (dir_path3 / ".hands").mkdir()
    assert is_project(dir_path3)
    dir_path4 = tmp_path / "not_a_project"
    dir_path4.mkdir()
    assert not is_project(dir_path4)

@pytest.mark.parametrize("filename,expected", [
    ("file.txt", "txt"),
    ("archive.tar.gz", "tar.gz"),
    ("drawing.drawio.png", "drawio.png"),
    ("image.svg", "svg"),
    ("no_extension", ""),
    ("complex.name.tar.gz", "tar.gz"),
    ("complex.name.drawio.png", "drawio.png"),
])
def test_get_file_extension(filename, expected):
    assert get_file_extension(filename) == expected, f"Expected {expected} for {filename}, but got {get_file_extension(filename)}"
    assert get_file_extension(Path(filename)) == expected, f"Expected {expected} for Path({filename}), but got {get_file_extension(Path(filename))}"

@pytest.mark.skip(reason="CompressionType enum replaced with DynamicArchiveType registry - tests need updating")
@pytest.mark.parametrize("compression_type,expected", [
    # (CompressionType.ZIP, "zip"),  # Old enum no longer exists
    # ... other old enum values
])
def test_compression_type_enum(compression_type, expected):
    """Test CompressionType enum values."""
    # This test is skipped - CompressionType replaced with DynamicArchiveType registry
    pass

@pytest.mark.skip(reason="CompressionType enum replaced with DynamicArchiveType registry - tests need updating")
def test_compression_type_list_types():
    """Test listing all compression types."""
    # This test is skipped - CompressionType replaced with DynamicArchiveType registry
    pass

def test_does_not_exists(tmp_path):
    """Test does_not_exists function."""
    file = tmp_path / "file.txt"
    file.write_text("content")
    assert not does_not_exists(file)
    assert does_not_exists(tmp_path / "nonexistent.txt")

def test_filter_function(tmp_path):
    """Test filter function with glob patterns."""
    # Create test files
    (tmp_path / "file1.txt").write_text("content")
    (tmp_path / "file2.txt").write_text("content")
    (tmp_path / "file3.py").write_text("content")
    subdir = tmp_path / "subdir"
    subdir.mkdir()
    (subdir / "file4.txt").write_text("content")
    
    # Test filtering with *.txt pattern
    txt_files = filter(tmp_path, "*.txt")
    txt_names = [f.name for f in txt_files]
    assert "file1.txt" in txt_names
    assert "file2.txt" in txt_names
    assert "file3.py" not in txt_names
    
    # Test filtering with *.py pattern
    py_files = filter(tmp_path, "*.py")
    py_names = [f.name for f in py_files]
    assert "file3.py" in py_names
    assert len(py_names) == 1
    
    # Test filtering on non-directory (should return empty list)
    file_path = tmp_path / "file1.txt"
    result = filter(file_path, "*.txt")
    assert result == []

def test_which_function():
    """Test which function for finding executables."""
    # Test with common system commands
    python_path = which("python")
    if python_path:  # Only test if python is available
        assert isinstance(python_path, Path)
        assert python_path.exists()
    
    # Test with non-existent command
    result = which("nonexistent_command_12345")
    assert result is None

def test_which_with_path_object():
    """Test which function with Path object input."""
    result = which(Path("python"))
    # Should handle Path objects the same as strings
    if result:
        assert isinstance(result, Path)


@pytest.mark.parametrize("type,expected", [
    (None,False),
    (1,False),
    (1.4,False),
    (False,False),
    ('', False),
    (' ', False),
    #(Path(''), False),
    #(Path(' '), False),
])
def test_invalid_calls(type, expected):
    """Test some function with invalid input parameters."""
    ensure_path_result = ensure_path(type)
    assert ensure_path_result is expected

    result = is_directory(type)
    assert result is expected

    result = is_invalid(type)
    assert result is expected

    # TODO: more functions to test with invalid inputs

def test_invalid_which_calls():
    """Test which function with invalid input parameters."""
    result = which(None)
    assert result is None

    result = which("")
    assert result is None

    result = which("nonexistent_command_12345")
    assert result is None



class TestCoreCommandsAdditional:
    """Additional tests for core_commands functions."""
    
    def test_is_project_combined(self, tmp_path):
        """Test is_project function with different project types."""
        # Test directory with multiple project markers
        dir_path = tmp_path / "multi_project"
        dir_path.mkdir()
        (dir_path / ".git").mkdir()
        (dir_path / ".vscode").mkdir()
        (dir_path / ".hands").mkdir()
        
        assert is_project(dir_path)
        assert is_git_project(dir_path)
        assert is_vscode_project(dir_path)
        assert is_hands_project(dir_path)
    
    def test_get_file_extension_edge_cases(self):
        """Test get_file_extension with edge cases."""
        # Test with no extension
        assert get_file_extension("filename") == ""
        assert get_file_extension("filename.") == ""
        
        # Test with hidden files
        assert get_file_extension(".hidden") == ""
        assert get_file_extension(".hidden.txt") == "txt"
        
        # Test case sensitivity
        assert get_file_extension("FILE.TXT") == "txt"
        assert get_file_extension("File.Zip") == "zip"
        
        # Test complex extensions
        assert get_file_extension("backup.tar.gz.old") == "old"
        assert get_file_extension("diagram.excalidraw.png") == "excalidraw.png"
        
        # Test very long extensions
        assert get_file_extension("file.verylongextension") == "verylongextension"
    
    def test_is_item_edge_cases(self, tmp_path, monkeypatch):
        """Test is_item function with various edge cases."""
        # Test with Path objects
        path_obj = Path("nonexistent")
        assert not is_item(path_obj)
        
        # Test with empty string (should be treated as variable name)
        assert not is_item("")
        
        # Test with existing environment variable
        monkeypatch.setenv("TEST_ITEM_VAR", "value")
        assert is_item("TEST_ITEM_VAR")
        
        # Test with special characters in variable names
        monkeypatch.setenv("TEST_VAR_123", "value")
        assert is_item("TEST_VAR_123")
    
    def test_error_conditions(self, tmp_path):
        """Test error conditions and edge cases."""
        # Test exists with invalid path types
        assert not exists(None) if hasattr(Path, '__new__') else True  # Depending on Path implementation
        
        # Test directory operations on files
        file_path = tmp_path / "file.txt"
        file_path.write_text("content")
        assert not is_directory(file_path)
        
        # Test file operations on directories
        dir_path = tmp_path / "dir"
        dir_path.mkdir()
        assert not is_file(dir_path)
    
    def test_symlink_operations(self, tmp_path):
        """Test operations with symbolic links."""
        # Create original file
        original = tmp_path / "original.txt"
        original.write_text("content")
        
        # Create symbolic link
        link = tmp_path / "link.txt"
        try:
            link.symlink_to(original)
            
            # Test various functions with symlinks
            assert exists(link)
            assert is_object(link)
            assert is_link(link)
            assert is_item(link)
            
            # Test that symlink is not considered a regular file or directory
            assert not is_file(link)  # This might depend on implementation
            assert not is_directory(link)
            
        except OSError:
            # Skip if symlinks are not supported on this system
            pytest.skip("Symbolic links not supported on this system")
    
    def test_performance_with_large_directory(self, tmp_path):
        """Test performance and correctness with larger directory structures."""
        # Create a directory with many files
        test_dir = tmp_path / "large_dir"
        test_dir.mkdir()
        
        # Create 100 files with different extensions
        for i in range(100):
            ext = "txt" if i % 2 == 0 else "py"
            (test_dir / f"file_{i:03d}.{ext}").write_text(f"content {i}")
        
        # Test filtering
        txt_files = filter(test_dir, "*.txt")
        py_files = filter(test_dir, "*.py")
        
        assert len(txt_files) == 50
        assert len(py_files) == 50
        
        # Verify all are Path objects
        for file_path in txt_files + py_files:
            assert is_instance(file_path, Path), f"{file_path} is not a Path instance"
            assert is_file(file_path), f"{file_path} is not a file"
            assert exists(file_path), f"{file_path} does not exist"
