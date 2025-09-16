#!/usr/bin/env python3
"""
File operations module for hands-scaphoid package.

This module provides the File class for pure file operations
without context management.

File:
    name: FileOperations.py
    date: 2025-09-16

Description:
    Pure file operations class - no context management

Authors: ["Andreas Häberle"]
"""

from pathlib import Path
from typing import List, Optional, Union
from .__base__ import PathLike, console


class File:
    """
    Pure file operations class without context management.
    
    This class provides static methods for file operations that can be used
    independently of any context manager. All methods operate on explicit
    file paths and do not maintain any state.
    
    Example:
        # Direct file operations
        File.write_content(Path("config.txt"), "setting=value")
        content = File.read_content(Path("config.txt"))
        File.append_line(Path("log.txt"), "New log entry")
    """
    
    @staticmethod
    def read_content(file_path: PathLike) -> str:
        """
        Read the entire content of a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If lacking read permissions
        """
        path = Path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            console.print(f"[red]File not found:[/red] {path}")
            raise
        except PermissionError:
            console.print(f"[red]Permission denied reading file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error reading file {path}:[/red] {e}")
            raise
    
    @staticmethod
    def read_lines(file_path: PathLike) -> List[str]:
        """
        Read all lines from a file.
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            List of lines from the file
        """
        path = Path(file_path)
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return f.readlines()
        except FileNotFoundError:
            console.print(f"[red]File not found:[/red] {path}")
            raise
        except PermissionError:
            console.print(f"[red]Permission denied reading file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error reading file {path}:[/red] {e}")
            raise
    
    @staticmethod
    def write_content(file_path: PathLike, content: str, create_dirs: bool = True) -> None:
        """
        Write content to a file, replacing existing content.
        
        Args:
            file_path: Path to the file to write
            content: Content to write to the file
            create_dirs: Whether to create parent directories if they don't exist
            
        Raises:
            PermissionError: If lacking write permissions
        """
        path = Path(file_path)
        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            console.print(f"[green]Wrote content to file:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied writing file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error writing file {path}:[/red] {e}")
            raise
    
    @staticmethod
    def append_content(file_path: PathLike, content: str, create_dirs: bool = True) -> None:
        """
        Append content to a file.
        
        Args:
            file_path: Path to the file to append to
            content: Content to append to the file
            create_dirs: Whether to create parent directories if they don't exist
        """
        path = Path(file_path)
        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(path, 'a', encoding='utf-8') as f:
                f.write(content)
                
            console.print(f"[green]Appended content to file:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied writing file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error writing file {path}:[/red] {e}")
            raise
    
    @staticmethod
    def write_line(file_path: PathLike, line: str, create_dirs: bool = True) -> None:
        """
        Write a line to a file, replacing existing content.
        
        Args:
            file_path: Path to the file to write
            line: Line to write to the file (newline will be added)
            create_dirs: Whether to create parent directories if they don't exist
        """
        content = line if line.endswith('\n') else line + '\n'
        File.write_content(file_path, content, create_dirs)
    
    @staticmethod
    def append_line(file_path: PathLike, line: str, create_dirs: bool = True) -> None:
        """
        Append a line to a file.
        
        Args:
            file_path: Path to the file to append to
            line: Line to append to the file (newline will be added)
            create_dirs: Whether to create parent directories if they don't exist
        """
        content = line if line.endswith('\n') else line + '\n'
        File.append_content(file_path, content, create_dirs)
    
    @staticmethod
    def add_heading(file_path: PathLike, title: str, level: int = 1, create_dirs: bool = True) -> None:
        """
        Append a markdown-style heading to a file.
        
        Args:
            file_path: Path to the file to append to
            title: Heading text
            level: Heading level (1-6)
            create_dirs: Whether to create parent directories if they don't exist
        """
        if not 1 <= level <= 6:
            raise ValueError("Heading level must be between 1 and 6")
        
        heading = '#' * level + ' ' + title + '\n'
        File.append_content(file_path, heading, create_dirs)
    
    @staticmethod
    def create_file(file_path: PathLike, create_dirs: bool = True) -> None:
        """
        Create an empty file.
        
        Args:
            file_path: Path to the file to create
            create_dirs: Whether to create parent directories if they don't exist
        """
        path = Path(file_path)
        try:
            if create_dirs:
                path.parent.mkdir(parents=True, exist_ok=True)
            
            path.touch()
            console.print(f"[green]Created file:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied creating file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error creating file {path}:[/red] {e}")
            raise
    
    @staticmethod
    def file_exists(file_path: PathLike) -> bool:
        """
        Check if a file exists.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file exists and is a file, False otherwise
        """
        path = Path(file_path)
        return path.exists() and path.is_file()
    
    @staticmethod
    def get_file_size(file_path: PathLike) -> int:
        """
        Get the size of a file in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes
            
        Raises:
            FileNotFoundError: If the file doesn't exist
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")
        return path.stat().st_size
    
    @staticmethod
    def copy_file(source_path: PathLike, target_path: PathLike, create_dirs: bool = True) -> None:
        """
        Copy a file from source to target.
        
        Args:
            source_path: Path to the source file
            target_path: Path to the target file
            create_dirs: Whether to create target parent directories if they don't exist
        """
        import shutil
        
        source = Path(source_path)
        target = Path(target_path)
        
        if not source.exists():
            raise FileNotFoundError(f"Source file not found: {source}")
        
        try:
            if create_dirs:
                target.parent.mkdir(parents=True, exist_ok=True)
            
            shutil.copy2(source, target)
            console.print(f"[green]Copied file:[/green] {source} → {target}")
        except PermissionError:
            console.print(f"[red]Permission denied copying file:[/red] {source} → {target}")
            raise
        except Exception as e:
            console.print(f"[red]Error copying file {source} → {target}:[/red] {e}")
            raise
    
    @staticmethod
    def delete_file(file_path: PathLike) -> None:
        """
        Delete a file.
        
        Args:
            file_path: Path to the file to delete
            
        Raises:
            FileNotFoundError: If the file doesn't exist
            PermissionError: If lacking delete permissions
        """
        path = Path(file_path)
        try:
            if not path.exists():
                raise FileNotFoundError(f"File not found: {path}")
            
            path.unlink()
            console.print(f"[green]Deleted file:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied deleting file:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error deleting file {path}:[/red] {e}")
            raise