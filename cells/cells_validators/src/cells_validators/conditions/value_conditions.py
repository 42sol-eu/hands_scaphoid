"""
Value-based conditions for rule evaluation.
"""

import re
from ..__base__ import Any, Dict, Optional, Union, logger
from ..types.rule_types import ConditionType, ConditionOperator
from .base_condition import BaseCondition, EvaluationContext

class ValueCondition(BaseCondition):
    """
    Condition that evaluates based on the primary value.
    
    Supports various operators like equals, starts_with, contains, matches, etc.
    """
    
    def __init__(
        self,
        operator: ConditionOperator,
        value: Any,
        case_sensitive: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionType.VALUE, operator, value, metadata)
        self.case_sensitive = case_sensitive
        self._compiled_regex: Optional[re.Pattern] = None
        
        # Pre-compile regex patterns for performance
        if operator in (ConditionOperator.MATCHES, ConditionOperator.NOT_MATCHES):
            try:
                flags = 0 if case_sensitive else re.IGNORECASE
                self._compiled_regex = re.compile(str(value), flags)
            except re.error as e:
                logger.warning(f"Invalid regex pattern '{value}': {e}")
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate value condition against context."""
        if not self.enabled:
            return True
            
        # Get the value to evaluate
        eval_value = context.get('value')
        if eval_value is None:
            return self.operator == ConditionOperator.NOT_EQUALS
        
        # Convert to string for string operations
        eval_str = str(eval_value)
        target_str = str(self.value) if self.value is not None else ""
        
        # Apply case sensitivity
        if not self.case_sensitive:
            eval_str = eval_str.lower()
            target_str = target_str.lower()
        
        # Evaluate based on operator
        try:
            return self._evaluate_operator(eval_str, eval_value, context)
        except Exception as e:
            logger.error(f"Error evaluating condition {self}: {e}")
            return False
    
    def _evaluate_operator(self, eval_str: str, eval_value: Any, context: Dict[str, Any]) -> bool:
        """Evaluate the specific operator."""
        if self.operator == ConditionOperator.EQUALS:
            return eval_str == str(self.value)
        
        elif self.operator == ConditionOperator.NOT_EQUALS:
            return eval_str != str(self.value)
        
        elif self.operator == ConditionOperator.STARTS_WITH:
            target = str(self.value)
            if not self.case_sensitive:
                target = target.lower()
            return eval_str.startswith(target)
        
        elif self.operator == ConditionOperator.ENDS_WITH:
            target = str(self.value)
            if not self.case_sensitive:
                target = target.lower()
            return eval_str.endswith(target)
        
        elif self.operator == ConditionOperator.CONTAINS:
            target = str(self.value)
            if not self.case_sensitive:
                target = target.lower()
            return target in eval_str
        
        elif self.operator == ConditionOperator.NOT_CONTAINS:
            target = str(self.value)
            if not self.case_sensitive:
                target = target.lower()
            return target not in eval_str
        
        elif self.operator == ConditionOperator.MATCHES:
            if self._compiled_regex:
                return bool(self._compiled_regex.search(eval_str))
            return False
        
        elif self.operator == ConditionOperator.NOT_MATCHES:
            if self._compiled_regex:
                return not bool(self._compiled_regex.search(eval_str))
            return True
        
        elif self.operator == ConditionOperator.LENGTH_GT:
            return len(eval_str) > int(self.value)
        
        elif self.operator == ConditionOperator.LENGTH_LT:
            return len(eval_str) < int(self.value)
        
        elif self.operator == ConditionOperator.LENGTH_EQ:
            return len(eval_str) == int(self.value)
        
        else:
            logger.warning(f"Unknown value operator: {self.operator}")
            return False

class ContextCondition(BaseCondition):
    """
    Condition that evaluates based on context attributes.
    
    Can check for attribute existence, values, or types.
    """
    
    def __init__(
        self,
        operator: ConditionOperator,
        attribute: str,
        value: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionType.CONTEXT, operator, value, metadata)
        self.attribute = attribute
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate context condition against context."""
        if not self.enabled:
            return True
        
        try:
            if self.operator == ConditionOperator.HAS_ATTRIBUTE:
                return self.attribute in context.get('attributes', {})
            
            elif self.operator == ConditionOperator.ATTRIBUTE_EQUALS:
                attr_value = context.get('attributes', {}).get(self.attribute)
                return attr_value == self.value
            
            elif self.operator == ConditionOperator.IS_TYPE:
                actual_type = context.get('type', '')
                expected_type = str(self.value)
                return actual_type == expected_type
            
            else:
                logger.warning(f"Unknown context operator: {self.operator}")
                return False
                
        except Exception as e:
            logger.error(f"Error evaluating context condition {self}: {e}")
            return False

class CustomCondition(BaseCondition):
    """
    Condition that uses a custom evaluation function.
    
    Allows for completely custom logic that can't be expressed
    with the built-in condition types.
    """
    
    def __init__(
        self,
        evaluation_func: callable,
        description: str = "",
        metadata: Optional[Dict[str, Any]] = None
    ):
        super().__init__(ConditionType.CUSTOM, ConditionOperator.AND, None, metadata)
        self.evaluation_func = evaluation_func
        self.description = description
    
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """Evaluate custom condition using provided function."""
        if not self.enabled:
            return True
        
        try:
            return bool(self.evaluation_func(context))
        except Exception as e:
            logger.error(f"Error in custom condition '{self.description}': {e}")
            return False
    
    def __str__(self) -> str:
        """String representation of custom condition."""
        return f"CustomCondition({self.description})"