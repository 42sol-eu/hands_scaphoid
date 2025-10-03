, #!/usr/bin/env python3
"""
Test module for ValidationMixin functionality.

File:
    name: test_ValidationMixin.py
    uuid: f8e7d6c5-b4a3-4e7d-9e8b-1a2b3c4d5e6f
    date: 2025-10-03

Description:
    Comprehensive tests for ValidationMixin functionality including rule management,
    validation execution, severity levels, and configuration

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- DUT[testing]: Device Under Test (the ValidationMixin class)
- OS[system]: Operating System
"""

# [Test imports]
import pytest
import platform
from unittest.mock import patch

# [Device under test imports]
from hands_scaphoid.objects.ValidatorMixin import ValidationMixin, ValidationRule, ValidationViolation
from hands_scaphoid.types.SeverityType import SeverityType

# [Mock class for testing mixin]
class TestItem(ValidationMixin):
    """Test class that uses ValidationMixin for testing purposes."""
    
    def __init__(self, value: str, **kwargs):
        self.value = value
        super().__init__(**kwargs)

# [Fixtures]

@pytest.fixture
def basic_validator():
    """Create a basic ValidationMixin test instance."""
    return TestItem("test_value")

@pytest.fixture
def strict_validator():
    """Create a strict mode ValidationMixin test instance."""
    return TestItem("test_value", strict_mode=True)

@pytest.fixture
def cross_platform_validator():
    """Create a cross-platform ValidationMixin test instance."""
    return TestItem("test_value", cross_platform=True)

@pytest.fixture
def sample_validation_rule():
    """Create a sample validation rule."""
    return ValidationRule(
        name="test_rule",
        pattern=r"^test_",
        severity=SeverityType.ERROR,
        description="Must start with 'test_'"
    )

# [Initialization Tests]

def test_ValidationMixin_initialization(basic_validator):
    """Test basic ValidationMixin initialization."""
    assert not basic_validator.strict_mode
    assert not basic_validator.cross_platform
    assert basic_validator.validation_enabled
    assert len(basic_validator.get_rules()) > 0  # Should have built-in rules

def test_ValidationMixin_strict_mode_initialization(strict_validator):
    """Test ValidationMixin initialization with strict mode."""
    assert strict_validator.strict_mode
    assert not strict_validator.cross_platform
    assert strict_validator.validation_enabled

def test_ValidationMixin_cross_platform_initialization(cross_platform_validator):
    """Test ValidationMixin initialization with cross-platform mode."""
    assert not cross_platform_validator.strict_mode
    assert cross_platform_validator.cross_platform
    assert cross_platform_validator.validation_enabled

# [Property Tests]

def test_ValidationMixin_strict_mode_property(basic_validator):
    """Test strict_mode property getter and setter."""
    # Initial state
    assert not basic_validator.strict_mode
    
    # Set to True
    basic_validator.strict_mode = True
    assert basic_validator.strict_mode
    
    # Set to False
    basic_validator.strict_mode = False
    assert not basic_validator.strict_mode

def test_ValidationMixin_cross_platform_property(basic_validator):
    """Test cross_platform property getter and setter."""
    # Initial state
    assert not basic_validator.cross_platform
    
    # Set to True
    basic_validator.cross_platform = True
    assert basic_validator.cross_platform
    
    # Set to False
    basic_validator.cross_platform = False
    assert not basic_validator.cross_platform

def test_ValidationMixin_validation_enabled_property(basic_validator):
    """Test validation_enabled property getter and setter."""
    # Initial state
    assert basic_validator.validation_enabled
    
    # Disable validation
    basic_validator.validation_enabled = False
    assert not basic_validator.validation_enabled
    
    # Enable validation
    basic_validator.validation_enabled = True
    assert basic_validator.validation_enabled

# [Rule Management Tests]

def test_add_rule_basic(basic_validator):
    """Test adding a basic validation rule."""
    initial_rule_count = len(basic_validator.get_rules())
    
    basic_validator.add_rule(
        name="custom_rule",
        pattern=r"^custom",
        severity=SeverityType.ERROR,
        description="Must start with 'custom'"
    )
    
    rules = basic_validator.get_rules()
    assert len(rules) == initial_rule_count + 1
    assert "custom_rule" in rules
    
    rule = rules["custom_rule"]
    assert rule.name == "custom_rule"
    assert rule.pattern == r"^custom"
    assert rule.severity == SeverityType.ERROR
    assert rule.description == "Must start with 'custom'"
    assert not rule.inverse
    assert rule.enabled

