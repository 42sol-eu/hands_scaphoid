#!/usr/bin/env python3
"""
Test module for PathVariable functionality.

File:
    name: test_PathVariable.py
    uuid: c7ea69be-ea5c-4368-ae2f-30e7acb858fd
    date: 2025-10-03

Description:
    Comprehensive tests for PathVariable functionality including initialization,
    serialization, deserialization, and all instance methods

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- DUT[testing]: Device Under Test (the class being tested)
- 42sol[company]: 42 solutions (www.42sol.eu)
"""

# [Linter config]
# pyright: reportRedeclaration=false
# pyright: reportUndefinedVariable=false
# pyright: reportDefinedOuterName=false

# [Standard library imports]
import os

# [Device under test import]
from hands_scaphoid.objects.PathVariable import PathVariable
from hands_scaphoid.objects.ItemCore import ItemCore
from hands_scaphoid.types import ItemType
from hands_scaphoid.types.SeverityType import SeverityType

# [Test imports]
import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch

# [Test data - Global variables for consistency across tests]

# Primary test path
G_var_name1 = "TEST_PATH_FILE"
G_var_value1 = "/etc/hosts"
G_var_type1 = ItemType.PATH
G_var_project1 = None

# Secondary test variable with project
G_var_name2 = "PROJECT_VAR"
G_var_value2 = "PROJECT_VALUE"
G_var_type2 = ItemType.PROJECT
G_var_project2 = ".env"

# Third test variable for additional scenarios
G_var_name3 = "TEST_PATH_DIRECTORY"
G_var_value3 = "/etc/ssh/"
G_var_type3 = ItemType.PATH
G_var_project3 = "/etc"

# Fourth test variable for invalid values
G_var_name4 = "TEST_PATH_INVALID"
G_var_value4 = " / invalid"
G_var_type4 = ItemType.PATH
G_var_project4 = None

# [Fixtures for PathVariable instances]

@pytest.fixture
def variable_item():
    """Primary PathVariable fixture for standard testing."""
    
    return PathVariable(name=G_var_name1, value=G_var_value1)

@pytest.fixture
def path_item():
    """Primary PathVariable fixture for standard testing."""
    
    return PathVariable(name=G_var_name1, value=G_var_value1)

@pytest.fixture
def variable_with_project():
    """PathVariable fixture with project parameter."""
    
    return PathVariable(name=G_var_name2, value=G_var_value2)

@pytest.fixture
def variable_numeric():
    """PathVariable fixture with numeric value."""
    
    return PathVariable(name=G_var_name3, value=G_var_value3)

@pytest.fixture
def variable_hex():
    """PathVariable fixture with hexadecimal value."""
    
    return PathVariable(name=G_var_name4, value=G_var_value4)

# [Fixtures for dictionary representations]

@pytest.fixture
def dictionary_variable():
    """Dictionary representation of primary PathVariable."""
    
    return {
        "name": G_var_name1,
        "value": G_var_value1,
        "item_type": G_var_type1,
        "project": G_var_project1,
    }

@pytest.fixture
def dictionary_variable_with_project():
    """Dictionary representation of PathVariable with project."""
    
    return {
        "name": G_var_name2,
        "value": G_var_value2,
        "item_type": G_var_type2,
        "project": G_var_project2,
    }

@pytest.fixture
def dictionary_variable_numeric():
    """Dictionary representation of PathVariable with numeric value."""
    
    return {
        "name": G_var_name3,
        "value": G_var_value3,
        "item_type": G_var_type3,
        "project": G_var_project3,
    }

# [Fixtures for serialized formats]

@pytest.fixture
def json_variable():
    """JSON representation of primary PathVariable."""
    
    return f'{{"name": "{G_var_name1}", "value": "{G_var_value1}", "item_type": "{G_var_type1.value}", "project": null}}'

@pytest.fixture
def yaml_variable():
    """YAML representation of primary PathVariable."""
    
    return f"item_type: variable\nname: {G_var_name1}\nproject: null\nvalue: {G_var_value1}\n"

