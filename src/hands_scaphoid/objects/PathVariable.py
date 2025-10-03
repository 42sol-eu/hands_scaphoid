#!/usr/bin/env python3
"""
PathVariable module for hands-scaphoid package.

This module provides the PathVariable class with comprehensive path validation.
---yaml
File:
    name: PathVariable.py
    uuid: 1ab01ca2-84c3-454a-9589-5ba028a0c2ce
    date: 2025-10-03

Description:
    Path variable class with ValidationMixin integration for robust path validation

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- OS[system]: Operating System
"""

# [Standard library imports]
import os
from typing import List, Optional

# [Local imports]
from .VariableItem import VariableItem
from .ValidatorMixin import ValidationMixin, ValidationViolation
from ..types.ItemType import ItemType
from ..types.SeverityType import SeverityType
from ..__base__ import is_instance, Any, logger

# [Third party imports]
# - none 

# [Code]
class PathVariable(ValidationMixin, VariableItem):
    """
    A variable that contains a path with comprehensive validation.
    
    Combines VariableItem functionality with ValidationMixin to provide:
    - Path-specific validation rules
    - Cross-platform path compatibility checking
    - Strict mode for enhanced validation
    - Built-in rules for common path issues
    """
    
    def __init__(self, name: str, value: str, strict_mode: bool = False, cross_platform: bool = False):
        # Initialize ValidationMixin first
        ValidationMixin.__init__(self, strict_mode=strict_mode, cross_platform=cross_platform)
        
        # Initialize VariableItem (which calls ItemCore)
        VariableItem.__init__(self, name=name, value="")  # Don't set value yet to avoid validation before setup
        
        # Set specific attributes
        self._item_type = ItemType.PATH
        self._valid = None
        self._exists = None
        
        # Add path-specific validation rules
        self.add_path_rules()
        
        # Now set the value (triggers validation)
        self.value = value

    @property
    def value(self) -> str:
        """Get the path value."""
        return self._value

    @value.setter
    def value(self, new_value: str):
        """
        Set the path value and perform validation.
        
        Args:
            new_value: The new path value to set
        """
        self._value = new_value
        self._exists = os.path.exists(new_value) if new_value else False
        
        # Perform validation and store result
        if self.validation_enabled:
            is_valid, violations = self.validate()
            self._valid = is_valid
            self._last_violations = violations
        else:
            self._valid = True
            self._last_violations = []

    @property
    def valid(self) -> bool:
        """Check if the path passes validation rules."""
        if self._valid is None and self.validation_enabled:
            self._valid, self._last_violations = self.validate()
        return self._valid if self._valid is not None else True

    @property
    def not_valid(self) -> bool:
        """Check if the path does not pass validation rules."""
        return not self.valid

    @property
    def invalid(self) -> bool:
        """Check if the path does not pass validation rules."""
        return not self.valid

    @property
    def exists(self) -> bool:
        """Check if the path exists on the filesystem."""
        if self._exists is None:
            self._exists = os.path.exists(self._value) if self._value else False
        return self._exists

    @property
    def not_exists(self) -> bool:
        """Check if the path does not exist on the filesystem."""
        return not self.exists

    @property  
    def last_violations(self) -> List[ValidationViolation]:
        """Get violations from the last validation run."""
        return getattr(self, '_last_violations', [])

    def get_validation_summary(self) -> dict:
        """
        Get a summary of the current validation status.
        
        Returns:
            dict: Summary containing validity, violations, and recommendations
        """
        is_valid, violations = self.validate() if self.validation_enabled else (True, [])
        
        return {
            "is_valid": is_valid,
            "exists": self.exists,
            "validation_enabled": self.validation_enabled,
            "strict_mode": self.strict_mode,
            "cross_platform": self.cross_platform,
            "violations": [
                {
                    "rule": v.rule_name,
                    "severity": v.severity.value,
                    "message": v.message
                }
                for v in violations
            ],
            "error_count": sum(1 for v in violations if v.severity.is_error),
            "warning_count": sum(1 for v in violations if v.severity.is_warning),
            "info_count": sum(1 for v in violations if v.severity.is_info)
        }

    def __repr__(self):
        """Returns a string representation of the PathVariable."""
        valid_status = "valid" if self.valid else "invalid"
        exists_status = "exists" if self.exists else "not exists"
        return f"PathVariable(name={self.name}, value={self.value}, {valid_status}, {exists_status})"

    @classmethod
    def is_valid_path(cls, path: str, strict_mode: bool = False, cross_platform: bool = False) -> bool:
        """
        Check if a given path string is valid according to validation rules.
        
        Args:
            path: Path string to validate
            strict_mode: Enable strict validation
            cross_platform: Enable cross-platform validation
            
        Returns:
            bool: True if path is valid, False otherwise
        """
        temp_var = cls("temp", path, strict_mode=strict_mode, cross_platform=cross_platform)
        return temp_var.valid

    @classmethod
    def does_exist(cls, path: str) -> bool:
        """Check if a given path exists on the filesystem."""
        return os.path.exists(path)

    @classmethod  
    def get_path_violations(cls, path: str, strict_mode: bool = False, cross_platform: bool = False) -> List[ValidationViolation]:
        """
        Get validation violations for a path without creating a persistent object.
        
        Args:
            path: Path string to validate
            strict_mode: Enable strict validation  
            cross_platform: Enable cross-platform validation
            
        Returns:
            List[ValidationViolation]: List of violations found
        """
        temp_var = cls("temp", path, strict_mode=strict_mode, cross_platform=cross_platform)
        _, violations = temp_var.validate()
        return violations
        
    def to_dict(self) -> dict:
        """
        Serialize the PathVariable to a dictionary.
        
        Returns:
            dict: Dictionary representation including validation config
        """
        data = super().to_dict()
        data.update({
            "exists": self.exists,
            "validation_summary": self.get_validation_summary()
        })
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "PathVariable":
        """
        Create PathVariable from dictionary representation.
        
        Args:
            data: Dictionary containing PathVariable data
            
        Returns:
            PathVariable: Configured instance
        """
        # Extract PathVariable-specific parameters
        name = data.get("name", "")
        value = data.get("value", "")
        strict_mode = data.get("strict_mode", False)
        cross_platform = data.get("cross_platform", False)
        
        # Create instance
        obj = cls(name=name, value=value, strict_mode=strict_mode, cross_platform=cross_platform)
        
        # Apply validation configuration if present
        if "validation_enabled" in data:
            obj.validation_enabled = data["validation_enabled"]
            
        # Load any custom validation rules
        if "validation_rules" in data:
            rules_data = data["validation_rules"]
            for rule_name, rule_config in rules_data.items():
                if rule_name not in obj._validation_rules:  # Don't override built-in rules
                    obj.add_rule(
                        name=rule_name,
                        pattern=rule_config.get("pattern", ".*"),
                        severity=SeverityType(rule_config.get("severity", "error")),
                        description=rule_config.get("description", ""),
                        inverse=rule_config.get("inverse", False)
                    )
        
        # Ensure correct type
        if not is_instance(obj, PathVariable):
            raise TypeError(f"from_dict expected to create 'PathVariable', got '{type(obj)}'")
        return obj