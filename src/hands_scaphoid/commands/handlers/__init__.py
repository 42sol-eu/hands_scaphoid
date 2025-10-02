"""
Handler implementations module.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Base handlers]
from .Handler import Handler
from .FileHandler import FileHandler
from .DirectoryHandler import DirectoryHandler
from .ArchiveHandler import ArchiveHandler
from .HandlerRegistry import HandlerRegistry

#%% [Exports]
__all__ = [
    "Handler",
    "FileHandler",
    "DirectoryHandler", 
    "ArchiveHandler",
    "HandlerRegistry",
]