def test_add_rule_with_inverse(basic_validator):
    """Test adding a validation rule with inverse logic."""
    basic_validator.add_rule(
        name="inverse_rule",
        pattern=r"bad_pattern",
        severity=SeverityType.WARNING,
        description="Should not contain bad pattern",
        inverse=True
    )
    
    rule = basic_validator.get_rules()["inverse_rule"]
    assert rule.inverse

def test_add_rule_custom_function(basic_validator):
    """Test adding a validation rule with custom function."""
    def custom_validator(value: str) -> bool:
        return len(value) > 5
    
    basic_validator.add_rule(
        name="length_rule",
        pattern=custom_validator,
        severity=SeverityType.INFO,
        description="Must be longer than 5 characters"
    )
    
    rule = basic_validator.get_rules()["length_rule"]
    assert callable(rule.pattern)
    assert rule.severity == SeverityType.INFO

def test_remove_rule(basic_validator):
    """Test removing a validation rule."""
    # Add a rule first
    basic_validator.add_rule("temp_rule", r".*", SeverityType.INFO, "Temporary rule")
    assert "temp_rule" in basic_validator.get_rules()
    
    # Remove the rule
    result = basic_validator.remove_rule("temp_rule")
    assert result
    assert "temp_rule" not in basic_validator.get_rules()
    
    # Try to remove non-existent rule
    result = basic_validator.remove_rule("non_existent")
    assert not result

def test_enable_disable_rule(basic_validator):
    """Test enabling and disabling validation rules."""
    # Add a rule
    basic_validator.add_rule("toggle_rule", r".*", SeverityType.ERROR, "Toggle test")
    
    # Disable the rule
    result = basic_validator.disable_rule("toggle_rule")
    assert result
    rule = basic_validator.get_rules()["toggle_rule"]
    assert not rule.enabled
    
    # Enable the rule
    result = basic_validator.enable_rule("toggle_rule")
    assert result
    rule = basic_validator.get_rules()["toggle_rule"]
    assert rule.enabled
    
    # Try to enable/disable non-existent rule
    assert not basic_validator.enable_rule("non_existent")
    assert not basic_validator.disable_rule("non_existent")

# [Validation Tests]

def test_validate_with_no_rules():
    """Test validation with no rules returns valid."""
    validator = TestItem("any_value")
    validator._validation_rules.clear()  # Remove all rules
    
    is_valid, violations = validator.validate()
    assert is_valid
    assert len(violations) == 0

def test_validate_disabled():
    """Test validation when disabled."""
    validator = TestItem("any_value")
    validator.validation_enabled = False
    
    is_valid, violations = validator.validate()
    assert is_valid
    assert len(violations) == 0

def test_validate_regex_rule_success():
    """Test successful validation with regex rule."""
    validator = TestItem("valid_test_value")
    validator._validation_rules.clear()  # Start clean
    
    validator.add_rule(
        name="starts_with_valid",
        pattern=r"^valid_",
        severity=SeverityType.ERROR,
        description="Must start with 'valid_'"
    )
    
    is_valid, violations = validator.validate()
    assert is_valid
    assert len(violations) == 0

def test_validate_regex_rule_failure():
    """Test failed validation with regex rule."""
    validator = TestItem("invalid_test_value")
    validator._validation_rules.clear()  # Start clean
    
    validator.add_rule(
        name="starts_with_valid",
        pattern=r"^valid_",
        severity=SeverityType.ERROR,
        description="Must start with 'valid_'"
    )
    
    is_valid, violations = validator.validate()
    assert not is_valid
    assert len(violations) == 1
    
    violation = violations[0]
    assert violation.rule_name == "starts_with_valid"
    assert violation.severity == SeverityType.ERROR
    assert "Must start with 'valid_'" in violation.message
    assert violation.value == "invalid_test_value"

def test_validate_inverse_rule():
    """Test validation with inverse rule logic."""
    validator = TestItem("contains_bad_word")
    validator._validation_rules.clear()  # Start clean
    
    validator.add_rule(
        name="no_bad_words",
        pattern=r"bad_word",
        severity=SeverityType.ERROR,
        description="Must not contain bad words",
        inverse=True
    )
    
    is_valid, violations = validator.validate()
    assert not is_valid
    assert len(violations) == 1

def test_validate_custom_function_rule():
    """Test validation with custom function rule."""
    validator = TestItem("short")
    validator._validation_rules.clear()  # Start clean
    
    def min_length_validator(value: str) -> bool:
        return len(value) >= 10
    
    validator.add_rule(
        name="min_length",
        pattern=min_length_validator,
        severity=SeverityType.WARNING,
        description="Must be at least 10 characters"
    )
    
    is_valid, violations = validator.validate()
    assert is_valid  # Warnings don't make it invalid
    assert len(violations) == 1
    assert violations[0].severity == SeverityType.WARNING

