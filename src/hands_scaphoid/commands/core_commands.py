"""
Core commands for package.

This module contains core command functions used throughout the package.
---yaml
File:
    name:        core_commands.py  
    uuid:        d71b08ee-39a3-409a-b8d2-412899dac67c

Description:     core_commands init

Project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid


Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

import os
from ..__base__ import (
    # console, 
    # yes, no, true, false, 
    # DEBUG_MODE,
    logger,
    PathLike, Path
)
from ..objects import ObjectCore
from enum import Enum
from dataclasses import dataclass
from shutil import which as shutil_which
from typing import Any, Dict, List, Optional

logger.debug("Importing core_commands module")


@dataclass
class ArchiveHandler:
    extract: callable
    pack: callable
    test: callable
    list_files: callable

class DynamicArchiveType:
    """A registry like enum replacement that can be extended at runtime.
    Also getting an archive handler for the core functions.
    """
    _next_id: int = 1
    _members:           Dict[str, int] = {}
    _extensions:        Dict[str, str] = {}
    _handler:           Dict[str, ArchiveHandler] = {}

    @classmethod
    def get_next_identifier(cls):
        the_id = cls._next_id 
        cls._next_id += 1
        return the_id 
    
    def __init__(self, name: str):
        if name in self.__class__._members:
            raise ValueError(f'{name} already defined in {self.__class__}')
        self.name  = name
        self.value = DynamicArchiveType.get_next_identifier()
        self.__class__._members[self.name] = self.value
        
    
    @classmethod 
    def get(cls, name: str) -> "DynamicArchiveType":
        """get a member (suffix) by name."""
        if name not in cls._members:
            raise ValueError(f'{name} [red]not[/red] defined in {cls.__class__}')
        return cls._members[name]

    @classmethod 
    def get_suffix(cls, name: str) -> "DynamicArchiveType":
        """get a member (suffix) by name."""
        if name not in cls._extensions:
            raise ValueError(f'Extension for {name} [red]not[/red] defined in {cls.__class__}')
        return cls._extensions[name]

    @classmethod 
    def get_handler(cls, name: str) -> "ArchiveHandler":
        """get an archive handler for the archive type."""
        if name not in cls._handler:
            raise ValueError(f'ArchiveHandler for {name} [red]not[/red] defined in {cls.__class__}')
        return cls._handler[name]
    
    @classmethod
    def add(cls, name: str, extension: str, handler: ArchiveHandler=None) -> bool:
        if name in cls._members:
            raise ValueError(f'{name} is already defined in {cls.__class__}')

        cls._members[name] = cls.get_next_identifier()
        cls._extensions[name] = extension
        cls._handler[name] = handler
        
        return True

    @classmethod
    def add_similar(cls, name: str, extension: str, similar_name: str) -> bool:
        """Add an archive type that reuses an already defined archive handler."""
        if similar_name not in cls._members:
            raise ValueError(f'The {similar_name} is not defined in {cls.__class__}')

        cls._members[name] = cls.get_next_identifier()
        cls._extensions[name] = extension
        cls._handler[name] = cls._handler[similar_name]

        return True
        
    @classmethod
    def items(cls) -> Dict[str, "DynamicArchiveType"]:
        return dict(cls._members)    
    
    @classmethod
    def list_types(cls) -> List[str]:
        """
        List all supported compression types.
        Returns:
            List of supported compression type strings.
        """        
        return list(cls.items().keys())

    @classmethod
    def list_extensions(cls) -> List[str]:
        """
        List all supported compression type extensions.
        Returns:
            List of supported compression type extension strings.
        """        
        return list(cls._extensions.values())

    @classmethod
    def list_types(cls) -> List[str]:
        """
        List all supported compression types.
        
        Returns:
            List of supported compression type strings.
        """        
        return list(cls._members.keys())


# Import the centralized archive registry
from .archive_registry import ArchiveType


# DynamicArchiveType and ArchiveType replaces `class CompressionType(str, Enum)`. It is user extensible at runtime.

# Backward compatibility alias
CompressionType = DynamicArchiveType


def does_not_exists(path: PathLike) -> bool:
    """
    Check if a path does not exist.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object does not exist, False otherwise.
    """
    return not Path(path).exists()


def exists(path: PathLike) -> bool:
    """
    Check if a path exists.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object exists, False otherwise.
    """
    if path is None:
        return False
    return Path(path).exists()


def ensure_path(path: Any) -> Path:
    """
    Ensure the path is a Path object.

    Args:
        path (Any): The path to ensure.
    Returns:
        Path: The ensured Path object.
    """
    if is_invalid(path):
        return False

    if is_instance(path, Path):
        return path
    elif is_instance(path, str):
        return Path(path)
    elif is_instance(path, ObjectCore):
        path = path.name
    elif is_variable(path):
        path = str(os.environ.get(str(path), path))
    return Path(str(path)) # TODO: does this work with Any?


def filter(path: PathLike, filter: str) -> List:
    """
    Filter out None values from a list.
    Args:
        path (PathLike): The list to filter.
        filter (str): The filter pattern (e.g., "*.txt").
    Returns:
        List: The filtered list.
    """
    item_list = []
    p = ensure_path(path)
    if not p.is_dir():
        return item_list
    
    for item in p.glob(filter):
        item_list.append(item)
        
    return item_list

def is_invalid(path: PathLike) -> bool:
    """
    Check if a path is invalid (None or empty string).

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is invalid, False otherwise.
    """
    if path is None:
        return True
    if (is_instance(path, str) or is_instance(path, Path)) and str(path).strip() == "":
        return True
    if  is_instance(path, int) or is_instance(path, float) or is_instance(path, bool):
        return True
    
    return False

def is_object(path: PathLike) -> bool:
    """
    Check if a path is a file or directory.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a file or directory, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)
    return p.is_file() or p.is_dir() or p.is_symlink()

