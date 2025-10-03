#!/usr/bin/env python3
"""
Base module for bones_validator package.

Provides common imports and utilities used throughout the package.
"""

# [Standard library imports]
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Protocol,
    Set,
    Tuple,
    Union,
    TYPE_CHECKING
)

# [Third party imports]
from pydantic import BaseModel, Field

# [Version info]
__version__ = "0.1.0"
__author__ = "Andreas Felix Häberle"
__email__ = "felix@42sol.eu"

# [Logging setup]
logger = logging.getLogger("bones_validator")
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

# [Common type aliases]
ValueType = Union[str, int, float, bool]
ConditionFunc = Callable[[Any], bool]
ValidatorFunc = Callable[[str], bool]
RulePattern = Union[str, ValidatorFunc]

# [Common exports]
__all__ = [
    # Types
    "ValueType",
    "ConditionFunc", 
    "ValidatorFunc",
    "RulePattern",
    # Classes
    "BaseModel",
    "Field",
    "ABC",
    "abstractmethod",
    "dataclass",
    "field",
    "Enum",
    "Protocol",
    # Standard library
    "Any",
    "Callable",
    "Dict",
    "List",
    "Optional",
    "Set", 
    "Tuple",
    "Union",
    "TYPE_CHECKING",
    "re",
    "logging",
    # Utilities
    "logger",
    "__version__",
    "__author__",
    "__email__",
]