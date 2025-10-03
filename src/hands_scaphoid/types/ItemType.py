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

# [Standard library imports]
from enum import Enum
import yaml 

# [Local imports]
from .EnumMixin import EnumMixin

class ItemType(EnumMixin, str, Enum):
    """Enum representing different types of items."""

    ITEM = "item"
    VARIABLE = "variable"
    PATH = "path"
    OBJECT = "object"
    PROJECT = "project"
    ENVIRONMENT = "environment"
    FILE = "file"
    DIRECTORY = "directory"
    ARCHIVE = "archive"
    LINK = "link"
    MOUNT = "mount"
    SYSTEM = "system"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"ItemType.{self.name}"

    # Additional item types can be added here as needed.

# Custom representer for Enum
def enum_representer(dumper, data):
    """convert the enum to a YAML scalar"""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.value)

# Register the custom representer
yaml.add_representer(Enum, enum_representer)
yaml.add_representer(ItemType, enum_representer, yaml.SafeDumper)