@pytest.fixture
def toml_variable():
    """TOML representation of primary PathVariable."""
    
    return f'name = "{G_var_name1}"\nvalue = "{G_var_value1}"\nitem_type = "{G_var_type1.value}"\nproject = ""\n'

@pytest.fixture
def env_G_var_variable():
    """Environment variable representation of primary PathVariable."""
    
    return f"{G_var_name1}={G_var_value1}"

# [Core initialization tests]

def test_PathVariable_initialization(path_item):
    """Test basic PathVariable initialization with all core properties."""
    
    assert path_item.name == G_var_name1, f"Error: PathVariable.name expected '{G_var_name1}', got '{path_item.name}'"
    assert path_item.value == G_var_value1, f"Error: PathVariable.value expected '{G_var_value1}', got '{path_item.value}'"
    assert path_item.item_type == G_var_type1, f"Error: PathVariable.item_type expected '{G_var_type1}', got '{path_item.item_type}'"
    assert path_item.project == G_var_project1, f"Error: PathVariable.project expected '{G_var_project1}', got '{path_item.project}'"

def test_PathVariable_initialization_with_project(variable_with_project):
    """Test PathVariable initialization with project parameter."""
    
    assert variable_with_project.name == G_var_name2, f"Error: PathVariable.name with project expected '{G_var_name2}', got '{variable_with_project.name}'"
    assert variable_with_project.value == G_var_value2, f"Error: PathVariable.value with project expected '{G_var_value2}', got '{variable_with_project.value}'"
    assert variable_with_project.item_type == G_var_type2, f"Error: PathVariable.item_type with project expected '{G_var_type2}', got '{variable_with_project.item_type}'"

def test_PathVariable_type_enforcement():
    """Test that PathVariable enforces VARIABLE type regardless of input."""
    # Test that even if we try to pass a different type, it gets set to VARIABLE
    var = PathVariable(name="TYPE_TEST", value="VALUE")
    assert var.item_type == ItemType.VARIABLE, f"Error: PathVariable must enforce VARIABLE type, got '{var.item_type}'"

# [Value setting and property tests]

def test_PathVariable_set_value(variable_item):
    """Test PathVariable value setting through property setter."""
    
    # Initial value check
    assert variable_item.value == G_var_value1, f"Error: PathVariable initial value expected '{G_var_value1}', got '{variable_item.value}'"
    
    # Set new value
    variable_item.value = G_var_value2
    assert variable_item.value == G_var_value2, f"Error: PathVariable value setter expected '{G_var_value2}', got '{variable_item.value}'"
    assert variable_item._value == G_var_value2, f"Error: PathVariable._value internal property expected '{G_var_value2}', got '{variable_item._value}'"

def test_PathVariable_with_integer_value(variable_numeric):
    """Test PathVariable with integer value handling."""
    
    assert variable_numeric.name == G_var_name3, f"Error: PathVariable with int name expected '{G_var_name3}', got '{variable_numeric.name}'"
    assert variable_numeric.value == G_var_value3, f"Error: PathVariable with int value expected '{G_var_value3}', got '{variable_numeric.value}'"
    assert variable_numeric.item_type == G_var_type3, f"Error: PathVariable with int item_type expected '{G_var_type3}', got '{variable_numeric.item_type}'"
    
    # Test value change
    new_value = 999
    variable_numeric.value = new_value
    assert variable_numeric.value == new_value, f"Error: PathVariable set int value expected '{new_value}', got '{variable_numeric.value}'"

def test_PathVariable_with_hex_value(variable_hex):
    """Test PathVariable with hexadecimal value handling."""
    
    expected_decimal = 57005  # 0xDEAD in decimal
    assert variable_hex.name == G_var_name4, f"Error: PathVariable with hex name expected '{G_var_name4}', got '{variable_hex.name}'"
    assert variable_hex.value == expected_decimal, f"Error: PathVariable with hex value expected '{expected_decimal}', got '{variable_hex.value}'"
    assert variable_hex.item_type == G_var_type4, f"Error: PathVariable with hex item_type expected '{G_var_type4}', got '{variable_hex.item_type}'"

