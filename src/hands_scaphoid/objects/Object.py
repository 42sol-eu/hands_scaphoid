from .Item import Item
from .type_enums import ItemType

class Object(Item):
    """
    Represents an object in the shell context.

    Attributes:
        name (str): The name of the object.
        path (str): The path of the object in the filesystem.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path, item_type=ItemType.OBJECT)

    def __repr__(self):
        return f"Object(name={self.name}, path={self.value})"