def test_validate_multiple_rules():
    """Test validation with multiple rules of different severities."""
    validator = TestItem("test_value")
    validator._validation_rules.clear()  # Start clean
    
    # Add multiple rules
    validator.add_rule("error_rule", r"^error", SeverityType.ERROR, "Error rule", inverse=True)
    validator.add_rule("warning_rule", r"_warning", SeverityType.WARNING, "Warning rule", inverse=True) 
    validator.add_rule("info_rule", r"^test", SeverityType.INFO, "Info rule")
    
    is_valid, violations = validator.validate()
    assert is_valid  # Only ERROR rules affect validity
    assert len(violations) == 1  # Only INFO rule should match
    assert violations[0].severity == SeverityType.INFO

# [Built-in Rules Tests]

def test_builtin_invalid_chars_rule():
    """Test built-in rule for invalid characters."""
    validator = TestItem("path<with>invalid:chars")
    
    is_valid, violations = validator.validate()
    assert not is_valid
    
    # Should have violation for invalid_chars rule
    invalid_chars_violations = [v for v in violations if v.rule_name == "invalid_chars"]
    assert len(invalid_chars_violations) > 0
    assert invalid_chars_violations[0].severity == SeverityType.ERROR

def test_builtin_uncommon_chars_rule():
    """Test built-in rule for uncommon characters."""
    validator = TestItem("path#with$uncommon%chars")
    
    is_valid, violations = validator.validate()
    # Should be valid (warnings don't invalidate) but have warnings
    assert is_valid
    
    # Should have violation for uncommon_chars rule
    uncommon_chars_violations = [v for v in violations if v.rule_name == "uncommon_chars"]
    assert len(uncommon_chars_violations) > 0
    assert uncommon_chars_violations[0].severity == SeverityType.WARNING

def test_builtin_whitespace_trim_rule():
    """Test built-in rule for leading/trailing whitespace."""
    validator = TestItem("  path_with_spaces  ")
    
    is_valid, violations = validator.validate()
    assert is_valid  # Warnings don't invalidate
    
    whitespace_violations = [v for v in violations if v.rule_name == "whitespace_trim"]
    assert len(whitespace_violations) > 0
    assert whitespace_violations[0].severity == SeverityType.WARNING

# [Strict Mode Tests]

def test_strict_mode_changes_severity():
    """Test that strict mode changes warning severity to error."""
    validator = TestItem("path#with$uncommon%chars", strict_mode=True)
    
    is_valid, violations = validator.validate()
    assert not is_valid  # Should be invalid in strict mode
    
    # Uncommon chars should now be ERROR in strict mode
    uncommon_chars_violations = [v for v in violations if v.rule_name == "uncommon_chars"]
    assert len(uncommon_chars_violations) > 0
    assert uncommon_chars_violations[0].severity == SeverityType.ERROR

def test_strict_mode_property_update():
    """Test that changing strict_mode property updates rule severities."""
    validator = TestItem("path#with$uncommon%chars")
    
    # Initially not strict - should be valid with warnings
    is_valid, violations = validator.validate()
    assert is_valid
    
    # Enable strict mode
    validator.strict_mode = True
    
    # Now should be invalid
    is_valid, violations = validator.validate()
    assert not is_valid

# [Cross-Platform Tests]

@patch('platform.system')
def test_cross_platform_windows(mock_system):
    """Test cross-platform validation on Windows."""
    mock_system.return_value = "Windows"
    
    validator = TestItem("path/with/unix/separators", cross_platform=True)
    
    is_valid, violations = validator.validate()
    assert is_valid  # Should be valid but have warnings
    
    # Should warn about Unix separators on Windows
    separator_violations = [v for v in violations if v.rule_name == "cross_platform_separator"]
    assert len(separator_violations) > 0
    assert separator_violations[0].severity == SeverityType.WARNING

@patch('platform.system')
def test_cross_platform_unix(mock_system):
    """Test cross-platform validation on Unix-like system."""
    mock_system.return_value = "Linux"
    
    validator = TestItem("path\\with\\windows\\separators", cross_platform=True)
    
    is_valid, violations = validator.validate()
    assert is_valid  # Should be valid but have warnings
    
    # Should warn about Windows separators on Unix
    separator_violations = [v for v in violations if v.rule_name == "cross_platform_separator"]
    assert len(separator_violations) > 0
    assert separator_violations[0].severity == SeverityType.WARNING

