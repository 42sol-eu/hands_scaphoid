"""
Tests for rule base classes and validation violations.
"""

import pytest
from unittest.mock import MagicMock
from bones_validator.rules.base_rule import BaseRule, Rule, ConditionalRule, ValidationViolation
from bones_validator.types.rule_types import SeverityType
from bones_validator.conditions.value_conditions import ValueCondition
from bones_validator.types.rule_types import ConditionOperator

class TestValidationViolation:
    """Test ValidationViolation class."""
    
    def test_creation(self):
        """Test basic violation creation."""
        violation = ValidationViolation(
            rule_name="test_rule",
            message="Test message",
            severity=SeverityType.ERROR,
            value="test_value"
        )
        
        assert violation.rule_name == "test_rule"
        assert violation.message == "Test message"
        assert violation.severity == SeverityType.ERROR
        assert violation.value == "test_value"
        assert violation.context is None
    
    def test_creation_with_context(self):
        """Test violation creation with context."""
        context = {"field": "name", "index": 5}
        violation = ValidationViolation(
            rule_name="test_rule",
            message="Test message",
            severity=SeverityType.WARNING,
            value="test_value",
            context=context
        )
        
        assert violation.context == context
    
    def test_string_representation(self):
        """Test string representation."""
        violation = ValidationViolation(
            rule_name="test_rule",
            message="Test message",
            severity=SeverityType.ERROR,
            value="test_value"
        )
        
        str_repr = str(violation)
        assert "test_rule" in str_repr
        assert "ERROR" in str_repr
        assert "Test message" in str_repr

class TestBaseRule:
    """Test BaseRule abstract class."""
    
    def test_cannot_instantiate_directly(self):
        """Test that BaseRule cannot be instantiated directly."""
        with pytest.raises(TypeError):
            BaseRule(name="test", description="test")

