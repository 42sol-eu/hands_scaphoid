
from .type_enums import ItemType
import os
import yaml
import json

class ItemCore:
    def __init__(self, name: str, value: str, item_type: ItemType = ItemType.ITEM):
        self._name = name
        self._value = value
        self._item_type = item_type

    @property
    def name(self) -> str:
        return self._name
    
    @property
    def value(self) -> str:
        return self._value
    
    @property
    def item_type(self) -> ItemType:
        return self._item_type
    
    @value.setter
    def value(self, new_value: str):
        self._value = new_value
        
    def __repr__(self) -> str:
        return f"ItemCore(name={self._name}, value={self._value}, item_type={self._item_type})"
    
    def __str__(self) -> str:
        return f'{self._name}="{self._value}"'
    
    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "value": self._value,
            "item_type": self._item_type,
        }
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict())
    
    def to_yaml(self) -> str:
        return yaml.dump(self.to_dict())

    def to_env_var(self) -> str:
        return f"{self._name}={self._value}"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            item_type=ItemType(data.get("item_type", ItemType.ITEM)),
        )
        
    @classmethod
    def from_json(cls, json_str: str):
        data = json.loads(json_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_yaml(cls, yaml_str: str):
        data = yaml.safe_load(yaml_str)
        return cls.from_dict(data)
    
    @classmethod
    def from_env_var(cls, env_var: str):
        value = os.getenv(env_var, "")
        return cls(name=env_var, value=value, item_type=ItemType.VARIABLE)
    
