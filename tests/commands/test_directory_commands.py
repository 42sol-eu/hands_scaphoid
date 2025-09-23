"""
----
file:
    name:        test_directory_commands.py  
    uuid:        24b6a98a-97f9-49cd-8040-b36d5773f5e7
description:     Test: directory commands
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
from unittest.mock import patch
    
from hands_scaphoid.commands.directory_commands import (
    get_current_directory,
    get_file_directory,
    list_contents,
    create_directory,
    delete_directory,
)


# DUT class to mock self for methods requiring it
class TestDir:
    """A test directory-like object for testing purposes."""
    def __init__(self, path=None, dry_run=False, entered=False, allow_empty=False):
        """
        Initialize the test directory.
        """
        self._entered = entered
        self.dry_run = dry_run
        self.allow_empty = allow_empty
        self._path = Path(path) if path else Path.cwd()

    def resolve_path(self):
        """
        Resolve the path.
        """
        return self._path

def test_get_current_returns_cwd():
    """ Test that get_current returns the current working directory. """
    assert get_current_directory() == Path(os.getcwd()).resolve()

def test_get_script_folder_with_none(monkeypatch: pytest.MonkeyPatch):
    """
    Test that get_file_directory returns the correct folder when called with None.
    """
    # Simulate caller's __file__
    fake_file = "/tmp/fake_script.py"
    def fake_stack():
        class Frame:
            """A fake frame object."""
            frame = type("f", (), {"f_globals": {"__file__": fake_file}})
        return [None, Frame()]
    monkeypatch.setattr("inspect.stack", fake_stack)
    folder = get_file_directory()
    assert folder == Path(fake_file).parent.resolve()

def test_get_script_folder_with_path():
    """
    Test that get_file_directory returns the correct folder when given a specific path.
    """
    script_path = "/tmp/test_script.py"
    folder = get_file_directory(script_path)
    assert folder == Path("/tmp").resolve()

def test_list_contents_returns_files(tmp_path: Path):
    """
    Test that list_contents returns the correct files in the directory.
    """
    # Create files
    (tmp_path / "file1.txt").write_text("a")
    (tmp_path / "file2.txt").write_text("b")
    DUT = TestDir(path=tmp_path)
    contents = list_contents(DUT)
    assert set(p.name for p in contents) == {"file1.txt", "file2.txt"}

def test_list_contents_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """
    Test that list_contents behaves correctly in dry run mode.
    """
    DUT = TestDir(path=tmp_path, dry_run=True)
    result = list_contents(DUT)
    captured = capsys.readouterr()
    assert "[DRY RUN]" in captured.out
    assert not result

def test_list_contents_permission_error(monkeypatch: pytest.MonkeyPatch):
    """
    Test that list_contents handles permission errors gracefully.
    """
    DUT = TestDir(path="/forbidden")
    monkeypatch.setattr(Path, "iterdir", lambda self: (_ for _ in ()).throw(PermissionError()))
    result = list_contents(DUT)
    assert not result

def test_delete_directory_success(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """ Test that delete_directory successfully deletes a directory. """
    subdir = tmp_path / "to_delete"
    subdir.mkdir()
    DUT = TestDir(path=tmp_path)
    result = delete_directory(DUT, "to_delete")
    captured = capsys.readouterr()
    assert result is True
    assert "Deleted directory" in captured.out
    assert not subdir.exists()

def test_delete_directory_dry_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    subdir = tmp_path / "dry_run"
    subdir.mkdir()
    DUT = TestDir(path=tmp_path)
    result = delete_directory(DUT, "dry_run", dry_run=True)
    captured = capsys.readouterr()
    assert result is True
    assert "[DRY RUN]" in captured.out
    assert subdir.exists()

def test_delete_directory_not_exists(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    """ Test that delete_directory handles non-existent directories gracefully. """
    DUT = TestDir(path=tmp_path)
    result = delete_directory(DUT, "missing")
    captured = capsys.readouterr()
    assert result is False
    assert "Directory does not exist" in captured.out

def test_delete_directory_exception(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]):
    """ Test that delete_directory handles exceptions gracefully. """
    
    result = True
    subdir = tmp_path / "error_dir"
    subdir.mkdir()
    DUT = TestDir(path=tmp_path)
    with patch.object(subdir, "rmdir", side_effect=OSError("fail")):
        result = delete_directory(DUT, "error_dir")
        captured = capsys.readouterr()
    assert result is False
    assert "Error deleting directory" in captured.out


# TODO: implement tests all directory_commands