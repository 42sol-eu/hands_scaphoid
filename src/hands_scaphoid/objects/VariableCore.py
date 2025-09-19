from .ItemCore import ItemCore
from .type_enums import ItemType


class VariableCore(ItemCore):
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
        return f"VariableCore(name={self.name}, value={self.value})"