def is_directory(path: PathLike) -> bool:
    """
    Check if a path is a directory.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a directory, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)
    return p.is_dir()

def is_file(path: PathLike) -> bool:
    """
    Check if a path is a file.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a file, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)  
    return p.is_file()

def is_link(path: PathLike) -> bool:
    """
    Check if a path is a symbolic link.

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a symbolic link, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)
    return p.is_symlink()

def is_variable(name: str) -> bool:
    """
    Check if a variable is defined (not None).

    Args:
        name (str): The variable to check.
    Returns:
        bool: True if the variable is defined, False otherwise.
    """
    if not is_instance(name, str):
        return False

    value = os.getenv(key=name, default=None)
    if value:
        return True
    return False

is_instance = isinstance

def is_item(p: PathLike) -> bool:
    """
    Check if a path is a file, directory, or symbolic link.

    Args:
        p (PathLike): The path to check.
    Returns:
        bool: 
        - True if the object is a object or item (variable), 
        - False otherwise
    """
    if is_invalid(p):
        return False
    
    if is_object(p): 
        return True

    if is_instance(p, Path):
        return False
    return is_variable(p)

def is_git_project(path: PathLike) -> bool:
    """
    Check if a path is a project directory (contains a .git folder).

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a project directory, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)
    return p.is_dir() and (p / ".git").exists()

def is_vscode_project(path: PathLike) -> bool:
    """
    Check if a path is a VSCode project directory (contains a .vscode folder).

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a VSCode project directory, False otherwise.
    """
    if is_invalid(path):
        return False

    p = Path(path)
    return p.is_dir() and (p / ".vscode").exists()

def is_hands_project(path: PathLike) -> bool:
    """
    Check if a path is a Hands project directory (contains a .hands folder).

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a Hands project directory, False otherwise.
    """
    if is_invalid(path):
        return False
    
    p = Path(path)
    return p.is_dir() and (p / ".hands").exists()

def is_project(path: PathLike) -> bool:
    """
    Check if a path is a project directory (contains a .git or .vscode folder).

    Args:
        path (PathLike): The path to check.
    Returns:
        bool: True if the object is a project directory, False otherwise.
    """
    p = Path(path)
    return is_git_project(p) or is_hands_project(p) or is_vscode_project(p)

def get_file_extension(filename: PathLike) -> str:
    """
    Get the file extension from a filename.

    Also supports double extensions like .tar.gz and modern graphical extensions like .drawio.png.

    Args:
        filename (str): The name of the file.
    Returns:
        str: The file extension, or an empty string if none exists.
    """
    if is_instance(filename, Path):
        filename = str(filename)
    filename = filename.lower()

    if filename.count(".") == 0:
        # no extension
        return ""

    if filename.count(".") == 1 and filename.find(".") == 0:
        # hidden file with no extension
        return ""

    parts = filename.rsplit(".")
    if len(parts) == 0:
        return ""

    extension = parts[-1]

    #!md|# Handle double extensions
    if len(parts) > 2:
        #!md|- Archive  extensions like .tar.gz
        if extension in ["gz", "bz2", "xz", "zip"] and len(parts) > 2 and parts[-2] == "tar":
            extension = "tar.gz"

        #!md|# Handle modern graphical extensions
        #!md|- Excalidraw and Draw.io use double extensions
        if extension in ["png", "svg"] and len(parts) > 2:
            extension = f"{parts[-2]}.{extension}"

    return extension


def which( executable: PathLike ) -> PathLike:
    """
    Locate a command.

    Args:
        executable (PathLike): The name of the executable to find.
    Returns:
        PathLike: The path to the executable, or None if not found.
    """

    path = shutil_which(executable)
    if path is None:
        return None
    return Path(path).resolve()

# TODO: more commands e.g. change_modifiers, change_owner, change_group, change, is_executable
# TODO: implement dry_run decorator in base_decorators.py
# - TODO: def count( name: PathLike, count=CountType)
# - TODO: CountType (characters, words, lines, pattern (regex) bytes )
# - TODO: cli for count() and wc()
# - TODO: cli for chmod, chown, sudo, 