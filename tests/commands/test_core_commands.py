"""

----
file:
    name:        test_core_commands.py  
    uuid:        d397dc43-5ad4-4def-adaf-9a7a5d9bd4ea
description:     Test: core commands
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
    
from hands_scaphoid.commands.core_commands import (
    exists,
    is_instance,
    is_item,
    is_directory,
    is_file,
    is_git_project,
    is_hands_project,
    is_link,
    is_object,
    is_variable,
    is_vscode_project,
    get_file_extension,
)
def test_exists(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    assert exists(file)
    assert not exists(tmp_path / "nofile.txt")

def test_is_object(tmp_path):
    file = tmp_path / "file.txt"
    file.write_text("content")
    dir_path = tmp_path / "dir"
    dir_path.mkdir()
    symlink = tmp_path / "link"
    symlink.symlink_to(file)
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
    symlink = tmp_path / "link"
    symlink.symlink_to(file)
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
    symlink = tmp_path / "link"
    symlink.symlink_to(file)
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
    assert get_file_extension(filename) == expected
    assert get_file_extension(Path(filename)) == expected

# TODO: implement tests all core_commands