# [String representation tests]

def test_PathVariable_str_repr(variable_item):
    """Test PathVariable string and repr methods."""
    
    
    # Test __str__ method
    expected_str = f'{G_var_name1}="{G_var_value1}"'
    assert str(variable_item) == expected_str, f"Error: PathVariable.__str__ expected '{expected_str}', got '{str(variable_item)}'"
    
    # Test __repr__ method (now includes validation status)
    repr_str = repr(variable_item)
    assert 'PathVariable' in repr_str, f"Error: PathVariable.__repr__ should contain 'PathVariable', got '{repr_str}'"
    assert G_var_name1 in repr_str, f"Error: PathVariable.__repr__ should contain name '{G_var_name1}', got '{repr_str}'"
    assert G_var_value1 in repr_str, f"Error: PathVariable.__repr__ should contain value '{G_var_value1}', got '{repr_str}'"

# [Serialization tests]

def test_PathVariable_to_dict_json_yaml_env(variable_item, dictionary_variable, json_variable, yaml_variable, env_var_variable):
    """Test all PathVariable serialization methods."""
    
    # Test to_dict
    dict_rep = variable_item.to_dict()
    assert dict_rep == dictionary_variable, f"Error: PathVariable.to_dict expected '{dictionary_variable}', got '{dict_rep}'"
    
    # Test to_json
    json_rep = variable_item.to_json()
    assert json_rep == json_variable, f"Error: PathVariable.to_json expected '{json_variable}', got '{json_rep}'"
    
    # Test to_yaml
    yaml_rep = variable_item.to_yaml()
    assert yaml_rep == yaml_variable, f"Error: PathVariable.to_yaml expected '{yaml_variable}', got '{yaml_rep}'"
    
    # Test to_env_var
    env_rep = variable_item.to_env_var()
    assert env_rep == env_var_variable, f"Error: PathVariable.to_env_var expected '{env_var_variable}', got '{env_rep}'"

def test_PathVariable_to_toml(variable_item, toml_variable):
    """Test PathVariable TOML serialization."""
    toml_rep = variable_item.to_toml()
    assert toml_rep == toml_variable, f"Error: PathVariable.to_toml expected '{toml_variable}', got '{toml_rep}'"

# [Deserialization tests]

def test_PathVariable_from_dict(variable_item, dictionary_variable):
    """Test PathVariable creation from dictionary."""
    new_variable = PathVariable.from_dict(dictionary_variable)
    assert isinstance(new_variable, PathVariable), f"Error: PathVariable.from_dict type expected 'PathVariable', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: PathVariable.from_dict name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: PathVariable.from_dict value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: PathVariable.from_dict item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_PathVariable_from_json(variable_item, json_variable):
    """Test PathVariable creation from JSON string."""
    new_variable = ItemCore.from_json(json_variable)
    assert isinstance(new_variable, ItemCore), f"Error: PathVariable.from_json type expected 'ItemCore', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: PathVariable.from_json name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: PathVariable.from_json value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: PathVariable.from_json item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_PathVariable_from_yaml(variable_item, yaml_variable):
    """Test PathVariable creation from YAML string."""
    new_variable = ItemCore.from_yaml(yaml_variable)
    assert isinstance(new_variable, ItemCore), f"Error: PathVariable.from_yaml type expected 'ItemCore', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: PathVariable.from_yaml name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: PathVariable.from_yaml value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: PathVariable.from_yaml item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_PathVariable_from_env_var():
    """Test PathVariable creation from environment variable."""
    # Set up test environment variable
    test_env_name = "TEST_FROM_ENV"
    test_env_value = "ENV_VALUE"
    os.environ[test_env_name] = test_env_value
    
    try:
        new_variable = ItemCore.from_env_var(test_env_name)
        assert isinstance(new_variable, ItemCore), f"Error: PathVariable.from_env_var type expected 'ItemCore', got '{type(new_variable)}'"
        assert new_variable.name == test_env_name, f"Error: PathVariable.from_env_var name expected '{test_env_name}', got '{new_variable.name}'"
        assert new_variable.value == test_env_value, f"Error: PathVariable.from_env_var value expected '{test_env_value}', got '{new_variable.value}'"
        assert new_variable.item_type == ItemType.VARIABLE, f"Error: PathVariable.from_env_var item_type expected '{ItemType.VARIABLE}', got '{new_variable.item_type}'"
    finally:
        # Clean up test environment variable
        if test_env_name in os.environ:
            del os.environ[test_env_name]

