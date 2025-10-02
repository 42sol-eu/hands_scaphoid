"""
CommandType enum module.
---yaml
File:
    name: CommandType.py
    uuid: 5h6g0f5c-8e4d-5f8g-d9ea-5f6g7a8h9i0j
    date: 2025-09-30

Description:
    Enum representing different command categories for operations

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from enum import Enum


class CommandType(str, Enum):
    """Enum representing different command categories."""

    EXISTS = "exists"
    TYPE = "type"
    PERMISSIONS = "permissions"
    SIZE = "size"
    LIST = "list"
    SHOW = "show"
    LINK = "link"
    MOUNT = "mount"
    EXTRACT = "extract"
    CREATE = "create"
    MOVE = "move"
    COPY = "copy"
    UNLINK = "unlink"
    DELETE = "delete"
    UNMOUNT = "unmount"
    EXECUTE = "execute"
    # Additional command types can be added here as needed.