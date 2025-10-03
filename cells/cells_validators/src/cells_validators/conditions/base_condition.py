"""
Base condition classes for rule evaluation.
"""

from ..__base__ import ABC, abstractmethod, Any, Dict, Optional, logger
from ..types.rule_types import ConditionType, ConditionOperator

class BaseCondition(ABC):
    """
    Abstract base class for all rule conditions.
    
    Conditions determine when rules should be activated or applied.
    They can evaluate values, context, or logical combinations.
    """
    
    def __init__(
        self, 
        condition_type: ConditionType,
        operator: ConditionOperator,
        value: Any = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.condition_type = condition_type
        self.operator = operator
        self.value = value
        self.metadata = metadata or {}
        self._cache: Dict[str, Any] = {}
        self._enabled = True
    
    @property
    def enabled(self) -> bool:
        """Check if condition is enabled."""
        return self._enabled
    
    @enabled.setter
    def enabled(self, value: bool) -> None:
        """Enable or disable condition."""
        self._enabled = value
    
    @abstractmethod
    def evaluate(self, context: Dict[str, Any]) -> bool:
        """
        Evaluate the condition against the given context.
        
        Args:
            context: Evaluation context containing value and metadata
            
        Returns:
            bool: True if condition is met, False otherwise
        """
        pass
    
    def clear_cache(self) -> None:
        """Clear the condition cache."""
        self._cache.clear()
    
    def __str__(self) -> str:
        """String representation of the condition."""
        return f"{self.__class__.__name__}({self.operator}={self.value})"
    
    def __repr__(self) -> str:
        """Detailed representation of the condition."""
        return (
            f"{self.__class__.__name__}("
            f"type={self.condition_type}, "
            f"operator={self.operator}, "
            f"value={self.value}, "
            f"enabled={self.enabled})"
        )

class EvaluationContext:
    """
    Context object for condition evaluation.
    
    Provides structured access to values, attributes, and metadata
    during rule and condition evaluation.
    """
    
    def __init__(
        self,
        value: Any,
        attributes: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parent_context: Optional['EvaluationContext'] = None
    ):
        self.value = value
        self.attributes = attributes or {}
        self.metadata = metadata or {}
        self.parent_context = parent_context
        self._computed_values: Dict[str, Any] = {}
    
    def get_attribute(self, name: str, default: Any = None) -> Any:
        """Get an attribute value with optional default."""
        if name in self.attributes:
            return self.attributes[name]
        elif self.parent_context:
            return self.parent_context.get_attribute(name, default)
        else:
            return default
    
    def has_attribute(self, name: str) -> bool:
        """Check if attribute exists in context or parent contexts."""
        if name in self.attributes:
            return True
        elif self.parent_context:
            return self.parent_context.has_attribute(name)
        else:
            return False
    
    def set_computed_value(self, key: str, value: Any) -> None:
        """Set a computed value for caching."""
        self._computed_values[key] = value
    
    def get_computed_value(self, key: str, default: Any = None) -> Any:
        """Get a computed value from cache."""
        return self._computed_values.get(key, default)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert context to dictionary for condition evaluation."""
        return {
            'value': self.value,
            'attributes': self.attributes,
            'metadata': self.metadata,
            'computed': self._computed_values,
            'type': type(self.value).__name__,
            'str_value': str(self.value),
            'length': len(str(self.value)) if self.value is not None else 0,
        }
    
    def __str__(self) -> str:
        """String representation of context."""
        return f"EvaluationContext(value={self.value}, attrs={len(self.attributes)})"
    
    def __repr__(self) -> str:
        """Detailed representation of context.""" 
        return (
            f"EvaluationContext("
            f"value={repr(self.value)}, "
            f"attributes={self.attributes}, "
            f"metadata={self.metadata})"
        )