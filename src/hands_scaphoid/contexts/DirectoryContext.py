#!/usr/bin/env python3
"""
Directory context manager for hands-scaphoid package.

This module provides the DirectoryContext class for managing directory operations
with context manager support and hierarchical path resolution.

File:
    name: DirectoryContext.py
    date: 2025-09-16

Description:
    Directory context manager for hierarchical file system operations

Authors: ["Andreas Häberle"]
"""

from pathlib import Path
from typing import Optional, Union, List, Any
from .Context import Context
from .DirectoryOperations import Directory
from .__base__ import PathLike, os, console


class DirectoryContext(Context):
    """
    Directory context manager for hierarchical file system operations.

    This class allows you to work with directories in a hierarchical context,
    automatically changing the working directory when entering the context
    and restoring it when exiting. It delegates actual directory operations
    to the Directory class.

    Example:
        with DirectoryContext('~') as home:
            with DirectoryContext('projects') as projects:
                # Now working in ~/projects
                with DirectoryContext('myproject') as project:
                    # Now working in ~/projects/myproject
                    project.list_contents()
    """

    def __init__(
        self,
        path: PathLike,
        create: bool = True,
        dry_run: bool = False,
        enable_globals: bool = False,
    ):
        """
        Initialize a new DirectoryContext.

        Args:
            path: The directory path (relative or absolute)
            create: Whether to create the directory if it doesn't exist (default: True)
            dry_run: Whether to simulate operations without making actual changes
            enable_globals: Whether to enable global function access within context
        """
        super().__init__(path, create, dry_run, enable_globals)
        self.previous_cwd: Optional[Path] = None

    def _create_path(self, resolved_path: Path) -> None:
        """
        Create the directory if it doesn't exist.

        Args:
            resolved_path: The resolved absolute path to create
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would create directory: {resolved_path}[/dim]"
            )
            return

        Directory.create_directory(resolved_path, parents=True, exist_ok=True)

    def _enter_context(self, resolved_path: Path) -> None:
        """
        Change to the directory when entering the context.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would change to directory: {resolved_path}[/dim]"
            )
            return

        self.previous_cwd = Path.cwd()
        Directory.change_directory(resolved_path)

    def _exit_context(self, resolved_path: Path) -> None:
        """
        Restore the previous directory when exiting the context.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would restore directory: {self.previous_cwd}[/dim]"
            )
            return

        if self.previous_cwd:
            try:
                os.chdir(self.previous_cwd)
                console.print(f"[blue]Restored directory:[/blue] {self.previous_cwd}")
            except Exception as e:
                console.print(
                    f"[red]Error restoring directory {self.previous_cwd}:[/red] {e}"
                )
                raise

    def list_contents(self) -> List[str]:
        """
        List all items in the directory.

        Returns:
            List of file and directory names
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would list contents of: {self.resolve_path()}[/dim]"
            )
            return ["[DRY RUN] Directory contents would be listed here"]

        return Directory.list_contents(self.resolve_path())

    def list_files(self, extension: Optional[str] = None) -> List[str]:
        """
        List files in the directory, optionally filtered by extension.

        Args:
            extension: File extension filter (without dot, e.g., 'txt')

        Returns:
            List of filenames
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would list files in: {self.resolve_path()}[/dim]"
            )
            return ["[DRY RUN] Files would be listed here"]

        return Directory.list_files(self.resolve_path(), extension)

    def list_directories(self) -> List[str]:
        """
        List subdirectories in the directory.

        Returns:
            List of subdirectory names
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would list directories in: {self.resolve_path()}[/dim]"
            )
            return ["[DRY RUN] Directories would be listed here"]

        return Directory.list_directories(self.resolve_path())

    def create_subdirectory(self, name: str) -> "DirectoryContext":
        """
        Create a subdirectory within the current context.

        Args:
            name: Name of the subdirectory to create

        Returns:
            New DirectoryContext instance for method chaining
        """
        subdir_path = self.resolve_path() / name

        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would create subdirectory: {subdir_path}[/dim]"
            )
            return DirectoryContext(subdir_path, dry_run=True)

        Directory.create_directory(subdir_path, parents=True, exist_ok=True)
        return DirectoryContext(subdir_path)

    def is_empty(self) -> bool:
        """
        Check if the directory is empty.

        Returns:
            True if directory is empty, False otherwise
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would check if directory is empty: {self.resolve_path()}[/dim]"
            )
            return False

        return Directory.is_empty(self.resolve_path())

    def directory_exists(self) -> bool:
        """
        Check if the directory exists.

        Returns:
            True if directory exists, False otherwise
        """
        return Directory.directory_exists(self.resolve_path())

    def get_directory_size(self) -> int:
        """
        Get the total size of the directory and its contents in bytes.

        Returns:
            Total size in bytes
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would get directory size: {self.resolve_path()}[/dim]"
            )
            return 0

        return Directory.get_directory_size(self.resolve_path())

    def copy_to(
        self, target_path: PathLike, dirs_exist_ok: bool = False
    ) -> "DirectoryContext":
        """
        Copy this directory and its contents to another location.

        Args:
            target_path: Target directory path
            dirs_exist_ok: Whether to allow copying to existing directory

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would copy directory: {self.resolve_path()} → {target_path}[/dim]"
            )
            return self

        Directory.copy_directory(self.resolve_path(), target_path, dirs_exist_ok)
        return self

    def move_to(self, target_path: PathLike) -> "DirectoryContext":
        """
        Move this directory to another location.

        Args:
            target_path: Target directory path

        Returns:
            New DirectoryContext for the moved directory
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would move directory: {self.resolve_path()} → {target_path}[/dim]"
            )
            return DirectoryContext(target_path, dry_run=True)

        Directory.move_directory(self.resolve_path(), target_path)
        return DirectoryContext(target_path)

    def delete(self, recursive: bool = False) -> None:
        """
        Delete the directory.

        Args:
            recursive: Whether to delete directory and all its contents

        Note: This will also exit the context as the directory no longer exists.
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would delete directory: {self.resolve_path()}[/dim]"
            )
            return

        # Change back to previous directory before deletion
        if self.previous_cwd:
            os.chdir(self.previous_cwd)

        Directory.delete_directory(self.resolve_path(), recursive)

    def create_file(self, filename: str) -> Path:
        """
        Create a file in this directory.

        Args:
            filename: Name of the file to create

        Returns:
            Path to the created file
        """
        from .FileOperations import File

        file_path = self.resolve_path() / filename

        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would create file: {file_path}[/dim]")
            return file_path

        File.create_file(file_path, create_dirs=False)
        return file_path

    def write_file(self, filename: str, content: str) -> Path:
        """
        Create a file with content in this directory.

        Args:
            filename: Name of the file to create
            content: Content to write to the file

        Returns:
            Path to the created file
        """
        from .FileOperations import File

        file_path = self.resolve_path() / filename

        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would write file: {file_path}[/dim]")
            return file_path

        File.write_content(file_path, content, create_dirs=False)
        return file_path
