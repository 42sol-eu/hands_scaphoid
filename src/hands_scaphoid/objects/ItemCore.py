#!/usr/bin/env python3
"""
ItemCore module for hands-scaphoid package.

This module provides the ItemCore class for pure item operations.
---yaml
File:
    name: ItemCore.py
    uuid: 268f89e1-abfc-4376-9e19-f6e78372e289
    date: 2025-10-03

Description:
    Pure file operations class - no context management

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Häberle"]
"""

# [Standard library imports]
import os
import yaml
import json

# [Local imports]
from ..__base__ import *
from ..types.ItemType import ItemType

# [Third party imports]
import tomli 


# [Code]

class ItemCore:
    def __init__(self, name: str, value: str | int, 
                 item_type: str | ItemType = ItemType.ITEM,
                 project: Any = None):
        self._name = name
        self._value = value if isinstance(value, int) else value
        self._item_type = item_type
        if is_instance(project, str):
            project = ItemCore(name=project, value=os.getenv(project, ""), item_type=ItemType.PROJECT)
        self._project = project

    @property
    def name(self) -> str:
        return self._name

    @property
    def value(self) -> str | int:
        return self._value

    @value.setter
    def value(self, new_value: str):
        self._value = new_value

    @property
    def item_type(self) -> ItemType:
        return self._item_type

    @property
    def project(self) -> 'ItemCore':
        """get project as object"""
        return self._project

    @property
    def project_as_str(self) -> str:
        """get project as string"""
        return str(self._project) if self._project.value is None else self._project.value()

    @project.setter
    def project(self, new_project: Any):
        if is_instance(new_project, str):
            new_project = ItemCore(name=new_project, value=os.getenv(new_project, ""), item_type=ItemType.PROJECT)
        self._project = new_project

    def __repr__(self) -> str:
        return f"ItemCore(name={self._name}, value={self._value}, item_type={self._item_type.name})"

    def __str__(self) -> str:
        return f'{self._name}="{self._value}"'

    def to_dict(self) -> dict:
        return {
            "name": self._name,
            "value": self._value,
            "item_type": self._item_type,
            "project": self._project if self._project else None
        }
        # MAYBE: return project as sub dict (using a parameter in to_dict)

    def to_json(self) -> str:
        """return as JSON"""
        return json.dumps(self.to_dict())

    def to_yaml(self) -> str:
        return yaml.safe_dump(self.to_dict())

    def to_toml(self) -> str:
        """return as TOML"""
        # Manual TOML formatting
        data = self.to_dict()
        toml_lines = []
        for key, value in data.items():
            if value is None:
                toml_lines.append(f'{key} = ""')
            elif isinstance(value, str):
                toml_lines.append(f'{key} = "{value}"')
            elif isinstance(value, (int, float)):
                toml_lines.append(f'{key} = {value}')
            else:
                toml_lines.append(f'{key} = "{str(value)}"')
        return '\n'.join(toml_lines) + '\n'

    def to_env_var(self) -> str:
        return f"{self._name}={self._value}"

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            name=data.get("name", ""),
            value=data.get("value", ""),
            item_type=ItemType(data.get("item_type", ItemType.ITEM)),
            project=data.get("project"),
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

# [End of file]