class TestRule:
    """Test concrete Rule class."""
    
    def test_creation(self):
        """Test basic rule creation."""
        rule = Rule(
            name="test_rule",
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        assert rule.name == "test_rule"
        assert rule.pattern == r"^test"
        assert rule.severity == SeverityType.ERROR
        assert rule.description == "Must start with test"
        assert rule.inverse == False
        assert rule.dependencies == []
    
    def test_creation_with_dependencies(self):
        """Test rule creation with dependencies."""
        rule = Rule(
            name="test_rule",
            pattern=r"^test",
            severity=SeverityType.WARNING,
            description="Test rule",
            dependencies=["dep1", "dep2"]
        )
        
        assert rule.dependencies == ["dep1", "dep2"]
    
    def test_validate_valid_pattern(self):
        """Test validation with valid pattern match."""
        rule = Rule(
            name="test_rule",
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        result = rule.validate("test_value", {})
        assert result is None  # No violation
    
    def test_validate_invalid_pattern(self):
        """Test validation with invalid pattern match."""
        rule = Rule(
            name="test_rule", 
            pattern=r"^test",
            severity=SeverityType.ERROR,
            description="Must start with test"
        )
        
        result = rule.validate("other_value", {})
        assert result is not None
        assert isinstance(result, ValidationViolation)
        assert result.rule_name == "test_rule"
        assert result.severity == SeverityType.ERROR
        assert result.value == "other_value"
    
    def test_validate_inverse_pattern(self):
        """Test validation with inverse pattern matching."""
        rule = Rule(
            name="no_spaces",
            pattern=r"\s",
            severity=SeverityType.WARNING,
            description="No spaces allowed",
            inverse=True
        )
        
        # Should pass (no spaces found, inverse=True)
        result = rule.validate("no_spaces_here", {})
        assert result is None
        
        # Should fail (spaces found, but inverse=True means violation)
        result = rule.validate("has spaces", {})
        assert result is not None
        assert result.rule_name == "no_spaces"
        assert result.severity == SeverityType.WARNING
    
    def test_validate_with_context(self):
        """Test validation with context."""
        rule = Rule(
            name="test_rule",
            pattern=r"^test",
            severity=SeverityType.INFO,
            description="Test rule"
        )
        
        context = {"field": "name", "object_id": 123}
        result = rule.validate("invalid", context)
        
        assert result is not None
        assert result.context == context
    
    def test_validate_pattern_compilation_error(self):
        """Test validation with invalid regex pattern."""
        rule = Rule(
            name="bad_rule",
            pattern=r"[invalid",  # Invalid regex
            severity=SeverityType.ERROR,
            description="Bad regex"
        )
        
        # Should handle regex compilation error gracefully
        result = rule.validate("test", {})
        assert result is not None
        assert "regex" in result.message.lower() or "pattern" in result.message.lower()

class TestConditionalRule:
    """Test ConditionalRule class."""
    
    def test_creation(self):
        """Test conditional rule creation."""
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        rule = ConditionalRule(
            name="dotfile_rule",
            pattern=r"^\.[^/\\]+$",
            severity=SeverityType.ERROR,
            description="Valid dotfile",
            activation_condition=condition
        )
        
        assert rule.name == "dotfile_rule"
        assert rule.activation_condition == condition
        assert rule.pattern == r"^\.[^/\\]+$"
    
    def test_should_activate_true(self):
        """Test activation condition returning True."""
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        rule = ConditionalRule(
            name="dotfile_rule",
            pattern=r"^\.[^/\\]+$",
            severity=SeverityType.ERROR,
            description="Valid dotfile",
            activation_condition=condition
        )
        
        assert rule.should_activate(".bashrc", {}) == True
    
    def test_should_activate_false(self):
        """Test activation condition returning False."""
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        rule = ConditionalRule(
            name="dotfile_rule",
            pattern=r"^\.[^/\\]+$",
            severity=SeverityType.ERROR,
            description="Valid dotfile", 
            activation_condition=condition
        )
        
        assert rule.should_activate("regular_file.txt", {}) == False
    
    def test_validate_when_activated(self):
        """Test validation when rule is activated."""
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        rule = ConditionalRule(
            name="dotfile_rule",
            pattern=r"^\.[^/\\]+$",
            severity=SeverityType.ERROR,
            description="Valid dotfile",
            activation_condition=condition
        )
        
        # Valid dotfile - should activate and pass
        result = rule.validate(".bashrc", {})
        assert result is None
        
        # Invalid dotfile - should activate and fail
        result = rule.validate(".has/slash", {})
        assert result is not None
        assert result.rule_name == "dotfile_rule"
    
    def test_validate_when_not_activated(self):
        """Test validation when rule is not activated."""
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        rule = ConditionalRule(
            name="dotfile_rule",
            pattern=r"^\.[^/\\]+$",
            severity=SeverityType.ERROR,
            description="Valid dotfile",
            activation_condition=condition
        )
        
        # Regular file - should not activate, returns None
        result = rule.validate("regular_file.txt", {})
        assert result is None
    
    def test_validate_with_condition_error(self):
        """Test validation when condition evaluation fails.""" 
        # Mock condition that raises exception
        condition = MagicMock()
        condition.evaluate.side_effect = Exception("Condition error")
        
        rule = ConditionalRule(
            name="test_rule",
            pattern=r".*",
            severity=SeverityType.ERROR,
            description="Test rule",
            activation_condition=condition
        )
        
        # Should handle condition error gracefully
        result = rule.validate("test_value", {})
        assert result is not None
        assert "condition" in result.message.lower() or "error" in result.message.lower()
    
    def test_inheritance_from_rule(self):
        """Test that ConditionalRule inherits from Rule properly."""
        condition = ValueCondition(ConditionOperator.EQUALS, "test")
        rule = ConditionalRule(
            name="conditional_rule",
            pattern=r"^test$",
            severity=SeverityType.WARNING,
            description="Conditional test",
            activation_condition=condition,
            inverse=True,
            dependencies=["dep1"]
        )
        
        # Should have Rule attributes
        assert rule.inverse == True
        assert rule.dependencies == ["dep1"]
        assert rule.severity == SeverityType.WARNING
        
        # Should work with activation
        assert rule.should_activate("test", {}) == True
        assert rule.should_activate("other", {}) == False
    
    def test_complex_condition_integration(self):
        """Test integration with complex conditions."""
        from bones_validator.conditions.logical_conditions import AndCondition
        
        # Create compound condition: starts with "." AND contains "rc"  
        starts_condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        contains_condition = ValueCondition(ConditionOperator.CONTAINS, "rc")
        compound_condition = AndCondition([starts_condition, contains_condition])
        
        rule = ConditionalRule(
            name="rc_dotfile_rule",
            pattern=r"^\.[^/\\]*rc[^/\\]*$",
            severity=SeverityType.INFO,
            description="RC dotfile",
            activation_condition=compound_condition
        )
        
        # Should activate for .bashrc (starts with . AND contains rc)
        assert rule.should_activate(".bashrc", {}) == True
        result = rule.validate(".bashrc", {})
        assert result is None
        
        # Should not activate for .gitignore (starts with . but no rc)
        assert rule.should_activate(".gitignore", {}) == False
        result = rule.validate(".gitignore", {})
        assert result is None
        
        # Should not activate for bashrc (contains rc but doesn't start with .)
        assert rule.should_activate("bashrc", {}) == False
        result = rule.validate("bashrc", {})
        assert result is None