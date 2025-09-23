#!/usr/bin/env python3
"""
Context module for hands-scaphoid package.

This module provides the base Context class for managing hierarchical file system operations
with context manager support and global function access.
----
file:
    name: ContextCore.py
    uuid: 1f31a384-f5c2-4b7b-a755-f0caffaff1f4
    date: 2025-09-16
description:
    Base context manager for hierarchical file system operations
authors: ["Andreas Häberle"]
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid

"""

from pathlib import Path
from typing import Optional, Union, List, Any, Dict
from abc import ABC, abstractmethod
import threading
import builtins
from ..__base__ import PathLike, os, console


class Context(ABC):
    """
    Base context manager class for hierarchical file system operations.

    This class provides the foundation for managing nested context operations
    where each context maintains awareness of its parent and can resolve
    paths relative to the current working context.
    """

    # Thread-local storage for the context stack
    _context_stack = threading.local()

    def __init__(
        self,
        path: PathLike,
        create: bool = False,
        dry_run: bool = False,
        enable_globals: bool = False,
    ):
        """
        Initialize a new context.

        Args:
            path: The path for this context (relative or absolute)
            create: Whether to create the path if it doesn't exist
            dry_run: Whether to simulate operations without making actual changes
            enable_globals: Whether to enable global function access
        """
        self.path = Path(path).expanduser()
        self.create = create
        self.dry_run = dry_run
        self.enable_globals = enable_globals
        self.parent_context: Optional["Context"] = None
        self.original_cwd: Optional[Path] = None
        self._entered = False
        self._original_globals: Dict[str, Any] = {}

    @classmethod
    def _get_context_stack(cls) -> List["Context"]:
        """Get the current thread's context stack."""
        if not hasattr(cls._context_stack, "stack"):
            cls._context_stack.stack = []
        return cls._context_stack.stack

    @classmethod
    def get_current_context(cls) -> Optional["Context"]:
        """Get the current active context."""
        stack = cls._get_context_stack()
        return stack[-1] if stack else None

    def resolve_path(self) -> Path:
        """
        Resolve the absolute path for this context.

        Returns:
            The absolute path, taking into account parent contexts
        """
        if self.path.is_absolute():
            return self.path

        # If we have a parent context, resolve relative to it
        current_context = self.get_current_context()
        if current_context and current_context != self:
            return current_context.resolve_path() / self.path

        # Otherwise resolve relative to current working directory
        return Path.cwd() / self.path

    def __enter__(self):
        """Enter the context manager."""
        if self._entered:
            raise RuntimeError("Context is already entered")

        stack = self._get_context_stack()
        self.parent_context = stack[-1] if stack else None

        # Store original working directory if this is the first context
        if not stack:
            self.original_cwd = Path.cwd()

        # Resolve the absolute path
        resolved_path = self.resolve_path()

        # Create the path if requested and it doesn't exist
        if self.create and not resolved_path.exists():
            if not self.dry_run:
                self._create_path(resolved_path)
            else:
                console.print(
                    f"[dim][DRY RUN] Would create path: {resolved_path}[/dim]"
                )

        # Add this context to the stack
        stack.append(self)
        self._entered = True

        # Set up global functions if enabled
        if self.enable_globals:
            self._setup_global_functions()

        # Perform context-specific enter operations
        if not self.dry_run:
            self._enter_context(resolved_path)
        else:
            console.print(f"[dim][DRY RUN] Would enter context: {resolved_path}[/dim]")

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the context manager."""
        if not self._entered:
            return

        stack = self._get_context_stack()
        if not stack or stack[-1] != self:
            raise RuntimeError("Context exit order mismatch")

        # Perform context-specific exit operations
        resolved_path = self.resolve_path()
        if not self.dry_run:
            self._exit_context(resolved_path)
        else:
            console.print(f"[dim][DRY RUN] Would exit context: {resolved_path}[/dim]")

        # Remove this context from the stack
        stack.pop()
        self._entered = False

        # Clean up global functions if enabled
        if self.enable_globals:
            self._cleanup_global_functions()

        # If this was the last context, restore original working directory
        if not stack and self.original_cwd:
            os.chdir(self.original_cwd)

    @abstractmethod
    def _create_path(self, resolved_path: Path) -> None:
        """
        Create the path for this context.

        Args:
            resolved_path: The resolved absolute path to create
        """
        pass

    @abstractmethod
    def _enter_context(self, resolved_path: Path) -> None:
        """
        Perform context-specific operations when entering.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        pass

    @abstractmethod
    def _exit_context(self, resolved_path: Path) -> None:
        """
        Perform context-specific operations when exiting.

        Args:
            resolved_path: The resolved absolute path for this context
        """
        pass

    def __str__(self) -> str:
        """String representation of the context."""
        return f"{self.__class__.__name__}({self.path})"

    def __repr__(self) -> str:
        """Detailed string representation of the context."""
        return f"{self.__class__.__name__}(path={self.path!r}, create={self.create}, dry_run={self.dry_run})"

    def _setup_global_functions(self):
        """Setup global functions for this context type."""
        import builtins

        # Store original values before overriding
        for attr_name in dir(self):
            if not attr_name.startswith("_"):
                attr = getattr(self, attr_name)
                if callable(attr):
                    # Store original value if it exists
                    if hasattr(builtins, attr_name):
                        self._original_globals[attr_name] = getattr(builtins, attr_name)
                    # Set the global function
                    setattr(builtins, attr_name, attr)

    def _cleanup_global_functions(self):
        """Cleanup global functions set by this context."""
        import builtins

        for attr_name in dir(self):
            if not attr_name.startswith("_"):
                attr = getattr(self, attr_name)
                if callable(attr):
                    if attr_name in self._original_globals:
                        # Restore original value
                        setattr(builtins, attr_name, self._original_globals[attr_name])
                    else:
                        # Remove the attribute if it didn't exist before
                        if hasattr(builtins, attr_name):
                            delattr(builtins, attr_name)
