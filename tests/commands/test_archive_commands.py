"""
----
file:
    name:        test_archive_commands.py  
    uuid:        a8b9c7d6-1e2f-3456-7890-abcdef123456
description:     Test: archive commands
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid

----glossary
DUT::
    Device Under Test (or directly used to refer to the class or module being tested)
"""

import os
import tempfile
from pathlib import Path
import pytest
from unittest import mock
from unittest.mock import patch, MagicMock
import zipfile
import tarfile
import subprocess

from hands_scaphoid.commands.archive_commands import (
    is_archive_file,
    core_preconditions,
    create_7z_archive,
    create_rar_archive,
    create_tar_archive,
    create_zip_archive,
    core_extract_conditions,
    extract_7z_archive,
    extract_rar_archive,
    extract_tar_archive,
    extract_zip_archive,
    extract,
    list_contents,
)
from hands_scaphoid.commands.core_commands import CompressionType


class TestArchiveCommands:
    """Test class for archive_commands module."""

    def test_is_archive_file(self):
        """Test checking if a file is an archive based on extension."""
        # Test various archive extensions
        assert is_archive_file("test.zip")
        assert is_archive_file("test.tar")
        assert is_archive_file("test.tar.gz")
        assert is_archive_file("test.7z")
        assert is_archive_file("test.rar")
        assert is_archive_file("test.tar.bz2")
        assert is_archive_file("test.tar.xz")
        
        # Test non-archive files
        assert not is_archive_file("test.txt")
        assert not is_archive_file("test.py")
        assert not is_archive_file("README.md")
        
        # Test Path objects
        assert is_archive_file(Path("test.zip"))
        assert not is_archive_file(Path("test.txt"))

    def test_core_preconditions(self, tmp_path):
        """Test core preconditions for archive creation."""
        # Setup test directories
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        target_archive = tmp_path / "archive.zip"
        existing_archive = tmp_path / "existing.zip"
        existing_archive.write_text("existing")
        
        # Test successful preconditions
        assert core_preconditions(target_archive, source_dir)
        
        # Test with existing target archive
        assert not core_preconditions(existing_archive, source_dir)
        
        # Test with non-existent source
        assert not core_preconditions(target_archive, tmp_path / "nonexistent")
        
        # Test with source that's not a directory
        source_file = tmp_path / "file.txt"
        source_file.write_text("content")
        assert not core_preconditions(target_archive, source_file)

    def test_create_zip_archive(self, tmp_path):
        """Test creating ZIP archives."""
        # Setup test directory structure
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        subdir = source_dir / "subdir"
        subdir.mkdir()
        (subdir / "file3.txt").write_text("content3")
        
        # Test creating zip archive
        archive_name = str(tmp_path / "test_archive")
        result = create_zip_archive(archive_name, source_dir)
        assert result is True
        
        # Verify archive was created
        archive_path = Path(f"{archive_name}.zip")
        assert archive_path.exists()
        
        # Verify archive contents
        with zipfile.ZipFile(archive_path, 'r') as zf:
            names = zf.namelist()
            assert 'file1.txt' in names
            assert 'file2.txt' in names
            assert 'subdir/file3.txt' in names

    def test_create_zip_archive_with_extension(self, tmp_path):
        """Test creating ZIP archive when extension is already provided."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        archive_name = str(tmp_path / "test.zip")
        result = create_zip_archive(archive_name, source_dir)
        assert result is True
        assert Path(archive_name).exists()

    def test_create_tar_archive(self, tmp_path):
        """Test creating TAR archives."""
        # Setup test directory
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        
        # Test creating tar archive without compression
        archive_name = str(tmp_path / "test_archive")
        result = create_tar_archive(archive_name, source_dir)
        assert result is True
        
        archive_path = Path(f"{archive_name}.tar")
        assert archive_path.exists()

    def test_create_tar_archive_with_compression(self, tmp_path):
        """Test creating compressed TAR archives."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        # Test with gzip compression
        archive_name = str(tmp_path / "test_gz")
        result = create_tar_archive(archive_name, source_dir, compression="gz")
        assert result is True
        
        archive_path = Path(f"{archive_name}.tar.gz")
        assert archive_path.exists()

    def test_create_tar_archive_invalid_compression(self, tmp_path):
        """Test creating TAR archive with invalid compression."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        archive_name = str(tmp_path / "test")
        result = create_tar_archive(archive_name, source_dir, compression="invalid")
        assert result is False

    @patch('hands_scaphoid.commands.archive_commands.py7zr')
    def test_create_7z_archive(self, mock_py7zr, tmp_path):
        """Test creating 7Z archives."""
        # Setup test directory
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        # Mock the 7z library
        mock_archive = MagicMock()
        mock_py7zr.SevenZipFile.return_value.__enter__.return_value = mock_archive
        
        archive_name = str(tmp_path / "test")
        result = create_7z_archive(archive_name, source_dir)
        assert result is True
        
        # Verify 7z library was called
        mock_py7zr.SevenZipFile.assert_called_once()

    @patch('hands_scaphoid.commands.archive_commands.which')
    @patch('hands_scaphoid.commands.archive_commands.subprocess.run')
    def test_create_rar_archive(self, mock_run, mock_which, tmp_path):
        """Test creating RAR archives."""
        # Setup test directory
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        # Mock 'rar' command availability
        mock_which.return_value = Path("/usr/bin/rar")
        mock_run.return_value.returncode = 0
        
        archive_name = str(tmp_path / "test")
        result = create_rar_archive(archive_name, source_dir)
        assert result is True
        
        # Verify subprocess was called with correct arguments
        expected_cmd = ["rar", "a", str(Path(f"{archive_name}.rar")), str(source_dir)]
        mock_run.assert_called_once()
        assert mock_run.call_args[0][0] == expected_cmd

    @patch('hands_scaphoid.commands.archive_commands.which')
    def test_create_rar_archive_no_executable(self, mock_which, tmp_path):
        """Test creating RAR archive when rar executable is not available."""
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        
        # Mock 'rar' command not available
        mock_which.return_value = None
        
        archive_name = str(tmp_path / "test")
        result = create_rar_archive(archive_name, source_dir)
        assert result is False

    def test_core_extract_conditions(self, tmp_path):
        """Test core conditions for archive extraction."""
        # Create test archive
        archive_file = tmp_path / "test.zip"
        archive_file.write_text("archive content")
        
        target_dir = tmp_path / "extract"
        existing_dir = tmp_path / "existing"
        existing_dir.mkdir()
        
        # Test successful conditions
        assert core_extract_conditions(archive_file, target_dir)
        
        # Test with non-existent archive
        assert not core_extract_conditions(tmp_path / "nonexistent.zip", target_dir)
        
        # Test with existing target directory
        assert not core_extract_conditions(archive_file, existing_dir)

    def test_extract_zip_archive(self, tmp_path):
        """Test extracting ZIP archives."""
        # Create a test zip archive
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.write(source_dir / "file1.txt", "file1.txt")
            zf.write(source_dir / "file2.txt", "file2.txt")
        
        # Test extraction
        target_dir = tmp_path / "extracted"
        result = extract_zip_archive(archive_path, target_dir)
        assert result is True
        
        # Verify extracted files
        assert (target_dir / "file1.txt").exists()
        assert (target_dir / "file2.txt").exists()
        assert (target_dir / "file1.txt").read_text() == "content1"

    def test_extract_tar_archive(self, tmp_path):
        """Test extracting TAR archives."""
        # Create a test tar archive
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        archive_path = tmp_path / "test.tar"
        with tarfile.open(archive_path, 'w') as tf:
            tf.add(source_dir / "file.txt", arcname="file.txt")
        
        # Test extraction
        target_dir = tmp_path / "extracted"
        result = extract_tar_archive(archive_path, target_dir)
        assert result is True
        
        # Verify extracted file
        assert (target_dir / "file.txt").exists()
        assert (target_dir / "file.txt").read_text() == "content"

    @patch('hands_scaphoid.commands.archive_commands.py7zr')
    def test_extract_7z_archive(self, mock_py7zr, tmp_path):
        """Test extracting 7Z archives."""
        archive_path = tmp_path / "test.7z"
        archive_path.write_text("fake 7z content")
        target_dir = tmp_path / "extracted"
        
        # Mock the 7z library
        mock_archive = MagicMock()
        mock_py7zr.SevenZipFile.return_value.__enter__.return_value = mock_archive
        
        result = extract_7z_archive(archive_path, target_dir)
        assert result is True
        
        # Verify 7z library was called
        mock_py7zr.SevenZipFile.assert_called_once()
        mock_archive.extractall.assert_called_once_with(path=target_dir)

    @patch('hands_scaphoid.commands.archive_commands.rarfile')
    def test_extract_rar_archive(self, mock_rarfile, tmp_path):
        """Test extracting RAR archives."""
        archive_path = tmp_path / "test.rar"
        archive_path.write_text("fake rar content")
        target_dir = tmp_path / "extracted"
        
        # Mock the rarfile library
        mock_archive = MagicMock()
        mock_rarfile.RarFile.return_value.__enter__.return_value = mock_archive
        
        result = extract_rar_archive(archive_path, target_dir)
        assert result is True
        
        # Verify rarfile library was called
        mock_rarfile.RarFile.assert_called_once()
        mock_archive.extractall.assert_called_once_with(path=target_dir)

    def test_extract_dispatcher(self, tmp_path):
        """Test the main extract function that dispatches to specific extractors."""
        # Create a test zip archive
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.write(source_dir / "file.txt", "file.txt")
        
        # Test extraction using main extract function
        target_dir = tmp_path / "extracted"
        result = extract(archive_path, target_dir)
        assert result is True
        
        # Verify extracted file
        assert (target_dir / "file.txt").exists()

    def test_extract_unsupported_format(self, tmp_path):
        """Test extracting unsupported archive format."""
        archive_path = tmp_path / "test.unknown"
        archive_path.write_text("unknown format")
        target_dir = tmp_path / "extracted"
        
        result = extract(archive_path, target_dir)
        assert result is False

    def test_list_content_zip(self, tmp_path):
        """Test listing contents of ZIP archive."""
        # Create test zip with content
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")
        
        archive_path = tmp_path / "test.zip"
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.write(source_dir / "file1.txt", "file1.txt")
            zf.write(source_dir / "file2.txt", "file2.txt")
        
        # Test listing contents
        contents = list_contents(archive_path)
        content_names = [str(p) for p in contents]
        assert "file1.txt" in content_names
        assert "file2.txt" in content_names

    def test_list_content_tar(self, tmp_path):
        """Test listing contents of TAR archive."""
        # Create test tar with content
        source_dir = tmp_path / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")
        
        archive_path = tmp_path / "test.tar"
        with tarfile.open(archive_path, 'w') as tf:
            tf.add(source_dir / "file.txt", arcname="file.txt")
        
        # Test listing contents
        contents = list_contents(archive_path)
        content_names = [str(p) for p in contents]
        assert "file.txt" in content_names

    @patch('hands_scaphoid.commands.archive_commands.py7zr')
    def test_list_content_7z(self, mock_py7zr, tmp_path):
        """Test listing contents of 7Z archive."""
        archive_path = tmp_path / "test.7z"
        archive_path.write_text("fake 7z")
        
        # Mock the 7z library
        mock_archive = MagicMock()
        mock_archive.getnames.return_value = ["file1.txt", "file2.txt"]
        mock_py7zr.SevenZipFile.return_value.__enter__.return_value = mock_archive
        
        contents = list_contents(archive_path)
        content_names = [str(p) for p in contents]
        assert "file1.txt" in content_names
        assert "file2.txt" in content_names

    @patch('hands_scaphoid.commands.archive_commands.rarfile')
    def test_list_content_rar(self, mock_rarfile, tmp_path):
        """Test listing contents of RAR archive."""
        archive_path = tmp_path / "test.rar"
        archive_path.write_text("fake rar")
        
        # Mock the rarfile library
        mock_archive = MagicMock()
        mock_info1 = MagicMock()
        mock_info1.filename = "file1.txt"
        mock_info2 = MagicMock()
        mock_info2.filename = "file2.txt"
        mock_archive.infolist.return_value = [mock_info1, mock_info2]
        mock_rarfile.RarFile.return_value.__enter__.return_value = mock_archive
        
        contents = list_contents(archive_path)
        content_names = [str(p) for p in contents]
        assert "file1.txt" in content_names
        assert "file2.txt" in content_names

    def test_list_content_nonexistent(self, tmp_path):
        """Test listing contents of non-existent archive."""
        archive_path = tmp_path / "nonexistent.zip"
        contents = list_contents(archive_path)
        assert contents == []

    def test_list_content_unsupported_format(self, tmp_path):
        """Test listing contents of unsupported archive format."""
        archive_path = tmp_path / "test.unknown"
        archive_path.write_text("unknown format")
        contents = list_contents(archive_path)
        assert contents == []

    def test_error_handling(self, tmp_path):
        """Test error handling in archive operations."""
        # Test with invalid paths
        result = create_zip_archive("", tmp_path / "nonexistent")
        assert result is False
        
        result = extract_zip_archive(tmp_path / "nonexistent.zip", tmp_path / "target")
        assert result is False
