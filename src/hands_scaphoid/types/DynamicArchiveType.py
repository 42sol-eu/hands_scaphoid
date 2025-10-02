"""
DynamicArchiveType class module.
---yaml
File:
    name:   DynamicArchiveType.py
    uuid:   h8j2k7m9-3n5p-9q4r-cd5e-8j9k0l1m2n3o
    date:   2025-09-30

Description:
    Registry-like enum replacement that can be extended at runtime for archive types

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Dict, List

#%% [Local imports]
from ..commands.handlers.ArchiveHandler import ArchiveHandler


class DynamicArchiveType:
    """A registry like enum replacement that can be extended at runtime.
    Also getting an archive handler for the core functions.
    """
    _next_id: int = 1
    _members:           Dict[str, int] = {}
    _extensions:        Dict[str, str] = {}
    _handler:           Dict[str, ArchiveHandler] = {}

    @classmethod
    def get_next_identifier(cls):
        the_id = cls._next_id 
        cls._next_id += 1
        return the_id 
    
    def __init__(self, name: str):
        if name in self.__class__._members:
            raise ValueError(f'{name} already defined in {self.__class__}')
        self.name  = name
        self.value = DynamicArchiveType.get_next_identifier()
        self.__class__._members[self.name] = self.value
        
    
    @classmethod 
    def get(cls, name: str) -> "DynamicArchiveType":
        """get a member (suffix) by name."""
        if name not in cls._members:
            raise ValueError(f'{name} [red]not[/red] defined in {cls.__class__}')
        return cls._members[name]

    @classmethod 
    def get_suffix(cls, name: str) -> "DynamicArchiveType":
        """get a member (suffix) by name."""
        if name not in cls._extensions:
            raise ValueError(f'Extension for {name} [red]not[/red] defined in {cls.__class__}')
        return cls._extensions[name]

    @classmethod 
    def get_handler(cls, name: str) -> "ArchiveHandler":
        """get an archive handler for the archive type."""
        if name not in cls._handler:
            raise ValueError(f'ArchiveHandler for {name} [red]not[/red] defined in {cls.__class__}')
        return cls._handler[name]
    
    @classmethod
    def add(cls, name: str, extension: str, handler: ArchiveHandler=None) -> bool:
        if name in cls._members:
            raise ValueError(f'{name} is already defined in {cls.__class__}')

        cls._members[name] = cls.get_next_identifier()
        cls._extensions[name] = extension
        cls._handler[name] = handler
        
        return True

    @classmethod
    def add_similar(cls, name: str, extension: str, similar_name: str) -> bool:
        """Add an archive type that reuses an already defined archive handler."""
        if similar_name not in cls._members:
            raise ValueError(f'The {similar_name} is not defined in {cls.__class__}')

        cls._members[name] = cls.get_next_identifier()
        cls._extensions[name] = extension
        cls._handler[name] = cls._handler[similar_name]

        return True
        
    @classmethod
    def items(cls) -> Dict[str, "DynamicArchiveType"]:
        return dict(cls._members)    
    
    @classmethod
    def list_types(cls) -> List[str]:
        """
        List all supported compression types.
        Returns:
            List of supported compression type strings.
        """        
        return list(cls.items().keys())

    @classmethod
    def list_extensions(cls) -> List[str]:
        """
        List all supported compression type extensions.
        Returns:
            List of supported compression type extension strings.
        """        
        return list(cls._extensions.values())

    @classmethod
    def list_types(cls) -> List[str]:
        """
        List all supported compression types.
        
        Returns:
            List of supported compression type strings.
        """        
        return list(cls._members.keys())