from .ItemCore import ItemCore
from .type_enums import ItemType


class ObjectCore(ItemCore):
    """
    Represents an object in the shell context.

    Attributes:
        name (str): The name of the object.
        path (str): The path of the object in the filesystem.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path, item_type=ItemType.OBJECT)

    def __repr__(self):
        return f"ObjectCore(name={self.name}, path={self.value})"