# [Complex serialization scenarios]

def test_PathVariable_with_complex_values():
    """Test PathVariable serialization with complex values."""
    # Test with string containing special characters
    special_var = PathVariable(name="SPECIAL_VAR", value='value with "quotes" and spaces')
    
    # Test dict serialization
    dict_result = special_var.to_dict()
    expected_dict = {
        "name": "SPECIAL_VAR",
        "value": 'value with "quotes" and spaces',
        "item_type": ItemType.VARIABLE,
        "project": None,
    }
    assert dict_result == expected_dict, f"Error: PathVariable complex to_dict expected '{expected_dict}', got '{dict_result}'"
    
    # Test JSON serialization (should handle quotes properly)
    json_result = special_var.to_json()
    assert '"SPECIAL_VAR"' in json_result, f"Error: PathVariable complex JSON should contain quoted name, got '{json_result}'"
    assert '"variable"' in json_result, f"Error: PathVariable complex JSON should contain item_type, got '{json_result}'"


# [Round-trip serialization tests]

def test_PathVariable_json_roundtrip(variable_item):
    """Test PathVariable JSON serialization round-trip consistency."""
    # Serialize to JSON and back
    json_str = variable_item.to_json()
    restored_variable = ItemCore.from_json(json_str)
    
    assert restored_variable.name == variable_item.name, f"Error: JSON round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: JSON round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: JSON round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

def test_PathVariable_yaml_roundtrip(variable_item):
    """Test PathVariable YAML serialization round-trip consistency."""
    # Serialize to YAML and back
    yaml_str = variable_item.to_yaml()
    restored_variable = ItemCore.from_yaml(yaml_str)
    
    assert restored_variable.name == variable_item.name, f"Error: YAML round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: YAML round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: YAML round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

def test_PathVariable_dict_roundtrip(variable_item):
    """Test PathVariable dictionary serialization round-trip consistency."""
    # Serialize to dict and back
    dict_data = variable_item.to_dict()
    restored_variable = ItemCore.from_dict(dict_data)
    
    assert restored_variable.name == variable_item.name, f"Error: Dict round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: Dict round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: Dict round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

# [Edge case tests]

def test_PathVariable_empty_values():
    """Test PathVariable with empty or None values."""
    # Test with empty string value
    empty_var = PathVariable(name="EMPTY_VAR", value="")
    assert empty_var.name == "EMPTY_VAR", f"Error: PathVariable empty value name expected 'EMPTY_VAR', got '{empty_var.name}'"
    assert empty_var.value == "", f"Error: PathVariable empty value expected '', got '{empty_var.value}'"
    assert empty_var.item_type == ItemType.VARIABLE, f"Error: PathVariable empty value item_type expected '{ItemType.VARIABLE}', got '{empty_var.item_type}'"
    
    # Test serialization of empty value
    env_result = empty_var.to_env_var()
    expected_env = "EMPTY_VAR="
    assert env_result == expected_env, f"Error: PathVariable empty to_env_var expected '{expected_env}', got '{env_result}'"

