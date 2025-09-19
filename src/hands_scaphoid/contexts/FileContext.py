#!/usr/bin/env python3
"""
File context manager for hands-scaphoid package.

This module provides the FileContext class for managing file operations
with context manager support and hierarchical path resolution.

File:
    name: FileContext.py
    date: 2025-09-16

Description:
    File context manager for hierarchical file system operations

Authors: ["Andreas Häberle"]
"""

from pathlib import Path
from typing import Optional, List, TextIO
from .Context import Context
from .FileOperations import File
from .__base__ import PathLike, console


class FileContext(Context):
    """
    File context manager for hierarchical file system operations.

    This class allows you to work with files in a hierarchical context,
    providing convenient methods for reading, writing, and manipulating
    file content while maintaining awareness of the current directory context.

    The context manager automatically handles file handle management and
    delegates actual file operations to the File class.

    Example:
        with DirectoryContext('~/projects') as projects:
            with DirectoryContext('myproject') as project:
                with FileContext('README.md') as readme:
                    readme.add_heading('My Project')
                    readme.write_content('This is my project.')
    """

    def __init__(
        self,
        path: PathLike,
        create: bool = True,
        mode: str = "r+",
        encoding: str = "utf-8",
        dry_run: bool = False,
        enable_globals: bool = False,
    ):
        """
        Initialize a new FileContext.

        Args:
            path: The file path (relative or absolute)
            create: Whether to create the file if it doesn't exist (default: True)
            mode: File open mode (default: 'r+' for read/write)
            encoding: File encoding (default: 'utf-8')
            dry_run: Whether to simulate operations without making actual changes
            enable_globals: Whether to enable global function access within context
        """
        super().__init__(path, create, dry_run, enable_globals)
        self.mode = mode
        self.encoding = encoding
        self.file_handle: Optional[TextIO] = None
        self._content: Optional[str] = None

    def _create_path(self, resolved_path: Path) -> None:
        """
        Create the file if it doesn't exist.

        Args:
            resolved_path: The resolved absolute path to create
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would create file: {resolved_path}[/dim]")
            return

        File.create_file(resolved_path, create_dirs=True)

    def _enter_context(self, resolved_path: Path) -> None:
        """
        Open the file when entering the context.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would open file: {resolved_path}[/dim]")
            return

        try:
            # If file doesn't exist and we're in r+ mode, create it first
            if not resolved_path.exists() and "r" in self.mode:
                File.create_file(resolved_path, create_dirs=True)

            self.file_handle = open(resolved_path, self.mode, encoding=self.encoding)
            console.print(f"[green]Opened file:[/green] {resolved_path}")
        except Exception as e:
            console.print(f"[red]Error opening file {resolved_path}:[/red] {e}")
            raise

    def _exit_context(self, resolved_path: Path) -> None:
        """
        Close the file when exiting the context.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would close file: {resolved_path}[/dim]")
            return

        if self.file_handle:
            try:
                self.file_handle.close()
                console.print(f"[green]Closed file:[/green] {resolved_path}")
            except Exception as e:
                console.print(f"[red]Error closing file {resolved_path}:[/red] {e}")
                raise

    def write_line(self, content: str) -> "FileContext":
        """
        Write a line to the file with automatic newline.

        Args:
            content: Text content to write

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would append to file: {self.resolve_path()}[/dim]"
            )
            return self

        File.append_line(self.resolve_path(), content, create_dirs=False)
        return self

    def write_content(self, content: str) -> "FileContext":
        """
        Write content to the file without automatic newline.

        Args:
            content: Text content to write

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would append to file: {self.resolve_path()}[/dim]"
            )
            return self

        File.append_content(self.resolve_path(), content, create_dirs=False)
        return self

    def add_heading(self, title: str, level: int = 1) -> "FileContext":
        """
        Add a markdown-style heading to the file.

        Args:
            title: Heading text
            level: Heading level (1-6, default: 1)

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would append to file: {self.resolve_path()}[/dim]"
            )
            return self

        File.add_heading(self.resolve_path(), title, level, create_dirs=False)
        return self

    def read_content(self) -> str:
        """
        Read the entire file content.

        Returns:
            File content as string
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would read file: {self.resolve_path()}[/dim]"
            )
            return "[DRY RUN] File content would be read here"

        return File.read_content(self.resolve_path())

    def read_lines(self) -> List[str]:
        """
        Read all lines from the file.

        Returns:
            List of lines
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would read file: {self.resolve_path()}[/dim]"
            )
            return ["[DRY RUN] File lines would be read here"]

        return File.read_lines(self.resolve_path())

    def overwrite_content(self, content: str) -> "FileContext":
        """
        Overwrite the entire file content.

        Args:
            content: New content for the file

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would overwrite file: {self.resolve_path()}[/dim]"
            )
            return self

        File.write_content(self.resolve_path(), content, create_dirs=False)
        return self

    def overwrite_line(self, line: str) -> "FileContext":
        """
        Overwrite the entire file with a single line.

        Args:
            line: Line to write to the file

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would overwrite file: {self.resolve_path()}[/dim]"
            )
            return self

        File.write_line(self.resolve_path(), line, create_dirs=False)
        return self

    def copy_to(self, target_path: PathLike) -> "FileContext":
        """
        Copy this file to another location.

        Args:
            target_path: Target file path

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would copy file: {self.resolve_path()} → {target_path}[/dim]"
            )
            return self

        File.copy_file(self.resolve_path(), target_path, create_dirs=True)
        return self

    def get_file_size(self) -> int:
        """
        Get the size of the file in bytes.

        Returns:
            File size in bytes
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would get file size: {self.resolve_path()}[/dim]"
            )
            return 0

        return File.get_file_size(self.resolve_path())

    def file_exists(self) -> bool:
        """
        Check if the file exists.

        Returns:
            True if file exists, False otherwise
        """
        return File.file_exists(self.resolve_path())

    def delete(self) -> None:
        """
        Delete the file.

        Note: This will also exit the context as the file no longer exists.
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would delete file: {self.resolve_path()}[/dim]"
            )
            return

        # Close file handle before deletion
        if self.file_handle:
            self.file_handle.close()
            self.file_handle = None

        File.delete_file(self.resolve_path())
