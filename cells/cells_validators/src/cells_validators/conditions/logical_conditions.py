"""
Logical conditions for combining multiple conditions.
"""

from typing import List
from ..__base__ import Any, Dict, Optional, logger
from ..types.rule_types import ConditionType, ConditionOperator
from .base_condition import BaseCondition

class LogicalCondition(BaseCondition):
    """
    Condition that combines multiple sub-conditions using logical operators.
    
    Supports AND, OR, NOT, and XOR operations on child conditions.
    """
    
    def __init__(
        self,
        operator: ConditionOperator,
        conditions: List[BaseCondition],
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionType.LOGICAL, operator, None, metadata)
        self.conditions = conditions or []
        self._validate_operator()
    
    def _validate_operator(self) -> None:
        """Validate that the operator is appropriate for logical conditions."""
        logical_ops = {
            ConditionOperator.AND,
            ConditionOperator.OR, 
            ConditionOperator.NOT,
            ConditionOperator.XOR
        }
        
        if self.operator not in logical_ops:
            raise ValueError(f"Invalid logical operator: {self.operator}")
        
        # NOT operator should have exactly one condition
        if self.operator == ConditionOperator.NOT and len(self.conditions) != 1:
            raise ValueError("NOT operator requires exactly one condition")
        
        # XOR operator should have exactly two conditions
        if self.operator == ConditionOperator.XOR and len(self.conditions) != 2:
            raise ValueError("XOR operator requires exactly two conditions")
    
    def add_condition(self, condition: BaseCondition) -> None:
        """Add a condition to the logical group."""
        self.conditions.append(condition)
        self._validate_operator()
    
    def remove_condition(self, condition: BaseCondition) -> bool:
        """Remove a condition from the logical group."""
        try:
            self.conditions.remove(condition)
            return True
        except ValueError:
            return False
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate logical condition against context."""
        if not self.enabled:
            return True
        
        if not self.conditions:
            logger.warning(f"Logical condition {self.operator} has no sub-conditions")
            return True
        
        try:
            return self._evaluate_logical_operator(context)
        except Exception as e:
            logger.error(f"Error evaluating logical condition {self}: {e}")
            return False
    
    def _evaluate_logical_operator(self, context: Dict[str, Any]) -> bool:
        """Evaluate the specific logical operator."""
        if self.operator == ConditionOperator.AND:
            return all(condition.evaluate(context) for condition in self.conditions)
        
        elif self.operator == ConditionOperator.OR:
            return any(condition.evaluate(context) for condition in self.conditions)
        
        elif self.operator == ConditionOperator.NOT:
            return not self.conditions[0].evaluate(context)
        
        elif self.operator == ConditionOperator.XOR:
            result1 = self.conditions[0].evaluate(context)
            result2 = self.conditions[1].evaluate(context)
            return result1 != result2  # XOR: true if exactly one is true
        
        else:
            logger.warning(f"Unknown logical operator: {self.operator}")
            return False
    
    def clear_cache(self) -> None:
        """Clear cache for this condition and all sub-conditions."""
        super().clear_cache()
        for condition in self.conditions:
            condition.clear_cache()
    
    def __str__(self) -> str:
        """String representation of logical condition."""
        return f"LogicalCondition({self.operator}, {len(self.conditions)} conditions)"
    
    def __repr__(self) -> str:
        """Detailed representation of logical condition."""
        return (
            f"LogicalCondition("
            f"operator={self.operator}, "
            f"conditions={len(self.conditions)}, "
            f"enabled={self.enabled})"
        )

class AndCondition(LogicalCondition):
    """Convenience class for AND logical conditions."""
    
    def __init__(
        self,
        conditions: List[BaseCondition],
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionOperator.AND, conditions, metadata)

class OrCondition(LogicalCondition):
    """Convenience class for OR logical conditions."""
    
    def __init__(
        self,
        conditions: List[BaseCondition],
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionOperator.OR, conditions, metadata)

class NotCondition(LogicalCondition):
    """Convenience class for NOT logical conditions."""
    
    def __init__(
        self,
        condition: BaseCondition,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionOperator.NOT, [condition], metadata)

class XorCondition(LogicalCondition):
    """Convenience class for XOR logical conditions."""
    
    def __init__(
        self,
        condition1: BaseCondition,
        condition2: BaseCondition,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionOperator.XOR, [condition1, condition2], metadata)