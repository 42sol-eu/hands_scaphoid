"""
SimpleCommandType enum module.
---yaml
File:
    name: SimpleCommandType.py
    uuid: 7f4e8d3a-8c2b-5d6e-b7c8-3d4e5a6f7g8h
    date: 2025-09-30

Description:
    Enum representing different types of simple access commands

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from enum import Enum


class SimpleCommandType(str, Enum):
    """Enum representing different types of simple commands."""

    READ = "read-access"
    WRITE = "write-access"
    DELETE = "delete-access"
    EXECUTE = "execute-access"
    # Additional command types can be added here as needed.