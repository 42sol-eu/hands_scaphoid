from .Item import Item
from .type_enums import ItemType

class Variable(Item):
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
        return f"Variable(name={self.name}, value={self.value})"
    
