"""
HandlerRegistry class module.
---yaml
File:
    name: HandlerRegistry.py
    uuid: u5v1w7x3-4y9z-0a6b-rs7t-9u0v1w2x3y4z
    date: 2025-09-30

Description:
    Generic registry for managing handlers of any type with factory functions

Project:
    name: hands_scraphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
from typing import Any, List, Optional

#%% [Project base imports]
from ...__base__ import logger

#%% [Local imports]
from .FileHandler import FileHandler
from .files.TextFileHandler import TextFileHandler
from .files.JsonFileHandler import JsonFileHandler
from .DirectoryHandler import DirectoryHandler
from .directories.GitProjectHandler import GitProjectHandler
from .directories.PythonProjectHandler import PythonProjectHandler
from .files.ExecutableHandler import ExecutableHandler
from .files.PythonScriptHandler import PythonScriptHandler


class HandlerRegistry:
    """Generic registry for managing handlers of any type."""
    
    def __init__(self, handler_type: type):
        self.handler_type = handler_type
        self.handlers = {}
        self.default_handler = None
    
    def register(self, name: str, handler: Any, is_default: bool = False):
        """Register a handler."""
        if not isinstance(handler, self.handler_type):
            raise TypeError(f"Handler must be instance of {self.handler_type}")
        
        self.handlers[name] = handler
        if is_default:
            self.default_handler = handler
        
        logger.debug(f"Registered {self.handler_type.__name__}: {name}")
    
    def get(self, name: str) -> Optional[Any]:
        """Get handler by name."""
        return self.handlers.get(name)
    
    def get_default(self) -> Optional[Any]:
        """Get default handler."""
        return self.default_handler
    
    def list_handlers(self) -> List[str]:
        """List all registered handler names."""
        return list(self.handlers.keys())


# =============================================================================
# Factory Functions and Convenience APIs
# =============================================================================

def create_file_handler_registry() -> HandlerRegistry:
    """Create and populate file handler registry."""
    registry = HandlerRegistry(FileHandler)
    
    # Register default handlers
    registry.register('text', TextFileHandler(), is_default=True)
    registry.register('json', JsonFileHandler())
    registry.register('utf8', TextFileHandler('utf-8'))
    registry.register('ascii', TextFileHandler('ascii'))
    
    return registry


def create_directory_handler_registry() -> HandlerRegistry:
    """Create and populate directory handler registry."""
    registry = HandlerRegistry(DirectoryHandler)
    
    # Register default handlers
    registry.register('git', GitProjectHandler())
    registry.register('python', PythonProjectHandler())
    
    return registry


def create_executable_handler_registry() -> HandlerRegistry:
    """Create and populate executable handler registry."""
    registry = HandlerRegistry(ExecutableHandler)
    
    # Register default handlers
    registry.register('python', PythonScriptHandler(), is_default=True)
    
    return registry


# Global registries (lazy initialization)
_file_handlers = None
_directory_handlers = None
_executable_handlers = None


def get_file_handler_registry() -> HandlerRegistry:
    """Get global file handler registry."""
    global _file_handlers
    if _file_handlers is None:
        _file_handlers = create_file_handler_registry()
    return _file_handlers


def get_directory_handler_registry() -> HandlerRegistry:
    """Get global directory handler registry."""
    global _directory_handlers
    if _directory_handlers is None:
        _directory_handlers = create_directory_handler_registry()
    return _directory_handlers


def get_executable_handler_registry() -> HandlerRegistry:
    """Get global executable handler registry."""
    global _executable_handlers
    if _executable_handlers is None:
        _executable_handlers = create_executable_handler_registry()
    return _executable_handlers