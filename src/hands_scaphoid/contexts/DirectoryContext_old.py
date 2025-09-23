#!/usr/bin/env python3
"""
Directory module for hands-scaphoid package.

This module provides the Directory class for managing directory operations
with context manager support and hierarchical path resolution.
----
File:
    name: DirectoryContext.py
    uuid: 3908677f-4768-4b9b-9b8c-74cd0842a5b7
    date: 2025-09-16

authors: ["Andreas Häberle"]
description:
    Directory context manager for hierarchical file system operations

"""

from pathlib import Path
from typing import Optional, Union, List, Any
from .contexts.Context import Context
from .__base__ import PathLike, os, console


class DirectoryCore(Context):
    """
    Directory context manager for hierarchical file system operations.

    This class allows you to work with directories in a hierarchical context,
    automatically changing the working directory when entering the context
    and restoring it when exiting.

    Example:
        with DirectoryCore('~') as home:
            with DirectoryCore('projects') as projects:
                # Now working in ~/projects
                with DirectoryCore('myproject') as project:
                    # Now working in ~/projects/myproject
                    pass
    """

    def __init__(
        self,
        path: PathLike,
        create: bool = True,
        dry_run: bool = False,
        enable_globals: bool = False,
    ):
        """
        Initialize a new Directory context.

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

        try:
            resolved_path.mkdir(parents=True, exist_ok=True)
            console.print(f"[green]Created directory:[/green] {resolved_path}")
        except PermissionError:
            console.print(
                f"[red]Permission denied creating directory:[/red] {resolved_path}"
            )
            raise
        except Exception as e:
            console.print(f"[red]Error creating directory {resolved_path}:[/red] {e}")
            raise

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

        if not resolved_path.exists():
            raise FileNotFoundError(f"Directory does not exist: {resolved_path}")

        if not resolved_path.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {resolved_path}")

        # Store current working directory
        self.previous_cwd = Path.cwd()

        # Change to the new directory
        try:
            os.chdir(resolved_path)
            console.print(f"[blue]Changed to directory:[/blue] {resolved_path}")
        except PermissionError:
            console.print(
                f"[red]Permission denied accessing directory:[/red] {resolved_path}"
            )
            raise
        except Exception as e:
            console.print(
                f"[red]Error changing to directory {resolved_path}:[/red] {e}"
            )
            raise

    def _exit_context(self, resolved_path: Path) -> None:
        """
        Restore the previous working directory when exiting the context.

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
                # Don't raise here as we're exiting

    def get_current_path(self) -> Path:
        """
        Get the current absolute path of this directory context.

        Returns:
            The absolute path of this directory
        """
        return self.resolve_path()

    def list_files(self) -> List[Path]:
        """
        List the contents of this directory.

        Returns:
            List of paths in this directory
        """
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would list contents of: {self.resolve_path()}[/dim]"
            )
            return []

        if not self._entered:
            # If not in context, list the resolved path
            path = self.resolve_path()
        else:
            # If in context, list current directory
            path = Path.cwd()

        try:
            return list(path.iterdir())
        except PermissionError:
            console.print(f"[red]Permission denied listing directory:[/red] {path}")
            return []
        except Exception as e:
            console.print(f"[red]Error listing directory {path}:[/red] {e}")
            return []

    def list_contents(self) -> List[Path]:
        """
        List the contents of this directory (alias for list_files).

        Returns:
            List of paths in this directory
        """
        return self.list_files()

    def create_subdirectory(self, name: str) -> "Directory":
        """
        Create a subdirectory within this directory context.

        Args:
            name: Name of the subdirectory to create

        Returns:
            A new Directory instance for the subdirectory
        """
        return DirectoryCore(name, create=True, dry_run=self.dry_run)

    def create_directory(self) -> "Directory":
        """
        Create this directory if it doesn't exist (standalone method).

        Returns:
            Self for method chaining
        """
        resolved_path = self.resolve_path()
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would create directory: {resolved_path}[/dim]"
            )
        elif not resolved_path.exists():
            self._create_path(resolved_path)
        return self

    def exists(self) -> bool:
        """
        Check if this directory exists.

        Returns:
            True if the directory exists, False otherwise
        """
        return self.resolve_path().exists()

    def delete(self) -> "Directory":
        """
        Delete this directory (standalone method).

        Returns:
            Self for method chaining
        """
        resolved_path = self.resolve_path()
        if self.dry_run:
            console.print(
                f"[dim][DRY RUN] Would delete directory: {resolved_path}[/dim]"
            )
        elif resolved_path.exists():
            try:
                if resolved_path.is_dir():
                    import shutil

                    shutil.rmtree(resolved_path)
                    console.print(f"[red]Deleted directory:[/red] {resolved_path}")
                else:
                    console.print(
                        f"[yellow]Warning: Path is not a directory:[/yellow] {resolved_path}"
                    )
            except Exception as e:
                console.print(
                    f"[red]Error deleting directory {resolved_path}:[/red] {e}"
                )
                raise
        return self

    def __truediv__(self, other: Union[str, Path]) -> Path:
        """
        Allow path joining with the / operator.

        Args:
            other: Path component to join

        Returns:
            Combined path
        """
        return self.resolve_path() / other
