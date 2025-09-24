"""
Generic directory commands.
----
file:
    name:        directory_commands.py
    uuid:        4936d833-c8d8-46d3-a967-2d480236d2f3
description:     directory commands
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""


from ..__base__ import (
    logger,
    # yes, no, 
    PathLike, Path
)
from ..objects import ObjectCore
from .core_commands import CompressionType, does_not_exists, ensure_path, exists, filter, is_directory, is_instance, is_variable

from typing import Optional, Any
from pathlib import Path
import os
import shutil
import inspect


logger.debug("Importing directory_commands module")


def get_current_directory() -> Path:
    """
    Get the current absolute path of this directory context.

    Returns:
        The absolute path of this directory
    """
    return Path(os.getcwd()).resolve()


def get_file_directory(script_file: Optional[PathLike] = None) -> Path:
    """
    Get the folder of the calling script.

    Args:
        script_file: Optional path to a script file. If None, uses the caller's __file__.

    Returns:
        The folder containing the script.
    """
    if script_file is None:
        # Get the caller's frame and extract __file__ from globals
        frame = inspect.stack()[1]
        caller_globals = frame.frame.f_globals
        script_file = caller_globals.get("__file__", os.getcwd())
    return Path(script_file).parent.resolve()



def list_contents(path: PathLike, filter_pattern: str = None) -> list[Path]:
    """
    List the contents of this directory.
    
    Args:
        path: Path to the directory
        filter_pattern: Optional glob pattern to filter results

    Returns:
        List of paths in this directory
    """
    path = ensure_path(path)
    path = path.resolve()
    item_list = []

    if exists(path) is False or not is_directory(path):
        return item_list

    try:
        if filter_pattern:
            item_list = filter(path, filter_pattern)
        else:
            item_list = list(path.iterdir())
        return item_list

    except PermissionError:
        logger.error(f"Permission denied listing directory: {path}")
        return []

    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")
        return []


def list_archives(path: PathLike, filter_pattern: str = None) -> list[Path]:
    """
    List archive files in this directory.


    Returns:
        List of archive file paths in this directory
    """
    path = ensure_path(path)
    archives = []
    if exists(path) is False or not is_directory(path):
        return archives
    
    try:
        archive_types = CompressionType.list_types()
        for item in path.iterdir():
            ext = item.suffix.lower()[1:]
            if item.is_file() and ext in archive_types:
                if filter_pattern is None or item.match(filter_pattern, case_sensitive=False):
                    archives.append(item)
    
    except PermissionError:
        logger.error(f"Permission denied listing directory: {path}")
    
    except Exception as e:
        logger.error(f"Error listing directory {path}: {e}")

    return archives


def create_directory(path: PathLike, 
                     name: str, 
                     exist_ok: bool = False, 
                     make_parents: bool = False) -> Path:
    """
    Create a subdirectory within this directory context.

    Args:
        path: Path to the parent directory
        name: Name of the subdirectory to create
        exist_ok: If True, do not raise an error if the directory already exists
        make_parents: If True, create parent directories as needed

    Returns:
        A new path instance for the subdirectory
    """
    path = path.resolve() / name

    os.mkdir(path, exist_ok=exist_ok, make_parents=make_parents)
    return Path(path)


def delete_directory(
    path: PathLike,
    name: str,
    recursive: bool = False,
    ignore_errors: bool = False,
    allow_empty: bool = False
) -> bool:
    """
    Delete a subdirectory within this directory context.

    Args:
        path (PathLike): Path to the parent directory
        name (str): Name of the subdirectory to delete
        recursive (bool): If True, delete non-empty directories recursively
        ignore_errors (bool): If True, ignore errors during deletion
        allow_empty (bool): If True, do not raise an error if the directory does not

    Returns:
        True if deleted successfully, False otherwise
    """
    subdir = path.resolve() / name
    if does_not_exists(subdir) or not is_directory(subdir):
        if not allow_empty:
            logger.error(f"Directory does not exist: {subdir}")
            
        return False

    try:
        subdir.rmdir() if not recursive else shutil.rmtree(subdir, ignore_errors=ignore_errors)
        logger.info(f"Deleted directory: {subdir}")
        return True
        
    except Exception as e:
        logger.error(f"Error deleting directory {subdir}: {e}")
    
    return False

# TODO: complete implement functions
# - TODO: cli for ls(all, recursive, filter) 