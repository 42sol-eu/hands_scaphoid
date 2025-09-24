"""
core commands for package.

This module contains core command functions used throughout the package.
----
file:
    name:        core_commands.py  
    uuid:        d71b08ee-39a3-409a-b8d2-412899dac67c
description:     core_commands init
authors:         felix@42sol.eu
project:
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
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
from shutil import which as shutil_which
from typing import Any, Dict, List, Optional

logger.debug("Importing core_commands module")

class CompressionType(str, Enum):
    """
    Enumeration of supported compression types.
    """
    ZIP = "zip"
    TAR = "tar"
    GZIP = "gzip"
    GZ = "gz"
    BZIP2 = "bzip2"
    XZ = "xz"
    SEVEN_Z = "7z"
    RAR = "rar"
    TAR_GZ = "tar.gz"
    TAR_BZ2 = "tar.bz2"
    TAR_XZ = "tar.xz"
    UNKNOWN = "UNKNOWN"

    @staticmethod
    def list_types() -> List[str]:
        """
        List all supported compression types.
        Returns:
            List of supported compression type strings.
        """
        types = [ct.value for ct in CompressionType]
        types.remove(CompressionType.UNKNOWN.value)
        return types

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