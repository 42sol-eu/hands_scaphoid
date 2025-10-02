from .ItemCore import ItemCore
from ..types.ItemType import ItemType


class VariableItem(ItemCore):
    """
    Represents a variable in the shell context.

    Attributes:
        name (str): The name of the variable.
        value (str): The value of the variable.
    """

    def __init__(self, name: str, value: str):
        super().__init__(name, value, item_type=ItemType.VARIABLE)
        self.value = value

    def __repr__(self):
        return f"VariableItem(name={self.name}, value={self.value})"
