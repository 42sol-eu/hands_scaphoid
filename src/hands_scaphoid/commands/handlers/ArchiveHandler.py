"""
ArchiveHandler class module.
---yaml
File:
    name:   ArchiveHandler.py
    uuid:   f9e3k4p5-2q7l-8m3n-ab4c-9k5l6m7n8o9p
    date:   2025-09-30

Description:
    Dataclass for archive operation handlers

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from dataclasses import dataclass
from typing import Callable


@dataclass
class ArchiveHandler:
    """
    Dataclass containing callable handlers for archive operations.
    
    Attributes:
        extract: Callable for extracting archives
        pack: Callable for creating archives
        test: Callable for testing archive integrity
        list_files: Callable for listing archive contents
    """
    extract: Callable
    pack: Callable
    test: Callable
    list_files: Callable