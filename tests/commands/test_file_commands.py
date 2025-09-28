#!/usr/bin/env python3
"""
Unit tests for file commands module.
---yaml
File:
    name: test_file_commands.py
    uuid: ee446672-7c17-49f9-a5f3-492ad41a3bbb
    date: 2025-09-28

Description:
    Comprehensive tests for file command functionality including file reading,
    writing, manipulation, and validation operations.

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
from io import StringIO
from unittest import mock
from unittest.mock import patch, mock_open

# Third-party imports
import pytest

# Project imports
from hands_scaphoid.commands.file_commands import read
from hands_scaphoid.commands.core_commands import is_file
from hands_scaphoid.commands.directory_commands import ensure_path


class TestFileCommands:
    """Test class for file_commands module."""

    def test_read_entire_file(self, tmp_path):
        """Test reading entire file content."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        test_file.write_text(content)
        
        # Test reading entire file
        result = read(test_file)
        expected = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        assert result == expected

    def test_read_with_head(self, tmp_path):
        """Test reading first N lines of file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        test_file.write_text(content)
        
        # Test reading first 3 lines
        result = read(test_file, head=3)
        expected = "Line 1\nLine 2\nLine 3"
        assert result == expected

    def test_read_with_tail(self, tmp_path):
        """Test reading last N lines of file."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"
        test_file.write_text(content)
        
        # Test reading last 2 lines
        result = read(test_file, tail=2)
        expected = "Line 4\nLine 5"
        assert result == expected

    def test_read_with_head_and_tail(self, tmp_path):
        """Test reading file when both head and tail are specified (should return entire file)."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(content)
        
        # Test with both head and tail (should return entire content)
        result = read(test_file, head=2, tail=2)
        expected = "Line 1\n\nLine 2\n\nLine 3\n"
        assert result == expected

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading a file that doesn't exist."""
        nonexistent_file = tmp_path / "nonexistent.txt"
        
        result = read(nonexistent_file)
        assert result == ""

    def test_read_with_custom_line_separator(self, tmp_path):
        """Test reading file with custom line separator."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2\nLine 3"
        test_file.write_text(content)
        
        # Test with custom separator
        result = read(test_file, line_separator="|")
        expected = "Line 1|Line 2|Line 3"
        assert result == expected

    def test_read_with_print_enabled(self, tmp_path, capsys):
        """Test reading file with print output enabled."""
        # Create test file
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2"
        test_file.write_text(content)
        
        # Test with print enabled
        result = read(test_file, do_print=True)
        
        # Check that content was returned
        assert result == "Line 1\nLine 2"
        
        # Note: Cannot easily test rich console output in tests without complex mocking

    def test_read_empty_file(self, tmp_path):
        """Test reading an empty file."""
        test_file = tmp_path / "empty.txt"
        test_file.write_text("")
        
        result = read(test_file)
        assert result == ""

    def test_read_with_string_path(self, tmp_path):
        """Test reading file using string path instead of Path object."""
        test_file = tmp_path / "test.txt"
        content = "Test content"
        test_file.write_text(content)
        
        # Pass string path
        result = read(str(test_file))
        assert result == content

    def test_read_file_with_encoding_issues(self, tmp_path):
        """Test reading file when encoding issues might occur."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Test content with ünicödé")
        
        result = read(test_file)
        assert "ünicödé" in result

    @mock.patch('hands_scaphoid.commands.file_commands.Path.open')
    def test_read_file_exception_handling(self, mock_open_method, tmp_path):
        """Test exception handling during file reading."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        # Mock file open to raise an exception
        mock_open_method.side_effect = IOError("Mocked IO error")
        
        result = read(test_file)
        assert result == ""

    def test_read_head_larger_than_file(self, tmp_path):
        """Test reading more head lines than exist in file."""
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2"
        test_file.write_text(content)
        
        result = read(test_file, head=10)
        expected = "Line 1\nLine 2"
        assert result == expected

    def test_read_tail_larger_than_file(self, tmp_path):
        """Test reading more tail lines than exist in file."""
        test_file = tmp_path / "test.txt"
        content = "Line 1\nLine 2"
        test_file.write_text(content)
        
        result = read(test_file, tail=10)
        expected = "Line 1\nLine 2"
        assert result == expected


# TODO: Placeholder tests for future functions that need to be implemented

class TestFutureFileCommands:
    """Placeholder tests for file commands that are marked as TODO in the source."""
    
    def test_filter_placeholder(self):
        """Placeholder for filter function tests."""
        # TODO: Implement when filter(name: PathLike, pattern: str) -> list[str] is added
        pass
    
    def test_write_placeholder(self):
        """Placeholder for write function tests."""
        # TODO: Implement when write(name: PathLike, data: Any) -> bool is added
        pass
    
    def test_append_placeholder(self):
        """Placeholder for append function tests."""
        # TODO: Implement when append(name: PathLike, data: Any) is added
        pass
    
    def test_create_placeholder(self):
        """Placeholder for create function tests."""
        # TODO: Implement when create(name: PathLike, data: Any) -> bool is added
        pass