def test_PathVariable_special_characters():
    """Test PathVariable with special characters in name and value."""
    special_name = "VAR_WITH_UNDERSCORES_123"
    special_value = "value-with-dashes_and_underscores.and.dots"
    
    special_var = PathVariable(name=special_name, value=special_value)
    assert special_var.name == special_name, f"Error: PathVariable special chars name expected '{special_name}', got '{special_var.name}'"
    assert special_var.value == special_value, f"Error: PathVariable special chars value expected '{special_value}', got '{special_var.value}'"
    
    # Test that serialization works
    json_result = special_var.to_json()
    assert special_name in json_result, f"Error: PathVariable special chars JSON should contain name, got '{json_result}'"
    assert special_value in json_result, f"Error: PathVariable special chars JSON should contain value, got '{json_result}'"

def test_PathVariable_boolean_and_none_values():
    """Test PathVariable with boolean and None values."""
    # Test with boolean value
    bool_var = PathVariable(name="BOOL_VAR", value=True)
    assert bool_var.value is True, f"Error: PathVariable boolean value expected 'True', got '{bool_var.value}'"
    
    # Test with None value (should be handled gracefully)
    none_var = PathVariable(name="NONE_VAR", value=None)
    assert none_var.value is None, f"Error: PathVariable None value expected 'None', got '{none_var.value}'"
    
    # Test serialization with None
    dict_result = none_var.to_dict()
    assert dict_result["value"] is None, f"Error: PathVariable None to_dict value should be None, got '{dict_result['value']}'"

# [Performance and validation tests]

def test_PathVariable_inheritance():
    """Test that PathVariable properly inherits from ItemCore."""
    var = PathVariable(name="INHERIT_TEST", value="value")
    
    # Test inheritance
    assert isinstance(var, ItemCore), f"Error: PathVariable should inherit from ItemCore, got '{type(var)}'"
    assert isinstance(var, PathVariable), f"Error: PathVariable should be instance of PathVariable, got '{type(var)}'"
    
    # Test that all ItemCore methods are available
    assert hasattr(var, 'to_dict'), "Error: PathVariable should have to_dict method from ItemCore"
    assert hasattr(var, 'to_json'), "Error: PathVariable should have to_json method from ItemCore"
    assert hasattr(var, 'to_yaml'), "Error: PathVariable should have to_yaml method from ItemCore"
    assert hasattr(var, 'to_toml'), "Error: PathVariable should have to_toml method from ItemCore"
    assert hasattr(var, 'to_env_var'), "Error: PathVariable should have to_env_var method from ItemCore"

def test_PathVariable_multiple_instances():
    """Test creating multiple PathVariable instances."""
    variables = []
    
    # Create multiple instances
    for i in range(5):
        var = PathVariable(name=f"VAR_{i}", value=f"value_{i}")
        variables.append(var)
        
        # Test each instance
        assert var.name == f"VAR_{i}", f"Error: Multiple instance {i} name expected 'VAR_{i}', got '{var.name}'"
        assert var.value == f"value_{i}", f"Error: Multiple instance {i} value expected 'value_{i}', got '{var.value}'"
        assert var.item_type == ItemType.VARIABLE, f"Error: Multiple instance {i} item_type expected '{ItemType.VARIABLE}', got '{var.item_type}'"
    
    # Test that all instances are independent
    assert len(variables) == 5, f"Error: Should have 5 PathVariable instances, got {len(variables)}"
    assert all(isinstance(var, PathVariable) for var in variables), "Error: All instances should be PathVariable type"

# [Validation Tests - New functionality]

def test_PathVariable_validation_initialization():
    """Test PathVariable initialization with validation parameters."""
    # Test basic initialization
    var1 = PathVariable("TEST_VAR", "/test/path")
    assert not var1.strict_mode
    assert not var1.cross_platform
    assert var1.validation_enabled
    
    # Test with strict mode
    var2 = PathVariable("STRICT_VAR", "/test/path", strict_mode=True)
    assert var2.strict_mode
    
    # Test with cross-platform mode
    var3 = PathVariable("CROSS_VAR", "/test/path", cross_platform=True)
    assert var3.cross_platform

