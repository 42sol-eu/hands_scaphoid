#!/usr/bin/env python3
"""
Directory operations module for hands-scaphoid package.

This module provides the Directory class for pure directory operations
without context management.

File:
    name: DirectoryOperations.py
    date: 2025-09-16

Description:
    Pure directory operations class - no context management

Authors: ["Andreas Häberle"]
"""

import os
import shutil
from pathlib import Path
from typing import List, Optional, Union
from ..__base__ import PathLike, console
from .ObjectCore import ObjectCore


class DirectoryCore(ObjectCore):
    """
    Pure directory operations class without context management.

    This class provides static methods for directory operations that can be used
    independently of any context manager. All methods operate on explicit
    directory paths and do not maintain any state.

    Example:
        # Direct directory operations
        Directory.create_directory(Path("myproject"))
        files = Directory.list_contents(Path("myproject"))
        Directory.copy_directory(Path("source"), Path("target"))
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)

    def __repr__(self):
        return f"DirectoryCore(name={self.name}, path={self.value})"

    @staticmethod
    def create_directory(
        dir_path: PathLike, parents: bool = True, exist_ok: bool = True
    ) -> None:
        """
        Create a directory.

        Args:
            dir_path: Path to the directory to create
            parents: Whether to create parent directories if they don't exist
            exist_ok: Whether to raise an error if directory already exists

        Raises:
            PermissionError: If lacking create permissions
            FileExistsError: If directory exists and exist_ok is False
        """
        path = Path(dir_path)
        try:
            path.mkdir(parents=parents, exist_ok=exist_ok)
            console.print(f"[green]Created directory:[/green] {path}")
        except FileExistsError:
            if not exist_ok:
                console.print(f"[red]Directory already exists:[/red] {path}")
                raise
        except PermissionError:
            console.print(f"[red]Permission denied creating directory:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error creating directory {path}:[/red] {e}")
            raise

    @staticmethod
    def list_contents(dir_path: PathLike) -> List[str]:
        """
        List all items in a directory.

        Args:
            dir_path: Path to the directory to list

        Returns:
            List of file and directory names

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If lacking read permissions
        """
        path = Path(dir_path)
        try:
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {path}")

            contents = [item.name for item in path.iterdir()]
            console.print(f"[blue]Listed {len(contents)} items in:[/blue] {path}")
            return sorted(contents)
        except PermissionError:
            console.print(f"[red]Permission denied reading directory:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error listing directory {path}:[/red] {e}")
            raise

    @staticmethod
    def list_files(dir_path: PathLike, extension: Optional[str] = None) -> List[str]:
        """
        List files in a directory, optionally filtered by extension.

        Args:
            dir_path: Path to the directory to list
            extension: File extension filter (without dot, e.g., 'txt')

        Returns:
            List of filenames
        """
        path = Path(dir_path)
        try:
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {path}")

            files = []
            for item in path.iterdir():
                if item.is_file():
                    if (
                        extension is None
                        or item.suffix.lstrip(".").lower() == extension.lower()
                    ):
                        files.append(item.name)

            console.print(f"[blue]Found {len(files)} files in:[/blue] {path}")
            return sorted(files)
        except PermissionError:
            console.print(f"[red]Permission denied reading directory:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error listing files in {path}:[/red] {e}")
            raise

    @staticmethod
    def list_directories(dir_path: PathLike) -> List[str]:
        """
        List subdirectories in a directory.

        Args:
            dir_path: Path to the directory to list

        Returns:
            List of subdirectory names
        """
        path = Path(dir_path)
        try:
            if not path.exists():
                raise FileNotFoundError(f"Directory not found: {path}")
            if not path.is_dir():
                raise NotADirectoryError(f"Path is not a directory: {path}")

            dirs = []
            for item in path.iterdir():
                if item.is_dir():
                    dirs.append(item.name)

            console.print(f"[blue]Found {len(dirs)} subdirectories in:[/blue] {path}")
            return sorted(dirs)
        except PermissionError:
            console.print(f"[red]Permission denied reading directory:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error listing directories in {path}:[/red] {e}")
            raise

    @staticmethod
    def directory_exists(dir_path: PathLike) -> bool:
        """
        Check if a directory exists.

        Args:
            dir_path: Path to check

        Returns:
            True if directory exists and is a directory, False otherwise
        """
        path = Path(dir_path)
        return path.exists() and path.is_dir()

    @staticmethod
    def is_empty(dir_path: PathLike) -> bool:
        """
        Check if a directory is empty.

        Args:
            dir_path: Path to the directory to check

        Returns:
            True if directory is empty, False otherwise

        Raises:
            FileNotFoundError: If directory doesn't exist
            NotADirectoryError: If path is not a directory
        """
        path = Path(dir_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        return len(list(path.iterdir())) == 0

    @staticmethod
    def copy_directory(
        source_path: PathLike, target_path: PathLike, dirs_exist_ok: bool = False
    ) -> None:
        """
        Copy a directory and its contents to a new location.

        Args:
            source_path: Path to the source directory
            target_path: Path to the target directory
            dirs_exist_ok: Whether to allow copying to existing directory

        Raises:
            FileNotFoundError: If source directory doesn't exist
            PermissionError: If lacking copy permissions
        """
        source = Path(source_path)
        target = Path(target_path)

        if not source.exists():
            raise FileNotFoundError(f"Source directory not found: {source}")
        if not source.is_dir():
            raise NotADirectoryError(f"Source path is not a directory: {source}")

        try:
            shutil.copytree(source, target, dirs_exist_ok=dirs_exist_ok)
            console.print(f"[green]Copied directory:[/green] {source} → {target}")
        except PermissionError:
            console.print(
                f"[red]Permission denied copying directory:[/red] {source} → {target}"
            )
            raise
        except Exception as e:
            console.print(
                f"[red]Error copying directory {source} → {target}:[/red] {e}"
            )
            raise

    @staticmethod
    def move_directory(source_path: PathLike, target_path: PathLike) -> None:
        """
        Move a directory to a new location.

        Args:
            source_path: Path to the source directory
            target_path: Path to the target directory

        Raises:
            FileNotFoundError: If source directory doesn't exist
            PermissionError: If lacking move permissions
        """
        source = Path(source_path)
        target = Path(target_path)

        if not source.exists():
            raise FileNotFoundError(f"Source directory not found: {source}")
        if not source.is_dir():
            raise NotADirectoryError(f"Source path is not a directory: {source}")

        try:
            shutil.move(str(source), str(target))
            console.print(f"[green]Moved directory:[/green] {source} → {target}")
        except PermissionError:
            console.print(
                f"[red]Permission denied moving directory:[/red] {source} → {target}"
            )
            raise
        except Exception as e:
            console.print(f"[red]Error moving directory {source} → {target}:[/red] {e}")
            raise

    @staticmethod
    def delete_directory(dir_path: PathLike, recursive: bool = False) -> None:
        """
        Delete a directory.

        Args:
            dir_path: Path to the directory to delete
            recursive: Whether to delete directory and all its contents

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If lacking delete permissions
            OSError: If directory is not empty and recursive is False
        """
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        try:
            if recursive:
                shutil.rmtree(path)
                console.print(f"[green]Deleted directory recursively:[/green] {path}")
            else:
                path.rmdir()
                console.print(f"[green]Deleted directory:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied deleting directory:[/red] {path}")
            raise
        except OSError as e:
            if "not empty" in str(e).lower():
                console.print(
                    f"[red]Directory not empty (use recursive=True):[/red] {path}"
                )
            else:
                console.print(f"[red]Error deleting directory {path}:[/red] {e}")
            raise
        except Exception as e:
            console.print(f"[red]Error deleting directory {path}:[/red] {e}")
            raise

    @staticmethod
    def get_directory_size(dir_path: PathLike) -> int:
        """
        Get the total size of a directory and its contents in bytes.

        Args:
            dir_path: Path to the directory

        Returns:
            Total size in bytes

        Raises:
            FileNotFoundError: If directory doesn't exist
        """
        path = Path(dir_path)
        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        total_size = 0
        try:
            for item in path.rglob("*"):
                if item.is_file():
                    total_size += item.stat().st_size
            return total_size
        except PermissionError:
            console.print(
                f"[red]Permission denied accessing some files in:[/red] {path}"
            )
            raise
        except Exception as e:
            console.print(f"[red]Error calculating directory size {path}:[/red] {e}")
            raise

    @staticmethod
    def change_directory(dir_path: PathLike) -> str:
        """
        Change the current working directory.

        Args:
            dir_path: Path to change to

        Returns:
            Previous working directory path

        Raises:
            FileNotFoundError: If directory doesn't exist
            PermissionError: If lacking access permissions
        """
        path = Path(dir_path)

        if not path.exists():
            raise FileNotFoundError(f"Directory not found: {path}")
        if not path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {path}")

        try:
            previous_cwd = os.getcwd()
            os.chdir(path)
            console.print(f"[blue]Changed directory to:[/blue] {path}")
            return previous_cwd
        except PermissionError:
            console.print(f"[red]Permission denied changing to directory:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error changing to directory {path}:[/red] {e}")
            raise