# [Serialization Tests]

def test_to_dict_serialization(basic_validator):
    """Test ValidationMixin serialization to dictionary."""
    # Add a custom rule for testing
    basic_validator.add_rule("custom_rule", r"test", SeverityType.WARNING, "Test rule")
    
    data = basic_validator.to_dict()
    
    assert "strict_mode" in data
    assert "cross_platform" in data
    assert "validation_enabled" in data
    assert "validation_rules" in data
    
    assert data["strict_mode"] == basic_validator.strict_mode
    assert data["cross_platform"] == basic_validator.cross_platform
    assert data["validation_enabled"] == basic_validator.validation_enabled
    
    # Check that custom rule is included
    assert "custom_rule" in data["validation_rules"]
    rule_data = data["validation_rules"]["custom_rule"]
    assert rule_data["pattern"] == r"test"
    assert rule_data["severity"] == "warning"
    assert rule_data["description"] == "Test rule"

def test_from_dict_deserialization():
    """Test ValidationMixin deserialization from dictionary."""
    data = {
        "strict_mode": True,
        "cross_platform": True,
        "validation_enabled": False,
        "validation_rules": {
            "custom_rule": {
                "pattern": r"^custom",
                "severity": "error",
                "description": "Custom test rule",
                "inverse": True,
                "enabled": True
            }
        }
    }
    
    validator = ValidationMixin.from_dict(data)
    
    assert validator.strict_mode
    assert validator.cross_platform
    assert not validator.validation_enabled
    
    # Check that custom rule was loaded
    rules = validator.get_rules()
    assert "custom_rule" in rules
    rule = rules["custom_rule"]
    assert rule.pattern == r"^custom"
    assert rule.severity == SeverityType.ERROR
    assert rule.description == "Custom test rule"
    assert rule.inverse

# [Custom Rule Group Tests]

def test_add_custom_rule_group(basic_validator):
    """Test adding a group of related rules."""
    rules = [
        {"name": "rule1", "pattern": r"^start", "severity": SeverityType.ERROR, "description": "Rule 1"},
        {"name": "rule2", "pattern": r"end$", "severity": SeverityType.WARNING, "description": "Rule 2"}
    ]
    
    basic_validator.add_custom_rule_group("test_group", rules)
    
    validator_rules = basic_validator.get_rules()
    assert "rule1" in validator_rules
    assert "rule2" in validator_rules
    
    assert validator_rules["rule1"].severity == SeverityType.ERROR
    assert validator_rules["rule2"].severity == SeverityType.WARNING

# [Error Handling Tests]

def test_validate_with_exception_in_rule():
    """Test validation handles exceptions in custom rules gracefully."""
    validator = TestItem("test_value")
    validator._validation_rules.clear()
    
    def failing_validator(value: str) -> bool:
        raise ValueError("Intentional test error")
    
    validator.add_rule(
        name="failing_rule",
        pattern=failing_validator,
        severity=SeverityType.INFO,
        description="This rule will fail"
    )
    
    is_valid, violations = validator.validate()
    assert not is_valid  # Should be invalid due to rule error
    assert len(violations) == 1
    assert violations[0].severity == SeverityType.ERROR
    assert "Rule check failed" in violations[0].message

# [Integration Tests]

def test_full_validation_workflow():
    """Test complete validation workflow with multiple rule types."""
    validator = TestItem("valid_test_path", strict_mode=False, cross_platform=False)
    validator._validation_rules.clear()  # Start fresh
    
    # Add various rule types
    validator.add_rule("prefix_check", r"^valid_", SeverityType.ERROR, "Must start with valid_")
    validator.add_rule("no_spaces", r"\s", SeverityType.WARNING, "Should not contain spaces", inverse=True)
    validator.add_rule("min_length", lambda x: len(x) >= 5, SeverityType.INFO, "Should be at least 5 chars")
    
    # Test with valid value
    is_valid, violations = validator.validate()
    assert is_valid
    assert len([v for v in violations if v.severity.is_error]) == 0
    
    # Test with invalid value
    validator.value = "invalid short"
    is_valid, violations = validator.validate()
    assert not is_valid  # Invalid due to prefix error
    
    error_violations = [v for v in violations if v.severity.is_error]
    warning_violations = [v for v in violations if v.severity.is_warning]
    info_violations = [v for v in violations if v.severity.is_info]
    
    assert len(error_violations) == 1  # prefix_check
    assert len(warning_violations) == 1  # no_spaces  
    assert len(info_violations) == 0  # min_length passes