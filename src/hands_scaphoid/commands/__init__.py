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


# %% [Exports]
__all__ = [
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
    "create",  # src\hands_scaphoid\commands\archive_commands.py
    "extract",  # src\hands_scaphoid\commands\archive_commands.py
    "create_directory",  # src\hands_scaphoid\commands\directory_commands.py
    "delete_directory",  # src\hands_scaphoid\commands\directory_commands.py
    "list_archives",  # src\hands_scaphoid\commands\archive_commands.py
    "list_contents",  # src\hands_scaphoid\commands\directory_commands.py
]
