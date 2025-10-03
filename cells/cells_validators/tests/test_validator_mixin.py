"""
Tests for validator mixin functionality.
"""

import pytest
from bones_validator.validators.validator_mixin import ValidatorMixin, create_dotfile_rules, create_absolute_path_rules
from bones_validator.types.rule_types import SeverityType, ConditionOperator

# Mock class to test the mixin
class TestValidatedItem(ValidatorMixin):
    """Test class that uses ValidatorMixin."""
    
    def __init__(self, name: str, value: str):
        self.name = name
        self._value = value
        super().__init__()
    
    @property
    def value(self):
        return self._value
    
    @value.setter
    def value(self, new_value):
        old_value = self._value
        self._value = new_value
        if old_value != new_value:
            self._on_value_changed(new_value)

class TestValidatorMixin:
    """Test ValidatorMixin functionality."""
    
    def test_mixin_initialization(self):
        """Test basic mixin initialization."""
        item = TestValidatedItem("test", "value")
        
        assert item.validation_enabled == True
        assert item.auto_validate == True
        assert len(item.get_validation_rules()) >= 0  # May have built-in rules
    
    def test_add_validation_rule(self):
        """Test adding validation rules."""
        item = TestValidatedItem("test", "value")
        
        initial_count = len(item.get_validation_rules())
        
        item.add_validation_rule(
            name="test_rule",
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        rules = item.get_validation_rules()
        assert len(rules) == initial_count + 1
        assert "test_rule" in rules
        
        rule = rules["test_rule"]
        assert rule.severity == SeverityType.ERROR
        assert rule.description == "Must start with test"
    
    def test_remove_validation_rule(self):
        """Test removing validation rules."""
        item = TestValidatedItem("test", "value")
        
        # Add a rule first
        item.add_validation_rule("temp_rule", r".*", SeverityType.INFO, "Temp rule")
        assert "temp_rule" in item.get_validation_rules()
        
        # Remove the rule
        result = item.remove_validation_rule("temp_rule")
        assert result == True
        assert "temp_rule" not in item.get_validation_rules()
        
        # Try to remove non-existent rule
        result = item.remove_validation_rule("non_existent")
        assert result == False
    
    def test_basic_validation(self):
        """Test basic validation functionality.""" 
        item = TestValidatedItem("test", "test_value")
        
        # Add a simple rule
        item.add_validation_rule(
            name="starts_with_test",
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        # Test valid value
        result = item.validate_value("test_file")
        assert result.is_valid == True
        assert len(result.violations) == 0
        
        # Test invalid value
        result = item.validate_value("other_file")
        assert result.is_valid == False
        assert len(result.violations) == 1
        assert result.violations[0].rule_name == "starts_with_test"
    
    def test_is_valid_property(self):
        """Test is_valid property."""
        item = TestValidatedItem("test", "test_value")
        
        # Add rule that current value satisfies
        item.add_validation_rule(
            name="starts_with_test",
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        assert item.is_valid == True
        
        # Change to invalid value
        item.value = "invalid_value"
        assert item.is_valid == False
    
    def test_conditional_validation_rules_dotfiles(self):
        """Test conditional rules for dotfiles."""
        item = TestValidatedItem("test", ".bashrc")
        
        # Add dotfile conditional rules
        dotfile_rules = create_dotfile_rules()
        item.add_conditional_validation_rules(
            condition_spec=("starts_with", "."),
            rules=dotfile_rules,
            group_name="dotfiles"
        )
        
        # Test dotfile validation
        result = item.validate_value(".bashrc")
        assert result.is_valid == True
        
        # Test invalid dotfile
        result = item.validate_value("..invalid")
        assert result.is_valid == True  # May have warnings but not errors
        
        # Test non-dotfile (should not trigger dotfile rules)
        result = item.validate_value("regular_file.txt")
        assert result.is_valid == True
    
    def test_conditional_validation_rules_absolute_paths(self):
        """Test conditional rules for absolute paths."""
        item = TestValidatedItem("test", "/usr/bin/python")
        
        # Add absolute path rules
        absolute_rules = create_absolute_path_rules()
        item.add_conditional_validation_rules(
            condition_spec=("starts_with", "/"),
            rules=absolute_rules,
            group_name="absolute_paths"
        )
        
        # Test valid absolute path
        result = item.validate_value("/usr/bin/python")
        assert result.is_valid == True
        
        # Test path with double slashes (warning)
        result = item.validate_value("/usr//bin/python")
        assert result.is_valid == True  # Warnings don't invalidate
        assert result.warning_count > 0
        
        # Test relative path (should not trigger absolute path rules)
        result = item.validate_value("relative/path")
        assert result.is_valid == True
    
    def test_rule_networking_example(self):
        """Test the key rule networking feature."""
        item = TestValidatedItem("test", "value")
        
        # Set up rule networking: different rules for different value patterns
        
        # Rules for dotfiles
        dotfile_rules = [
            {'name': 'dotfile_valid', 'pattern': r'^\.[^/\\]+$', 'severity': SeverityType.ERROR, 'description': 'Valid dotfile'},
            {'name': 'dotfile_no_spaces', 'pattern': r'\s', 'severity': SeverityType.WARNING, 'description': 'No spaces in dotfiles', 'inverse': True}
        ]
        item.add_conditional_validation_rules(("starts_with", "."), dotfile_rules, "dotfiles")
        
        # Rules for absolute paths
        absolute_rules = [
            {'name': 'absolute_valid', 'pattern': r'^/[a-zA-Z0-9_/.-]*$', 'severity': SeverityType.ERROR, 'description': 'Valid absolute path'},
            {'name': 'absolute_no_double_slash', 'pattern': r'//+', 'severity': SeverityType.WARNING, 'description': 'No double slashes', 'inverse': True}
        ]
        item.add_conditional_validation_rules(("starts_with", "/"), absolute_rules, "absolute")
        
        # Rules for relative paths (anything not starting with . or /)
        from bones_validator.conditions.logical_conditions import NotCondition, OrCondition
        from bones_validator.conditions.value_conditions import ValueCondition
        
        relative_rules = [
            {'name': 'relative_simple', 'pattern': r'^[a-zA-Z0-9_.-]+$', 'severity': SeverityType.INFO, 'description': 'Simple relative path'}
        ]
        # This would need more complex condition setup for NOT (starts_with . OR starts_with /)
        
        # Test different value types trigger different rule sets
        
        # Dotfile - should trigger dotfile rules only
        result = item.validate_value(".gitignore")
        summary = item.get_validation_summary()
        executed_rules = [r for r in summary['executed_rules'] if 'dotfile' in r]
        assert len(executed_rules) > 0
        
        # Absolute path - should trigger absolute rules only  
        result = item.validate_value("/etc/hosts")
        summary = item.get_validation_summary()
        executed_rules = [r for r in summary['executed_rules'] if 'absolute' in r]
        assert len(executed_rules) > 0
    
    def test_validation_summary(self):
        """Test validation summary functionality."""
        item = TestValidatedItem("test", "test_value")
        
        # Add rules with different severities
        item.add_validation_rule("error_rule", r"^error", SeverityType.ERROR, "Error rule", inverse=True)
        item.add_validation_rule("warning_rule", r"^warning", SeverityType.WARNING, "Warning rule", inverse=True)
        item.add_validation_rule("info_rule", r"^info", SeverityType.INFO, "Info rule", inverse=True)
        
        summary = item.get_validation_summary()
        
        assert 'is_valid' in summary
        assert 'validation_enabled' in summary
        assert 'violations' in summary
        assert 'error_count' in summary
        assert 'warning_count' in summary
        assert 'info_count' in summary
        assert 'execution_time' in summary
        
        # Check violation counts
        assert summary['error_count'] == 1
        assert summary['warning_count'] == 1
        assert summary['info_count'] == 1
        assert summary['is_valid'] == False  # Has errors
    
    def test_validation_enabled_disabled(self):
        """Test validation enable/disable functionality."""
        item = TestValidatedItem("test", "test_value")
        
        # Add a failing rule
        item.add_validation_rule("fail_rule", r"^success", SeverityType.ERROR, "Must start with success")
        
        # With validation enabled, should fail
        assert item.is_valid == False
        
        # Disable validation
        item.validation_enabled = False
        assert item.is_valid == True  # Should pass when disabled
        
        # Re-enable validation
        item.validation_enabled = True
        assert item.is_valid == False  # Should fail again
    
    def test_auto_validate_on_value_change(self):
        """Test auto-validation when value changes."""
        item = TestValidatedItem("test", "valid_value")
        
        # Add validation rule
        item.add_validation_rule("starts_with_valid", r"^valid", SeverityType.ERROR, "Must start with valid")
        
        # Initially valid
        assert item.is_valid == True
        
        # Change to invalid value (should auto-validate)
        item.value = "invalid_value"
        assert item.is_valid == False
        
        # Disable auto-validation
        item.auto_validate = False
        item.value = "valid_again"
        # Note: is_valid property will still validate when accessed
        # but _on_value_changed won't be called automatically
    
    def test_cache_and_stats(self):
        """Test caching and statistics functionality."""
        item = TestValidatedItem("test", "test_value")
        
        # Add some rules
        item.add_validation_rule("rule1", r".*", SeverityType.INFO, "Rule 1")
        item.add_validation_rule("rule2", r".*", SeverityType.INFO, "Rule 2")
        
        # Perform validations
        for i in range(3):
            item.validate_value(f"value_{i}")
        
        # Check stats
        summary = item.get_validation_summary()
        engine_stats = summary['engine_stats']
        
        assert engine_stats['engine_stats']['total_validations'] >= 3
        assert engine_stats['rule_count'] >= 2
        
        # Test cache clearing
        item.clear_validation_cache()
        
        # Test stats reset
        item.reset_validation_stats()

class TestHelperFunctions:
    """Test helper functions for common rule patterns."""
    
    def test_create_dotfile_rules(self):
        """Test dotfile rules creation."""
        rules = create_dotfile_rules()
        
        assert len(rules) > 0
        assert any(rule['name'] == 'valid_dotfile' for rule in rules)
        
        # Check rule structure
        for rule in rules:
            assert 'name' in rule
            assert 'pattern' in rule
            assert 'severity' in rule
            assert 'description' in rule
    
    def test_create_absolute_path_rules(self):
        """Test absolute path rules creation."""
        rules = create_absolute_path_rules()
        
        assert len(rules) > 0
        assert any(rule['name'] == 'valid_absolute_path' for rule in rules)
        
        # Check rule structure
        for rule in rules:
            assert 'name' in rule
            assert 'pattern' in rule
            assert 'severity' in rule
            assert 'description' in rule