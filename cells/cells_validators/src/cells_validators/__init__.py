"""
Bones Validator - A rule-based validation framework with conditional rule networks.

This package provides a flexible validation system where rules can be activated
based on conditions, enabling complex validation workflows and rule networking.

Key Features:
- Rule-based validation with severity levels
- Conditional rule activation based on value patterns
- Rule dependencies and execution ordering
- High-performance caching and optimization
- Extensible architecture for custom rules and conditions

Example Usage:
    from bones_validator import RuleEngine, Rule, ValueCondition
    from bones_validator.types import SeverityType, ConditionOperator
    
    # Create engine
    engine = RuleEngine()
    
    # Add conditional rules for dotfiles
    dotfile_condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
    engine.add_conditional_rules(dotfile_condition, [
        Rule("hidden_file", r"^\.[^/]*$", SeverityType.ERROR, "Valid hidden file"),
        Rule("no_double_dots", r"^\.{2,}", SeverityType.WARNING, "No multiple dots", inverse=True)
    ])
    
    # Validate values
    result = engine.validate(".bashrc")  # Uses dotfile rules
    print(f"Valid: {result.is_valid}, Violations: {len(result.violations)}")
"""

from .__base__ import __version__, __author__, __email__

# Core components
from .core import RuleEngine, ValidationResult
from .rules import BaseRule, Rule, ConditionalRule, ValidationViolation
from .conditions import (
    BaseCondition,
    EvaluationContext,
    ValueCondition,
    ContextCondition,
    CustomCondition,
    LogicalCondition,
    AndCondition,
    OrCondition,
    NotCondition,
    XorCondition,
)
from .types import (
    SeverityType,
    RuleType,
    ConditionType,
    ConditionOperator,
    ConnectorType,
    ExecutionStrategy,
    RuleConfig,
    ConditionConfig,
    ConnectorConfig,
    EngineConfig,
)
from .validators import (
    ValidatorMixin,
    create_dotfile_rules,
    create_absolute_path_rules,
    create_filename_rules,
)

# Main exports
__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__email__",
    
    # Core components
    "RuleEngine",
    "ValidationResult",
    
    # Rules
    "BaseRule",
    "Rule", 
    "ConditionalRule",
    "ValidationViolation",
    
    # Conditions
    "BaseCondition",
    "EvaluationContext",
    "ValueCondition",
    "ContextCondition",
    "CustomCondition",
    "LogicalCondition",
    "AndCondition",
    "OrCondition", 
    "NotCondition",
    "XorCondition",
    
    # Types
    "SeverityType",
    "RuleType",
    "ConditionType",
    "ConditionOperator",
    "ConnectorType",
    "ExecutionStrategy",
    "RuleConfig",
    "ConditionConfig",
    "ConnectorConfig",
    "EngineConfig",
    
    # Validators
    "ValidatorMixin",
    "create_dotfile_rules",
    "create_absolute_path_rules",
    "create_filename_rules",
]