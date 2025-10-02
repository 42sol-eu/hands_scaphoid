"""
AccessCommandType enum module.
---yaml
File:
    name: AccessCommandType.py
    uuid: 6g5f9e4b-7d3c-4e7f-c8d9-4e5f6a7g8h9i
    date: 2025-09-30

Description:
    Enum representing different types of access permissions with single character symbols

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from enum import Enum


class AccessCommandType(str, Enum):
    """Enum representing different types of access permissions.

    Each access type is represented by a single character symbol.
    see https://hands-scaphoid.readthedocs.io/en/latest/operations/summary.html

    """

    META = "M"
    READ = "R"
    SHOW = "S"
    UPDATE = "U"
    CREATE = "C"
    WRITE = "W"
    DELETE = "D"
    EXECUTE = "E"
    # Additional access types can be added here as needed.