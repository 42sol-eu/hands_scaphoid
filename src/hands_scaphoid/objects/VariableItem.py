from .ItemCore import ItemCore
from ..types.ItemType import ItemType
from ..__base__ import is_instance, Any

class VariableItem(ItemCore):
    """
    Represents a variable in the shell context.

    Attributes:
        name (str): The name of the variable.
        value (str): The value of the variable.
    """

    def __init__(self, name: str, value: str):
        """Initializes a VariableItem instance."""
        super().__init__(name, value, item_type=ItemType.VARIABLE)
        self.value = value

    def __repr__(self):
        """Returns a string representation of the VariableItem."""
        return f"VariableItem(name={self.name}, value={self.value})"

    @classmethod
    def from_dict(cls, data: dict) -> "VariableItem":
        """ensure correct type"""
        obj = super().from_dict(data)
        if not is_instance(obj, VariableItem):
            raise TypeError(f"from_dict expected to create 'VariableItem', got '{type(obj)}'")
        return obj