

# [Standard library imports]
from enum import Enum

# [Local imports]
# - none

# [Code]
class EnumMixin:
    """Mixin for nicer Enum representations and serialization."""

    def __str__(self):
        """Default: str(e) -> value"""
        return str(self.value)

    def __repr__(self):
        """Debug-friendly: <Color.RED: red>"""
        return f"<{self.__class__.__name__}.{self.name}: {self.value!r}>"

    def __int__(self):
        """Allow int(Status.NEW) if the value is numeric""" 
        if isinstance(self.value, (int, float)):
            return int(self.value)
        raise TypeError(f"{self.__class__.__name__} values are not numeric")

    def __eq__(self, other):
        """Compare against same Enum OR raw value"""
        if isinstance(other, self.__class__):
            return self.value == other.value
        return self.value == other

    def __iter__(self):
        """Allows dict(e) -> {"name": ..., "value": ...}"""
        yield from {"name": self.name, "value": self.value}.items()

    def __format__(self, spec):
        """f"{Color.RED:>10}" uses its value for formatting"""
        return format(self.value, spec)

    def to_dict(self):
        """Convert to dictionary"""
        return {"name": self.name, "value": self.value}

    def to_json(self):
        """Convert to JSON-serializable format"""
        return json  # good for JSON dumps
    # TODO: evaluate to_yson, to_toml, to_env_var if needed

# [End of file]