def test_PathVariable_validation_basic():
    """Test basic validation functionality."""
    # Valid path
    var = PathVariable("VALID_PATH", "/etc/hosts")
    assert var.valid
    
    # Invalid path with bad characters
    var_invalid = PathVariable("INVALID_PATH", "path<with>bad:chars")
    assert not var_invalid.valid

def test_PathVariable_validation_summary():
    """Test validation summary functionality."""
    var = PathVariable("TEST_PATH", "/valid/path")
    summary = var.get_validation_summary()
    
    assert "is_valid" in summary
    assert "exists" in summary
    assert "validation_enabled" in summary
    assert "violations" in summary
    assert "error_count" in summary
    assert "warning_count" in summary
    assert "info_count" in summary
    
    assert isinstance(summary["violations"], list)
    assert isinstance(summary["error_count"], int)
    assert isinstance(summary["warning_count"], int)
    assert isinstance(summary["info_count"], int)

def test_PathVariable_validation_with_warnings():
    """Test validation with warning-level violations."""
    # Path with uncommon characters should generate warnings
    var = PathVariable("WARNING_PATH", "/path#with$special%chars")
    
    assert var.valid  # Should be valid (warnings don't invalidate)
    
    summary = var.get_validation_summary()
    assert summary["warning_count"] > 0
    assert summary["error_count"] == 0

def test_PathVariable_strict_mode_validation():
    """Test validation in strict mode."""
    # Path that would be warning in normal mode, error in strict mode
    var = PathVariable("STRICT_PATH", "/path#with$special%chars", strict_mode=True)
    
    assert not var.valid  # Should be invalid in strict mode
    
    summary = var.get_validation_summary()
    assert summary["error_count"] > 0

@patch('platform.system')
def test_PathVariable_cross_platform_validation(mock_system):
    """Test cross-platform validation."""
    mock_system.return_value = "Windows"
    
    # Unix-style path on Windows should generate warnings
    var = PathVariable("CROSS_PATH", "/unix/style/path", cross_platform=True)
    
    assert var.valid  # Should be valid but have warnings
    
    summary = var.get_validation_summary()
    assert summary["warning_count"] > 0

def test_PathVariable_custom_validation_rules():
    """Test adding custom validation rules."""
    var = PathVariable("CUSTOM_PATH", "/test/path")
    
    # Add custom rule
    var.add_rule(
        name="must_start_with_test",
        pattern=r"^/test",
        severity=SeverityType.ERROR,
        description="Path must start with /test"
    )
    
    # Should pass validation
    assert var.valid
    
    # Change to invalid path
    var.value = "/invalid/path"
    assert not var.valid

def test_PathVariable_validation_disable():
    """Test disabling validation."""
    var = PathVariable("DISABLED_PATH", "definitely<invalid>path")
    
    # Should be invalid initially
    assert not var.valid
    
    # Disable validation
    var.validation_enabled = False
    
    # Should now be valid (validation disabled)
    assert var.valid

def test_PathVariable_class_methods_validation():
    """Test class methods for validation."""
    # Test is_valid_path method
    assert PathVariable.is_valid_path("/valid/path")
    assert not PathVariable.is_valid_path("invalid<path>")
    
    # Test with strict mode
    assert not PathVariable.is_valid_path("/path#with$special", strict_mode=True)
    
    # Test get_path_violations method
    violations = PathVariable.get_path_violations("invalid<path>")
    assert len(violations) > 0
    assert any(v.severity.is_error for v in violations)

def test_PathVariable_last_violations_property():
    """Test last_violations property."""
    var = PathVariable("VIOLATION_PATH", "invalid<path>")
    
    # Should have violations
    violations = var.last_violations
    assert len(violations) > 0
    assert isinstance(violations[0].rule_name, str)
    assert isinstance(violations[0].severity, SeverityType)
    assert isinstance(violations[0].message, str)

def test_PathVariable_repr_with_validation():
    """Test __repr__ includes validation status."""
    var = PathVariable("REPR_PATH", "/valid/path")
    repr_str = repr(var)
    
    assert "PathVariable" in repr_str
    assert "valid" in repr_str
    assert "not exists" in repr_str or "exists" in repr_str

