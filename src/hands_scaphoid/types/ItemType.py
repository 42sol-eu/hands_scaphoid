"""
ItemType enum module.
---yaml
File:
    name: ItemType.py
    uuid: 8f3e7d2a-9b1c-4e5f-a6d7-2c3b4a5e6f7g
    date: 2025-09-30

Description:
    Enum representing different types of items in the hands_scaphoid system

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from enum import Enum


class ItemType(str, Enum):
    """Enum representing different types of items."""

    ITEM = "item"
    OBJECT = "object"
    VARIABLE = "variable"
    PATH = "path"
    FILE = "file"
    DIRECTORY = "directory"
    ARCHIVE = "archive"
    LINK = "link"
    MOUNT = "mount"
    SYSTEM = "system"
    # Additional item types can be added here as needed.