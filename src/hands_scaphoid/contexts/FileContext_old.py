#!/usr/bin/env python3
"""
File module for hands-scaphoid package.

This module provides the File class for managing file operations
with context manager support and hierarchical path resolution.

File:
    name: File.py
    date: 2025-09-16

Description:
    File context manager for hierarchical file system operations

Authors: ["Andreas Häberle"]
"""

from pathlib import Path
from typing import Optional, List, TextIO
from .contexts.Context import Context
from .__base__ import PathLike, console


class FileCore(Context):
    """
    File context manager for hierarchical file system operations.

    This class allows you to work with files in a hierarchical context,
    providing convenient methods for reading, writing, and manipulating
    file content while maintaining awareness of the current directory context.

    Example:
        with DirectoryCore('~') as home:
            with DirectoryCore('projects') as projects:
                with FileCore('README.md') as readme:
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
        Initialize a new File context.

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

        try:
            # Create parent directories if they don't exist
            resolved_path.parent.mkdir(parents=True, exist_ok=True)

            # Create empty file if it doesn't exist
            if not resolved_path.exists():
                resolved_path.touch()
                console.print(f"[green]Created file:[/green] {resolved_path}")
        except PermissionError:
            console.print(
                f"[red]Permission denied creating file:[/red] {resolved_path}"
            )
            raise
        except Exception as e:
            console.print(f"[red]Error creating file {resolved_path}:[/red] {e}")
            raise

    def _enter_context(self, resolved_path: Path) -> None:
        """
        Open the file when entering the context.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would open file: {resolved_path}[/dim]")
            self._content = ""  # Initialize content for dry run
            return

        if not resolved_path.exists():
            raise FileNotFoundError(f"File does not exist: {resolved_path}")

        if not resolved_path.is_file():
            raise IsADirectoryError(f"Path is not a file: {resolved_path}")

        try:
            # Adjust mode if file is empty and we're in r+ mode
            if self.mode == "r+" and resolved_path.stat().st_size == 0:
                # For empty files, use w+ to avoid issues with r+
                self.file_handle = open(resolved_path, "w+", encoding=self.encoding)
            else:
                self.file_handle = open(
                    resolved_path, self.mode, encoding=self.encoding
                )

            # Read current content
            self.file_handle.seek(0)
            self._content = self.file_handle.read()

            console.print(f"[blue]Opened file:[/blue] {resolved_path}")
        except PermissionError:
            console.print(f"[red]Permission denied opening file:[/red] {resolved_path}")
            raise
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

        if self.file_handle and not self.file_handle.closed:
            try:
                # Write any pending content
                if self._content is not None:
                    self.file_handle.seek(0)
                    self.file_handle.write(self._content)
                    self.file_handle.truncate()

                self.file_handle.close()
                console.print(f"[blue]Closed file:[/blue] {resolved_path}")
            except (PermissionError, OSError, IOError) as e:
                console.print(f"[red]Error closing file {resolved_path}:[/red] {e}")
                # Don't raise here as we're exiting

    def read_content(self) -> str:
        """
        Read the current content of the file.

        Returns:
            The file content as a string
        """
        if self._content is not None:
            return self._content

        if not self._entered:
            # If not in context, read directly from file
            resolved_path = self.resolve_path()
            try:
                with open(resolved_path, "r", encoding=self.encoding) as f:
                    return f.read()
            except (PermissionError, OSError, IOError) as e:
                console.print(f"[red]Error reading file {resolved_path}:[/red] {e}")
                return ""

        return ""

    def write_content(self, content: str, append: bool = False) -> "File":
        """
        Write content to the file.

        Args:
            content: Content to write
            append: Whether to append to existing content (default: False)

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            action = "append to" if append else "write to"
            console.print(
                f"[dim][DRY RUN] Would {action} file: {self.resolve_path()}[/dim]"
            )
            return self

        if not self._entered:
            # Standalone mode - read current content, modify, and write back
            resolved_path = self.resolve_path()
            try:
                if resolved_path.exists():
                    current_content = resolved_path.read_text(encoding=self.encoding)
                else:
                    current_content = ""

                if append:
                    new_content = current_content + content
                else:
                    new_content = content

                # Create parent directories if needed
                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                resolved_path.write_text(new_content, encoding=self.encoding)
                console.print(f"[green]Updated file:[/green] {resolved_path}")
            except Exception as e:
                console.print(f"[red]Error writing to file {resolved_path}:[/red] {e}")
                raise
        else:
            # Context mode
            if append and self._content:
                self._content += content
            else:
                self._content = content

        return self

    def append_content(self, content: str) -> "File":
        """
        Append content to the file.

        Args:
            content: Content to append

        Returns:
            Self for method chaining
        """
        return self.write_content(content, append=True)

    def write_line(self, line: str) -> "File":
        """
        Add a line to the file.

        Args:
            line: Line to add (newline will be appended if not present)

        Returns:
            Self for method chaining
        """
        if not line.endswith("\n"):
            line += "\n"
        return self.append_content(line)

    def add_line(self, line: str) -> "File":
        """
        Add a line to the file (alias for write_line).

        Args:
            line: Line to add (newline will be appended if not present)

        Returns:
            Self for method chaining
        """
        return self.write_line(line)

    def add_heading(self, heading: str, level: int = 1) -> "File":
        """
        Add a markdown heading to the file.

        Args:
            heading: The heading text
            level: Heading level (1-6, default: 1)

        Returns:
            Self for method chaining
        """
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")

        prefix = "#" * level
        heading_line = f"{prefix} {heading}\n\n"
        return self.append_content(heading_line)

    def get_lines(self) -> List[str]:
        """
        Get the file content as a list of lines.

        Returns:
            List of lines in the file
        """
        content = self.read_content()
        return content.splitlines()

    def insert_line_at(self, line_number: int, content: str) -> "File":
        """
        Insert a line at a specific line number.

        Args:
            line_number: Line number to insert at (0-based)
            content: Content to insert

        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would insert line at {line_number}: {content[:50]}...[/dim]"
            )
            return self

        if not self._entered:
            # Standalone mode
            resolved_path = self.resolve_path()
            try:
                if resolved_path.exists():
                    current_content = resolved_path.read_text(encoding=self.encoding)
                    lines = current_content.splitlines()
                else:
                    lines = []

                if not content.endswith("\n"):
                    content += "\n"

                lines.insert(line_number, content.rstrip("\n"))
                new_content = "\n".join(lines)
                if new_content and not new_content.endswith("\n"):
                    new_content += "\n"

                resolved_path.parent.mkdir(parents=True, exist_ok=True)
                resolved_path.write_text(new_content, encoding=self.encoding)
                console.print(f"[green]Inserted line in file:[/green] {resolved_path}")
            except Exception as e:
                console.print(
                    f"[red]Error inserting line in file {resolved_path}:[/red] {e}"
                )
                raise
        else:
            # Context mode
            lines = self.get_lines()
            if not content.endswith("\n"):
                content += "\n"

            lines.insert(line_number, content.rstrip("\n"))
            self._content = "\n".join(lines)
            if self._content and not self._content.endswith("\n"):
                self._content += "\n"

        return self

    def get_size(self) -> int:
        """
        Get the size of the file in bytes.

        Returns:
            File size in bytes
        """
        resolved_path = self.resolve_path()
        try:
            return resolved_path.stat().st_size
        except (PermissionError, OSError, IOError):
            return 0

    def exists(self) -> bool:
        """
        Check if the file exists.

        Returns:
            True if the file exists, False otherwise
        """
        return self.resolve_path().exists()

    def create_file(self) -> "File":
        """
        Create this file if it doesn't exist (standalone method).

        Returns:
            Self for method chaining
        """
        resolved_path = self.resolve_path()
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would create file: {resolved_path}[/dim]")
        elif not resolved_path.exists():
            self._create_path(resolved_path)
        return self

    def delete(self) -> "File":
        """
        Delete this file (standalone method).

        Returns:
            Self for method chaining
        """
        resolved_path = self.resolve_path()
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would delete file: {resolved_path}[/dim]")
        elif resolved_path.exists():
            try:
                resolved_path.unlink()
                console.print(f"[red]Deleted file:[/red] {resolved_path}")
            except Exception as e:
                console.print(f"[red]Error deleting file {resolved_path}:[/red] {e}")
                raise
        return self
