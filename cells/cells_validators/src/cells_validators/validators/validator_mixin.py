"""
Validation mixin for integrating bones_validator with existing classes.
"""

from ..__base__ import Any, Dict, List, Optional, logger
from ..core.rule_engine import RuleEngine, ValidationResult
from ..rules.base_rule import BaseRule, ValidationViolation
from ..conditions.base_condition import BaseCondition, EvaluationContext
from ..conditions.value_conditions import ValueCondition
from ..types.rule_types import SeverityType, EngineConfig, ConditionOperator

class ValidatorMixin:
    """
    Mixin class for adding bones_validator capabilities to existing classes.
    
    This mixin integrates the rule engine with classes that have a 'value' attribute,
    providing automatic validation with rule networking capabilities.
    """
    
    def __init__(self, *args, **kwargs):
        # Don't call super() to avoid issues with multiple inheritance
        # Let the concrete class handle the MRO properly
        
        # Initialize validation components
        self._rule_engine = RuleEngine()
        self._validation_enabled = True
        self._last_validation_result: Optional[ValidationResult] = None
        self._auto_validate = True  # Validate on value changes
        
        # Setup built-in validation rules
        self._setup_builtin_rules()
    
    @property
    def validation_enabled(self) -> bool:
        """Get validation enabled status."""
        return self._validation_enabled
        
    @validation_enabled.setter
    def validation_enabled(self, value: bool):
        """Enable or disable validation."""
        self._validation_enabled = value
    
    @property
    def auto_validate(self) -> bool:
        """Get auto-validation on value changes status."""
        return self._auto_validate
        
    @auto_validate.setter
    def auto_validate(self, value: bool):
        """Enable or disable auto-validation on value changes."""
        self._auto_validate = value
    
    def add_validation_rule(
        self,
        name: str,
        pattern: Any,
        severity: SeverityType = SeverityType.ERROR,
        description: str = "",
        inverse: bool = False,
        conditions: Optional[List[BaseCondition]] = None
    ) -> None:
        """
        Add a validation rule to the engine.
        
        Args:
            name: Unique rule identifier
            pattern: Validation pattern (regex string or function)
            severity: Violation severity level
            description: Human-readable description
            inverse: Invert rule logic
            conditions: Activation conditions for the rule
        """
        from ..rules.base_rule import Rule
        rule = Rule(name, pattern, severity, description, inverse)
        
        if conditions:
            for condition in conditions:
                rule.add_activation_condition(condition)
        
        self._rule_engine.add_rule(rule)
    
    def add_conditional_validation_rules(
        self,
        condition_spec: Any,
        rules: List[Dict[str, Any]],
        group_name: Optional[str] = None
    ) -> None:
        """
        Add a group of rules activated by a condition.
        
        This is the key method for rule networking - enables the pattern:
        "if value starts with '.' then use dotfile rules"
        "if value starts with '/' then use absolute path rules"
        
        Args:
            condition_spec: Condition specification (tuple, string, or BaseCondition)
            rules: List of rule specifications
            group_name: Optional group name for organization
        """
        # Convert rule specifications to Rule objects
        from ..rules.base_rule import Rule
        rule_objects = []
        for rule_spec in rules:
            rule = Rule(
                name=rule_spec['name'],
                pattern=rule_spec['pattern'],
                severity=rule_spec.get('severity', SeverityType.ERROR),
                description=rule_spec.get('description', ''),
                inverse=rule_spec.get('inverse', False)
            )
            rule_objects.append(rule)
        
        # Add conditional rules to engine
        self._rule_engine.add_conditional_rules(condition_spec, rule_objects, group_name)
    
    def remove_validation_rule(self, name: str) -> bool:
        """Remove a validation rule."""
        return self._rule_engine.remove_rule(name)
    
    def get_validation_rules(self) -> Dict[str, BaseRule]:
        """Get all validation rules."""
        return self._rule_engine.rules.copy()
    
    def validate_value(
        self,
        value: Any = None,
        context: Optional[EvaluationContext] = None
    ) -> ValidationResult:
        """
        Validate a value using the rule engine.
        
        Args:
            value: Value to validate (uses self.value if None)
            context: Optional evaluation context
            
        Returns:
            ValidationResult with validation details
        """
        if not self._validation_enabled:
            return ValidationResult(
                value=value,
                is_valid=True,
                violations=[],
                executed_rules=[],
                skipped_rules=[]
            )
        
        # Use instance value if none provided
        if value is None:
            value = getattr(self, 'value', None)
        
        # Perform validation
        result = self._rule_engine.validate(value, context)
        self._last_validation_result = result
        
        return result
    
    @property
    def is_valid(self) -> bool:
        """Check if current value is valid."""
        if not self._validation_enabled:
            return True
        
        # Validate current value
        result = self.validate_value()
        return result.is_valid
    
    @property
    def validation_violations(self) -> List[ValidationViolation]:
        """Get violations from last validation."""
        if self._last_validation_result:
            return self._last_validation_result.violations
        return []
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation summary."""
        result = self.validate_value()
        
        return {
            'is_valid': result.is_valid,
            'validation_enabled': self._validation_enabled,
            'auto_validate': self._auto_validate,
            'violations': [
                {
                    'rule': v.rule_name,
                    'severity': v.severity.value,
                    'message': v.message
                }
                for v in result.violations
            ],
            'executed_rules': result.executed_rules,
            'skipped_rules': result.skipped_rules,
            'error_count': result.error_count,
            'warning_count': result.warning_count,
            'info_count': result.info_count,
            'execution_time': result.execution_time,
            'engine_stats': self._rule_engine.get_stats()
        }
    
    def clear_validation_cache(self) -> None:
        """Clear validation result cache."""
        self._rule_engine.clear_cache()
    
    def reset_validation_stats(self) -> None:
        """Reset validation statistics."""
        self._rule_engine.reset_stats()
    
    def _setup_builtin_rules(self) -> None:
        """Setup built-in validation rules."""
        # This is a placeholder - subclasses should override
        # to add domain-specific built-in rules
        pass
    
    def _on_value_changed(self, new_value: Any) -> None:
        """
        Hook called when value changes (if auto_validate is enabled).
        
        Concrete classes should call this when their value changes.
        """
        if self._auto_validate and self._validation_enabled:
            self.validate_value(new_value)

# Convenience functions for common validation patterns

def create_dotfile_rules() -> List[Dict[str, Any]]:
    """Create common rules for dotfiles (hidden files)."""
    return [
        {
            'name': 'valid_dotfile',
            'pattern': r'^\.[^/\\]+$',
            'description': 'Must be valid dotfile format',
            'severity': SeverityType.ERROR
        },
        {
            'name': 'no_double_dots',
            'pattern': r'^\.{2,}',
            'description': 'Should not start with multiple dots',
            'severity': SeverityType.WARNING,
            'inverse': True
        },
        {
            'name': 'no_spaces_in_dotfile',
            'pattern': r'\s',
            'description': 'Dotfiles should not contain spaces',
            'severity': SeverityType.WARNING,
            'inverse': True
        }
    ]

def create_absolute_path_rules() -> List[Dict[str, Any]]:
    """Create common rules for absolute paths."""
    return [
        {
            'name': 'valid_absolute_path',
            'pattern': r'^[/\\]([^/\\<>:"|?*\x00-\x1f]+[/\\])*[^/\\<>:"|?*\x00-\x1f]*$',
            'description': 'Must be valid absolute path',
            'severity': SeverityType.ERROR
        },
        {
            'name': 'no_double_separators',
            'pattern': r'[/\\]{2,}',
            'description': 'Should not have consecutive separators',
            'severity': SeverityType.WARNING,
            'inverse': True
        },
        {
            'name': 'no_trailing_separator',
            'pattern': r'[/\\]$',
            'description': 'Should not end with separator',
            'severity': SeverityType.INFO,
            'inverse': True
        }
    ]

def create_filename_rules() -> List[Dict[str, Any]]:
    """Create common rules for filenames."""
    return [
        {
            'name': 'valid_filename',
            'pattern': r'^[^/\\<>:"|?*\x00-\x1f]+$',
            'description': 'Must be valid filename',
            'severity': SeverityType.ERROR
        },
        {
            'name': 'reasonable_filename_length',
            'pattern': lambda x: len(x) <= 255,
            'description': 'Filename should be reasonable length',
            'severity': SeverityType.WARNING
        }
    ]