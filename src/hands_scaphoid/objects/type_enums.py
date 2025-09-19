from enum import Enum

class ItemType(str, Enum):
    """Enum representing different types of items."""
    ITEM       = "item"
    OBJECT     = "object"
    VARIABLE   = "variable"
    PATH       = "path"
    FILE       = "file"
    DIRECTORY  = "directory"
    ARCHIVE    = "archive"
    LINK       = "link"
    MOUNT      = "mount"
    SYSTEM     = "system"
    # Additional item types can be added here as needed.

class SimpleCommandType(str, Enum):
    """Enum representing different types of simple commands."""
    READ = "read-access"
    WRITE = "write-access"
    DELETE = "delete-access"
    EXECUTE = "execute-access"
    # Additional command types can be added here as needed.

class AccessCommandType(str, Enum):
    """Enum representing different types of access permissions.

    Each access type is represented by a single character symbol.
    see https://hands-scaphoid.readthedocs.io/en/latest/operations/summary.html
    
    """

    META    = "M"
    READ    = "R"
    SHOW    = "S"
    UPDATE  = "U"
    CREATE  = "C"
    WRITE   = "W"
    DELETE  = "D"
    EXECUTE = "E"
    # Additional access types can be added here as needed.

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
