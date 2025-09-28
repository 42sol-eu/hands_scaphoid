#!/usr/bin/env python3
"""
Comprehensive unit tests for the separated architecture.

---yaml
File:
    name: test_separated_architecture.py
    uuid: 5a6b7c8d-9e0f-1234-5678-90abcdef1234
    date: 2025-09-28

Description:
    Complete test coverage for separated architecture including operations classes
    (File, Directory, Archive) and context classes (FileContext, DirectoryContext, 
    ArchiveContext) with context managers and global functions.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# Standard library imports
import sys
import os
import builtins
import tempfile
import shutil
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Third-party imports
import pytest

# Project imports - adjust path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from hands_scaphoid.contexts.ContextCore import Context
from hands_scaphoid.objects.FileCore import File
from hands_scaphoid.objects.DirectoryCore import Directory
from hands_scaphoid.objects.ArchiveFile import Archive

# from hands_scaphoid.contexts.FileContext import FileContext
# from hands_scaphoid.contexts.DirectoryContext import DirectoryContext
from hands_scaphoid.ArchiveContext import ArchiveContext


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    # Cleanup
    if Path(temp_dir).exists():
        shutil.rmtree(temp_dir)


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    fd, temp_file = tempfile.mkstemp(suffix=".txt")
    os.close(fd)
    yield Path(temp_file)
    # Cleanup
    if Path(temp_file).exists():
        Path(temp_file).unlink()


class TestFileOperations:
    """Test cases for the File operations class."""

    def test_write_and_read_content(self, temp_file):
        """Test writing and reading file content."""
        content = "Hello, World!\nThis is a test file."

        # Write content
        File.write_content(temp_file, content)
        assert temp_file.exists()

        # Read content back
        read_content = File.read_content(temp_file)
        assert read_content == content

    def test_read_lines(self, temp_file):
        """Test reading file lines."""
        content = "line1\nline2\nline3"
        File.write_content(temp_file, content)

        lines = File.read_lines(temp_file)
        assert lines == ["line1", "line2", "line3"]

    def test_append_line(self, temp_file):
        """Test appending lines to file."""
        File.write_content(temp_file, "initial content")
        File.append_line(temp_file, "appended line")

        content = File.read_content(temp_file)
        assert content == "initial content\nappended line"

    def test_add_heading(self, temp_file):
        """Test adding heading to file."""
        File.write_content(temp_file, "content")
        File.add_heading(temp_file, "Test Heading")

        content = File.read_content(temp_file)
        expected = "content\n\n## Test Heading\n"
        assert content == expected

    def test_file_exists(self, temp_file):
        """Test file existence check."""
        assert File.file_exists(temp_file)

        nonexistent = temp_file.parent / "nonexistent.txt"
        assert not File.file_exists(nonexistent)

    def test_copy_file(self, temp_file, temp_dir):
        """Test file copying."""
        File.write_content(temp_file, "test content")
        target = temp_dir / "copied_file.txt"

        File.copy_file(temp_file, target)
        assert target.exists()
        assert File.read_content(target) == "test content"

    def test_delete_file(self, temp_file):
        """Test file deletion."""
        File.write_content(temp_file, "test")
        assert temp_file.exists()

        File.delete_file(temp_file)
        assert not temp_file.exists()

    def test_create_file(self, temp_dir):
        """Test file creation."""
        file_path = temp_dir / "new_file.txt"
        content = "new file content"

        File.create_file(file_path, content)
        assert file_path.exists()
        assert File.read_content(file_path) == content


class TestDirectoryOperations:
    """Test cases for the Directory operations class."""

    def test_create_directory(self, temp_dir):
        """Test directory creation."""
        new_dir = temp_dir / "new_directory"

        Directory.create_directory(new_dir)
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_create_nested_directory(self, temp_dir):
        """Test nested directory creation."""
        nested_dir = temp_dir / "level1" / "level2" / "level3"

        Directory.create_directory(nested_dir)
        assert nested_dir.exists()
        assert nested_dir.is_dir()

    def test_list_contents(self, temp_dir):
        """Test directory content listing."""
        # Create test files and directories
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.py").touch()
        (temp_dir / "subdir").mkdir()

        contents = Directory.list_contents(temp_dir)
        assert "file1.txt" in contents
        assert "file2.py" in contents
        assert "subdir" in contents

    def test_list_files_with_extension(self, temp_dir):
        """Test listing files with specific extension."""
        (temp_dir / "file1.txt").touch()
        (temp_dir / "file2.py").touch()
        (temp_dir / "file3.txt").touch()

        txt_files = Directory.list_files(temp_dir, "*.txt")
        assert "file1.txt" in txt_files
        assert "file3.txt" in txt_files
        assert "file2.py" not in txt_files

    def test_copy_directory(self, temp_dir):
        """Test directory copying."""
        source_dir = temp_dir / "source"
        target_dir = temp_dir / "target"

        # Create source directory with content
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("test content")
        (source_dir / "subdir").mkdir()
        (source_dir / "subdir" / "nested.txt").write_text("nested content")

        Directory.copy_directory(source_dir, target_dir)

        assert target_dir.exists()
        assert (target_dir / "file.txt").exists()
        assert (target_dir / "subdir" / "nested.txt").exists()
        assert (target_dir / "file.txt").read_text() == "test content"

    def test_delete_directory(self, temp_dir):
        """Test directory deletion."""
        test_dir = temp_dir / "to_delete"
        test_dir.mkdir()
        (test_dir / "file.txt").touch()

        assert test_dir.exists()
        Directory.delete_directory(test_dir)
        assert not test_dir.exists()

    def test_directory_exists(self, temp_dir):
        """Test directory existence check."""
        assert Directory.directory_exists(temp_dir)

        nonexistent = temp_dir / "nonexistent"
        assert not Directory.directory_exists(nonexistent)

    def test_create_file_in_directory(self, temp_dir):
        """Test creating file in directory."""
        file_path = "test_file.txt"
        content = "test content"

        Directory.create_file(temp_dir, file_path, content)

        full_path = temp_dir / file_path
        assert full_path.exists()
        assert full_path.read_text() == content


class TestArchiveOperations:
    """Test cases for the Archive operations class."""

    def test_create_zip_archive(self, temp_dir):
        """Test ZIP archive creation."""
        # Create source content
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")
        (source_dir / "file2.txt").write_text("content2")

        archive_path = temp_dir / "test.zip"

        Archive.create_zip_archive(archive_path, source_dir)

        assert archive_path.exists()

        # Verify archive contents
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            names = zip_file.namelist()
            assert any("file1.txt" in name for name in names)
            assert any("file2.txt" in name for name in names)

    def test_create_tar_archive(self, temp_dir):
        """Test TAR archive creation."""
        # Create source content
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")

        archive_path = temp_dir / "test.tar.gz"

        Archive.create_tar_archive(archive_path, source_dir, compression="gz")

        assert archive_path.exists()

        # Verify archive contents
        with tarfile.open(archive_path, "r:gz") as tar_file:
            names = tar_file.getnames()
            assert any("file1.txt" in name for name in names)

    def test_extract_zip_archive(self, temp_dir):
        """Test ZIP archive extraction."""
        # Create archive
        archive_path = temp_dir / "test.zip"
        extract_dir = temp_dir / "extracted"

        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("test_file.txt", "test content")
            zip_file.writestr("subdir/nested.txt", "nested content")

        Archive.extract_archive(archive_path, extract_dir)

        assert extract_dir.exists()
        assert (extract_dir / "test_file.txt").exists()
        assert (extract_dir / "subdir" / "nested.txt").exists()
        assert (extract_dir / "test_file.txt").read_text() == "test content"

    def test_list_archive_contents(self, temp_dir):
        """Test listing archive contents."""
        archive_path = temp_dir / "test.zip"

        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("file1.txt", "content1")
            zip_file.writestr("dir/file2.txt", "content2")

        contents = Archive.list_archive_contents(archive_path)

        assert "file1.txt" in contents
        assert "dir/file2.txt" in contents

    def test_add_file_to_zip(self, temp_dir):
        """Test adding file to existing ZIP archive."""
        archive_path = temp_dir / "test.zip"
        file_to_add = temp_dir / "add_me.txt"
        file_to_add.write_text("added content")

        # Create initial archive
        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("existing.txt", "existing content")

        Archive.add_file_to_zip(archive_path, file_to_add)

        # Verify both files exist
        contents = Archive.list_archive_contents(archive_path)
        assert "existing.txt" in contents
        assert "add_me.txt" in contents

    def test_is_archive_file(self, temp_dir):
        """Test archive file detection."""
        zip_file = temp_dir / "test.zip"
        tar_file = temp_dir / "test.tar.gz"
        text_file = temp_dir / "test.txt"

        # Create files
        with zipfile.ZipFile(zip_file, "w"):
            pass
        text_file.write_text("not an archive")

        assert Archive.is_archive_file(zip_file)
        assert Archive.is_archive_file(tar_file)  # Based on extension
        assert not Archive.is_archive_file(text_file)

    def test_archive_info(self, temp_dir):
        """Test getting archive information."""
        archive_path = temp_dir / "test.zip"

        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("file1.txt", "content1")
            zip_file.writestr("file2.txt", "longer content for file2")

        info = Archive.archive_info(archive_path)

        assert info["type"] == "zip"
        assert info["file_count"] == 2
        assert "compressed_size" in info
        assert "uncompressed_size" in info


class TestFileContext:
    """Test cases for the FileContext class."""

    def test_file_context_creation(self, temp_dir):
        """Test FileContext creation and basic operations."""
        file_path = "test_file.txt"

        with DirectoryContext(temp_dir):
            with FileContext(file_path, create=True) as f:
                f.write_content("test content")

        full_path = temp_dir / file_path
        assert full_path.exists()
        assert full_path.read_text() == "test content"

    def test_file_context_method_chaining(self, temp_dir):
        """Test FileContext method chaining."""
        with DirectoryContext(temp_dir):
            with FileContext("chain_test.txt", create=True) as f:
                f.write_content("Initial content").add_heading("Section 1").append_line(
                    "Line 1"
                ).append_line("Line 2")

        content = (temp_dir / "chain_test.txt").read_text()
        assert "Initial content" in content
        assert "## Section 1" in content
        assert "Line 1" in content
        assert "Line 2" in content

    def test_file_context_dry_run(self, temp_dir):
        """Test FileContext dry run mode."""
        file_path = temp_dir / "dry_run_test.txt"

        with FileContext(file_path, create=True, dry_run=True) as f:
            f.write_content("should not be written")

        # File should not exist in dry run mode
        assert not file_path.exists()


class TestDirectoryContext:
    """Test cases for the DirectoryContext class."""

    def test_directory_context_creation(self, temp_dir):
        """Test DirectoryContext creation."""
        test_dir = temp_dir / "test_context_dir"

        with DirectoryContext(test_dir, create=True) as d:
            assert test_dir.exists()
            assert test_dir.is_dir()

    def test_directory_context_navigation(self, temp_dir):
        """Test directory navigation with context."""
        test_dir = temp_dir / "nav_test"
        test_dir.mkdir()

        original_cwd = Path.cwd()

        with DirectoryContext(test_dir) as d:
            # Should be in the test directory
            current_path = d.resolve_path()
            assert current_path == test_dir

        # Should return to original directory
        # Note: DirectoryContext doesn't change actual CWD, just context

    def test_hierarchical_contexts(self, temp_dir):
        """Test hierarchical directory contexts."""
        with DirectoryContext(temp_dir) as root:
            root.create_directory("level1")

            with DirectoryContext("level1") as level1:
                level1.create_directory("level2")

                with DirectoryContext("level2") as level2:
                    level2.create_file("deep_file.txt", "deep content")

        # Verify the hierarchical structure
        assert (temp_dir / "level1").exists()
        assert (temp_dir / "level1" / "level2").exists()
        assert (temp_dir / "level1" / "level2" / "deep_file.txt").exists()

        content = (temp_dir / "level1" / "level2" / "deep_file.txt").read_text()
        assert content == "deep content"

    def test_directory_context_dry_run(self, temp_dir):
        """Test DirectoryContext dry run mode."""
        test_dir = temp_dir / "dry_run_dir"

        with DirectoryContext(test_dir, create=True, dry_run=True) as d:
            d.create_directory("should_not_exist")
            d.create_file("should_not_exist.txt", "content")

        # Directory and file should not exist in dry run mode
        assert not test_dir.exists()


class TestArchiveContext:
    """Test cases for the ArchiveContext class."""

    def test_archive_context_creation(self, temp_dir):
        """Test ArchiveContext creation."""
        # Create source content
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file1.txt").write_text("content1")

        archive_path = temp_dir / "test.zip"

        with ArchiveContext(source=source_dir, target=archive_path) as archive:
            contents = archive.list_contents()
            assert any("file1.txt" in content for content in contents)

    def test_archive_context_selective_addition(self, temp_dir):
        """Test selective file addition to archive."""
        file1 = temp_dir / "file1.txt"
        file2 = temp_dir / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")

        archive_path = temp_dir / "selective.zip"

        with ArchiveContext(target=archive_path) as archive:
            archive.add_file(file1)
            archive.add_file(file2)

            contents = archive.list_contents()
            assert "file1.txt" in contents
            assert "file2.txt" in contents

    def test_archive_context_extraction(self, temp_dir):
        """Test archive extraction with context."""
        # Create archive
        archive_path = temp_dir / "extract_test.zip"
        with zipfile.ZipFile(archive_path, "w") as zip_file:
            zip_file.writestr("extracted_file.txt", "extracted content")

        extract_dir = temp_dir / "extracted"

        with ArchiveContext(target=archive_path) as archive:
            archive.extract_all(extract_dir)

        assert (extract_dir / "extracted_file.txt").exists()
        assert (extract_dir / "extracted_file.txt").read_text() == "extracted content"

    def test_archive_context_dry_run(self, temp_dir):
        """Test ArchiveContext dry run mode."""
        source_dir = temp_dir / "source"
        source_dir.mkdir()
        (source_dir / "file.txt").write_text("content")

        archive_path = temp_dir / "dry_run.zip"

        with ArchiveContext(
            source=source_dir, target=archive_path, dry_run=True
        ) as archive:
            # Operations should be simulated
            pass

        # Archive should not be created in dry run mode
        assert not archive_path.exists()


class TestGlobalFunctions:
    """Test cases for global function injection."""

    def test_global_functions_file_context(self, temp_dir):
        """Test global functions with FileContext."""
        original_builtins = set(dir(builtins))

        file_path = temp_dir / "global_test.txt"

        with FileContext(file_path, create=True, enable_globals=True) as f:
            # Check that functions are available globally
            current_builtins = set(dir(builtins))
            new_functions = current_builtins - original_builtins

            # Some expected functions should be added
            expected_functions = {"read_content", "write_content", "append_line"}
            assert expected_functions.issubset(new_functions)

        # Functions should be removed after context
        final_builtins = set(dir(builtins))
        assert final_builtins == original_builtins

    def test_global_functions_directory_context(self, temp_dir):
        """Test global functions with DirectoryContext."""
        original_builtins = set(dir(builtins))

        with DirectoryContext(temp_dir, enable_globals=True) as d:
            # Check that functions are available globally
            current_builtins = set(dir(builtins))
            new_functions = current_builtins - original_builtins

            # Some expected functions should be added
            expected_functions = {
                "create_directory",
                "list_contents",
                "change_directory",
            }
            assert expected_functions.issubset(new_functions)

        # Functions should be removed after context
        final_builtins = set(dir(builtins))
        assert final_builtins == original_builtins


class TestErrorHandling:
    """Test cases for error handling."""

    def test_file_operations_file_not_found(self):
        """Test FileOperations error handling for missing files."""
        nonexistent_file = Path("/nonexistent/file.txt")

        with pytest.raises(FileNotFoundError):
            File.read_content(nonexistent_file)

        with pytest.raises(FileNotFoundError):
            File.copy_file(nonexistent_file, Path("/tmp/target.txt"))

    def test_directory_operations_permission_error(self):
        """Test DirectoryOperations error handling for permission issues."""
        # This test might not work on all systems due to permission differences
        # We'll test with a non-existent parent directory instead
        invalid_path = Path("/nonexistent/parent/child")

        with pytest.raises((FileNotFoundError, PermissionError)):
            Directory.create_directory(invalid_path)

    def test_archive_operations_invalid_archive(self, temp_dir):
        """Test Archive operations error handling for invalid archives."""
        invalid_archive = temp_dir / "not_an_archive.txt"
        invalid_archive.write_text("This is not an archive")

        with pytest.raises((zipfile.BadZipFile, Exception)):
            Archive.list_archive_contents(invalid_archive)

    def test_context_manager_cleanup_on_exception(self, temp_dir):
        """Test that context managers clean up properly on exceptions."""
        test_dir = temp_dir / "exception_test"

        with pytest.raises(ValueError):
            with DirectoryContext(test_dir, create=True) as d:
                # Create some content
                d.create_file("test.txt", "content")
                # Raise an exception
                raise ValueError("Test exception")

        # Directory should still exist (creation was successful)
        assert test_dir.exists()
        assert (test_dir / "test.txt").exists()


class TestIntegration:
    """Integration tests combining multiple operations."""

    def test_complete_project_workflow(self, temp_dir):
        """Test a complete project creation workflow."""
        project_name = "test_project"

        with DirectoryContext(temp_dir) as workspace:
            # Create project structure
            with DirectoryContext(project_name, create=True) as project:
                project.create_directory("src")
                project.create_directory("tests")
                project.create_directory("docs")

                # Create source files
                with DirectoryContext("src") as src:
                    with FileContext("__init__.py", create=True) as init:
                        init.write_content(f'"""The {project_name} package."""')

                    with FileContext("main.py", create=True) as main:
                        main.write_content("#!/usr/bin/env python3").append_line(
                            f'"""Main module for {project_name}."""'
                        ).append_line("").append_line("def main():").append_line(
                            f'    print("Hello from {project_name}!")'
                        )

                # Create documentation
                with DirectoryContext("docs") as docs:
                    with FileContext("README.md", create=True) as readme:
                        readme.write_content(f"# {project_name.title()}").append_line(
                            ""
                        ).add_heading("Installation").append_line("pip install -e .")

                # Create archive backup
                with ArchiveContext(
                    source=".", target=f"{project_name}_backup.zip"
                ) as backup:
                    info = backup.get_archive_info()
                    assert info["file_count"] > 0

        # Verify the complete structure
        project_path = temp_dir / project_name
        assert project_path.exists()
        assert (project_path / "src" / "__init__.py").exists()
        assert (project_path / "src" / "main.py").exists()
        assert (project_path / "docs" / "README.md").exists()
        assert (project_path / f"{project_name}_backup.zip").exists()

        # Verify file contents
        main_content = (project_path / "src" / "main.py").read_text()
        assert "def main():" in main_content
        assert f"Hello from {project_name}" in main_content

        readme_content = (project_path / "docs" / "README.md").read_text()
        assert f"# {project_name.title()}" in readme_content
        assert "## Installation" in readme_content