def test_PathVariable_to_dict_with_validation():
    """Test to_dict includes validation information."""
    var = PathVariable("DICT_PATH", "/test/path")
    data = var.to_dict()
    
    assert "exists" in data
    assert "validation_summary" in data
    assert "strict_mode" in data  
    assert "cross_platform" in data
    
    validation_summary = data["validation_summary"]
    assert "is_valid" in validation_summary
    assert "violations" in validation_summary

def test_PathVariable_from_dict_with_validation():
    """Test from_dict preserves validation configuration."""
    original_data = {
        "name": "FROM_DICT_PATH",
        "value": "/test/path",
        "strict_mode": True,
        "cross_platform": True,
        "validation_enabled": True,
        "validation_rules": {
            "custom_rule": {
                "pattern": r"^/test",
                "severity": "error",
                "description": "Must start with /test",
                "inverse": False,
                "enabled": True
            }
        }
    }
    
    var = PathVariable.from_dict(original_data)
    
    assert var.name == "FROM_DICT_PATH"
    assert var.value == "/test/path"
    assert var.strict_mode
    assert var.cross_platform
    assert var.validation_enabled
    
    # Check custom rule was loaded
    rules = var.get_rules()
    assert "custom_rule" in rules

def test_PathVariable_validation_with_existing_path():
    """Test validation with paths that actually exist."""
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a test file
        test_file = Path(tmpdir) / "test.txt"
        test_file.write_text("test content")
        
        var = PathVariable("EXISTING_PATH", str(test_file))
        
        assert var.exists
        assert var.valid
        
        summary = var.get_validation_summary()
        assert summary["exists"]

def test_PathVariable_path_specific_rules():
    """Test path-specific validation rules."""
    var = PathVariable("PATH_RULES", "/test/path")
    
    # Should have path-specific rules loaded
    rules = var.get_rules()
    rule_names = set(rules.keys())
    
    # Check for some expected path-specific rules
    expected_rules = {
        "invalid_chars", 
        "uncommon_chars", 
        "whitespace_trim",
        "multiple_separators",
        "relative_path_components",
        "absolute_path_format"
    }
    
    # At least some of these should be present
    assert len(expected_rules.intersection(rule_names)) > 0

def test_PathVariable_windows_reserved_names():
    """Test validation of Windows reserved names."""
    reserved_names = ["CON", "PRN", "AUX", "NUL", "COM1", "LPT1"]
    
    for name in reserved_names:
        var = PathVariable("RESERVED_TEST", name)
        # Should generate at least a warning
        summary = var.get_validation_summary()
        assert summary["warning_count"] > 0 or summary["error_count"] > 0

def test_PathVariable_relative_path_validation():
    """Test validation of relative path components."""
    test_paths = [
        "./relative/path",
        "../parent/path", 
        "/absolute/./current",
        "/absolute/../parent"
    ]
    
    for path in test_paths:
        var = PathVariable("RELATIVE_TEST", path)
        # These should be valid but might have info messages
        assert var.valid
        
        summary = var.get_validation_summary()
        # Should not have errors
        assert summary["error_count"] == 0

def test_PathVariable_validation_rule_management():
    """Test managing validation rules on PathVariable instances."""
    var = PathVariable("RULE_MGMT", "/test/path")
    
    initial_rule_count = len(var.get_rules())
    
    # Add a custom rule
    var.add_rule("custom_test", r"^/test", SeverityType.INFO, "Custom test rule")
    assert len(var.get_rules()) == initial_rule_count + 1
    
    # Disable a rule
    var.disable_rule("custom_test")
    rule = var.get_rules()["custom_test"]
    assert not rule.enabled
    
    # Enable the rule
    var.enable_rule("custom_test")
    rule = var.get_rules()["custom_test"]
    assert rule.enabled
    
    # Remove the rule
    var.remove_rule("custom_test")
    assert "custom_test" not in var.get_rules()

# [End of test file]
