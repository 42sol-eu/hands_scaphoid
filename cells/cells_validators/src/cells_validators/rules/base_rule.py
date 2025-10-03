"""
Base rule classes for validation.
"""

import re
from dataclasses import dataclass
from ..__base__ import ABC, abstractmethod, Any, Dict, List, Optional, Union, logger
from ..types.rule_types import SeverityType, RuleType
from ..conditions.base_condition import BaseCondition, EvaluationContext

@dataclass
class ValidationViolation:
    """
    Represents a validation rule violation.
    """
    rule_name: str
    severity: SeverityType
    message: str
    value: Any
    context: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

class BaseRule(ABC):
    """
    Abstract base class for all validation rules.
    
    Rules define validation logic that can be applied to values.
    They can have conditions that determine when they should be active.
    """
    
    def __init__(
        self,
        name: str,
        pattern: Union[str, callable],
        severity: SeverityType = SeverityType.ERROR,
        description: str = "",
        inverse: bool = False,
        enabled: bool = True,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.name = name
        self.pattern = pattern
        self.severity = severity
        self.description = description or f"Rule: {name}"
        self.inverse = inverse
        self.enabled = enabled
        self.tags = tags or []
        self.metadata = metadata or {}
        
        # Rule networking
        self.activation_conditions: List[BaseCondition] = []
        self.dependencies: List[str] = dependencies or []  # Rule names this rule depends on
        self.dependents: List[str] = []    # Rule names that depend on this rule
        
        # Performance tracking
        self.execution_count = 0
        self.violation_count = 0
        
        # Compile regex patterns for performance
        self._compiled_pattern: Optional[re.Pattern] = None
        if isinstance(pattern, str):
            try:
                self._compiled_pattern = re.compile(pattern)
            except re.error as e:
                logger.warning(f"Invalid regex pattern in rule '{name}': {e}")
    
    @property
    def rule_type(self) -> RuleType:
        """Get the rule type."""
        return RuleType.BASIC
    
    def add_activation_condition(self, condition: BaseCondition) -> None:
        """Add a condition that determines when this rule is active."""
        self.activation_conditions.append(condition)
    
    def remove_activation_condition(self, condition: BaseCondition) -> bool:
        """Remove an activation condition."""
        try:
            self.activation_conditions.remove(condition)
            return True
        except ValueError:
            return False
    
    def is_active(self, context: Dict[str, Any]) -> bool:
        """Check if the rule should be active given the context."""
        if not self.enabled:
            return False
        
        # If no activation conditions, rule is always active
        if not self.activation_conditions:
            return True
        
        # All activation conditions must be met
        try:
            value = context.get('value') if isinstance(context, dict) else context
            eval_context = EvaluationContext(value, metadata=context)
            return all(condition.evaluate(eval_context.to_dict()) for condition in self.activation_conditions)
        except Exception as e:
            logger.error(f"Error evaluating activation conditions for rule '{self.name}': {e}")
            return False
    
    @abstractmethod
    def validate(self, value: Any, context: Optional[Union[EvaluationContext, Dict[str, Any]]] = None) -> Optional[ValidationViolation]:
        """
        Validate a value against this rule.
        
        Args:
            value: Value to validate
            context: Optional evaluation context
            
        Returns:
            ValidationViolation if rule is violated, None otherwise
        """
    
    def _create_violation(self, value: Any, message: str = None, context: Optional[Dict[str, Any]] = None) -> ValidationViolation:
        """Create a validation violation for this rule."""
        self.violation_count += 1
        return ValidationViolation(
            rule_name=self.name,
            severity=self.severity,
            message=message or self.description,
            value=value,
            context=context,
            metadata=self.metadata.copy()
        )
    
    def reset_stats(self) -> None:
        """Reset execution statistics."""
        self.execution_count = 0
        self.violation_count = 0
    
    def get_stats(self) -> Dict[str, Any]:
        """Get rule execution statistics."""
        return {
            'name': self.name,
            'executions': self.execution_count,
            'violations': self.violation_count,
            'violation_rate': self.violation_count / max(self.execution_count, 1),
            'enabled': self.enabled,
            'has_conditions': len(self.activation_conditions) > 0,
            'dependencies': len(self.dependencies),
            'dependents': len(self.dependents)
        }
    
    def __str__(self) -> str:
        """String representation of the rule."""
        status = "enabled" if self.enabled else "disabled"
        return f"{self.name} ({status})"
    
    def __repr__(self) -> str:
        """Detailed representation of the rule."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"severity={self.severity}, "
            f"enabled={self.enabled}, "
            f"conditions={len(self.activation_conditions)})"
        )

class Rule(BaseRule):
    """
    Basic validation rule implementation.
    
    Supports regex patterns and custom validator functions.
    """
    
    def validate(self, value: Any, context: Optional[Union[EvaluationContext, Dict[str, Any]]] = None) -> Optional[ValidationViolation]:
        """Validate value against the rule pattern."""
        self.execution_count += 1
        
        # Create context if not provided or convert dict to EvaluationContext
        if context is None:
            context = EvaluationContext(value)
            context_dict = context.to_dict()
        elif isinstance(context, dict):
            context_dict = context
            context = EvaluationContext(value, metadata=context)
        else:
            context_dict = context.to_dict()
        
        # Check if rule is active
        if not self.is_active(context_dict):
            return None
        
        try:
            # Evaluate the pattern
            if isinstance(self.pattern, str):
                # Regex pattern
                match = self._compiled_pattern.search(str(value)) if self._compiled_pattern else False
            else:
                # Custom validator function
                match = bool(self.pattern(value))
            
            # Apply inverse logic if needed
            if self.inverse:
                match = not match
            
            # Return violation if rule fails
            if not match:
                return self._create_violation(value, self.description, context_dict)
            
            return None
            
        except Exception as e:
            logger.error(f"Error validating rule '{self.name}': {e}")
            return self._create_violation(value, f"Rule validation error: {e}", context_dict)

class ConditionalRule(Rule):
    """
    Rule that has explicit conditions for activation.
    
    This is a specialized version of Rule that emphasizes
    the conditional aspect for rule networking.
    """
    
    def __init__(
        self,
        name: str,
        pattern: Union[str, callable],
        severity: SeverityType = SeverityType.ERROR,
        description: str = "",
        inverse: bool = False,
        enabled: bool = True,
        activation_condition: Optional[BaseCondition] = None,
        conditions: Optional[List[BaseCondition]] = None,
        dependencies: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(name, pattern, severity, description, inverse, enabled, dependencies, tags, metadata)
        
        # Handle both single condition and list of conditions for flexibility
        if activation_condition:
            self.activation_conditions.append(activation_condition)
        if conditions:
            self.activation_conditions.extend(conditions)
    
    @property
    def rule_type(self) -> RuleType:
        """Get the rule type."""
        return RuleType.CONDITIONAL
    
    def should_activate(self, value: Any, context: Optional[Dict[str, Any]] = None) -> bool:
        """Check if this rule should be activated for the given value and context."""
        context = context or {}
        eval_context = EvaluationContext(value, metadata=context)
        return self.is_active(eval_context.to_dict())