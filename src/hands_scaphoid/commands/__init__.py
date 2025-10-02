"""
Init hands_scaphoid/commands module for package.

This module contains command functions used throughout the package.
----
file:
    name:       __init__.py
    uuid:       c7151963-72d1-4661-bec3-accb29f39c85
    date:       
description:    init commands
authors:        felix@42sol.eu
project:
    name:       hands_scaphoid
    uuid:       2945ba3b-2d66-4dff-b898-672c386f03f4
    url:        https://github.com/42sol-eu/hands_scaphoid
"""

from hands_scaphoid.commands.core_commands import (
    exists,
    get_file_extension,
    is_directory,
    is_file,
    is_git_project,
    is_hands_project,
    is_instance,
    is_item,
    is_link,
    is_object,
    is_variable,
    is_vscode_project,
)

from .archive_commands import (
    create,
    extract,
)
from .directory_commands import (
    create_directory,
    delete_directory,
    list_archives,
    list_contents,
)

# Individual class imports for backward compatibility
from .handlers.ArchiveHandler import ArchiveHandler
from .archive_registry import DynamicArchiveType

# Handler pattern classes
from .handlers.Handler import Handler
from .handlers.FileHandler import FileHandler
from .handlers.files.TextFileHandler import TextFileHandler
from .handlers.files.JsonFileHandler import JsonFileHandler
from .handlers.DirectoryHandler import DirectoryHandler
from .handlers.directories.GitProjectHandler import GitProjectHandler
from .handlers.directories.PythonProjectHandler import PythonProjectHandler
from .handlers.files.ExecutableHandler import ExecutableHandler
from .handlers.files.PythonScriptHandler import PythonScriptHandler
from .handlers.HandlerRegistry import (
    HandlerRegistry,
    create_file_handler_registry,
    create_directory_handler_registry,
    create_executable_handler_registry,
    get_file_handler_registry,
    get_directory_handler_registry,
    get_executable_handler_registry,
)

# Archive handler classes
from .handlers.archives.ZipArchiveHandler import ZipArchiveHandler
from .handlers.archives.TarArchiveHandler import TarArchiveHandler
from .handlers.archives.SevenZipArchiveHandler import SevenZipArchiveHandler
from .handlers.directories.AppBundleHandler import AppBundleHandler
from .handlers.archives.WheelArchiveHandler import WheelArchiveHandler
from .handlers.files.OfficeDocumentHandler import OfficeDocumentHandler


# %% [Exports]
__all__ = [
    # Core functions
    "exists",
    "get_file_extension",
    "is_directory",
    "is_file",
    "is_git_project",
    "is_hands_project",
    "is_instance",
    "is_item",
    "is_link",
    "is_object",
    "is_variable",
    "is_vscode_project",
    "create",  # archive_commands.py
    "extract",  # archive_commands.py
    "create_directory",  # directory_commands.py
    "delete_directory",  # directory_commands.py
    "list_archives",  # archive_commands.py
    "list_contents",  # directory_commands.py
    
    # Core classes
    "ArchiveHandler",
    "DynamicArchiveType",
    
    # Handler pattern classes
    "Handler",
    "FileHandler",
    "TextFileHandler", 
    "JsonFileHandler",
    "DirectoryHandler",
    "GitProjectHandler",
    "PythonProjectHandler",
    "ExecutableHandler",
    "PythonScriptHandler",
    "HandlerRegistry",
    "create_file_handler_registry",
    "create_directory_handler_registry", 
    "create_executable_handler_registry",
    "get_file_handler_registry",
    "get_directory_handler_registry",
    "get_executable_handler_registry",
    
    # Archive handler classes
    "ZipArchiveHandler",
    "TarArchiveHandler",
    "SevenZipArchiveHandler",
    "AppBundleHandler",
    "WheelArchiveHandler",
    "OfficeDocumentHandler",
]
