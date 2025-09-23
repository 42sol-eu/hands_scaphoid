"""
Init hands_scaphoid/commands module for package.

This module contains command functions used throughout the package.
----
file:
    name:        __init__.py
    uuid:        c7151963-72d1-4661-bec3-accb29f39c85
description:     init commands
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from hands_scaphoid.commands.core_commands import (
    exists,
    is_instance,
    is_item,
    is_directory,
    is_file,
    is_git_project,
    is_hands_project,
    is_link,
    is_object,
    is_variable,
    is_vscode_project,
    get_file_extension,
)
from .directory_commands import (
    create_directory,
    delete_directory,
    list_archives,
    list_contents,
)
from .archive_commands import create_zip_archive, list_archives


__all__ = [
    "create_directory",  # src\hands_scaphoid\commands\directory_commands.py
    "delete_directory",  # src\hands_scaphoid\commands\directory_commands.py
    "list_archives",  # src\hands_scaphoid\commands\archive_commands.py
    "list_contents",  # src\hands_scaphoid\commands\directory_commands.py
]
