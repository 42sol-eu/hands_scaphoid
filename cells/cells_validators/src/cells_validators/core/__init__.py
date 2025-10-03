"""
Core package initialization.
"""

from .rule_engine import RuleEngine, ValidationResult

__all__ = [
    "RuleEngine",
    "ValidationResult",
]