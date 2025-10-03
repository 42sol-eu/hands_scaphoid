#!/usr/bin/env python3
"""
SeverityType enum module for validation system.

File:
    name: SeverityType.py
    uuid: d4f8e9b2-3c5a-4f7d-9e8b-1a2c3d4e5f6g
    date: 2025-10-03

Description:
    Enum representing different severity levels for validation rules and violations

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- N/A:: Not Applicable
"""

# [Standard library imports]
from enum import Enum
import yaml

# [Local imports]
from .EnumMixin import EnumMixin

class SeverityType(EnumMixin, str, Enum):
    """
    Enum representing different severity levels for validation rules.
    
    Used to categorize validation rule violations:
    - ERROR: Critical issues that make the value invalid
    - WARNING: Issues that should be noted but don't invalidate the value
    - INFO: Informational messages for debugging or best practices
    """

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"

    def __str__(self):
        return self.value
    
    def __repr__(self):
        return f"SeverityType.{self.name}"

    @property
    def is_error(self) -> bool:
        """Check if this severity represents an error.""" 
        return self == SeverityType.ERROR
        
    @property
    def is_warning(self) -> bool:
        """Check if this severity represents a warning."""
        return self == SeverityType.WARNING
        
    @property
    def is_info(self) -> bool:
        """Check if this severity represents info."""
        return self == SeverityType.INFO

# Custom representer for Enum
def enum_representer(dumper, data):
    """Convert the enum to a YAML scalar."""
    return dumper.represent_scalar('tag:yaml.org,2002:str', data.value)

# Register the custom representer
yaml.add_representer(SeverityType, enum_representer, yaml.SafeDumper)