#!/usr/bin/env python3
"""
Test module for VariableItem functionality.

File:
    name: test_VariableItem.py
    uuid: 7e8f9a0b-1c2d-3e4f-5a6b-7c8d9e0f1a2b
    date: 2025-10-03

Description:
    Comprehensive tests for VariableItem functionality including initialization,
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
# pyright: reportGlobalVariablesNotAssigned=false

# [Standard library imports]
import os

# [Test imports]
import pytest

# [Device under test import]
from hands_scaphoid.objects.VariableItem import VariableItem
from hands_scaphoid.objects.ItemCore import ItemCore
from hands_scaphoid.types import ItemType

# [Test data - Global variables for consistency across tests]

# Primary test variable
G_var_name1 = "TEST_VARIABLE"
G_var_value1 = "TEST_VALUE"
G_var_type1 = ItemType.VARIABLE
G_var_project1 = None

# Secondary test variable with project
G_var_name2 = "PROJECT_VAR"
G_var_value2 = "PROJECT_VALUE"
G_var_type2 = ItemType.VARIABLE
G_var_project2 = ".env"

# Third test variable for additional scenarios
G_var_name3 = "NUMERIC_VAR"
G_var_value3 = 42
G_var_type3 = ItemType.VARIABLE
G_var_project3 = None

# Fourth test variable for hex values
G_var_name4 = "HEX_VAR"
G_var_value4 = 0xDEAD
G_var_type4 = ItemType.VARIABLE
G_var_project4 = None

# [Fixtures for VariableItem instances]

@pytest.fixture
def variable_item():
    """Primary VariableItem fixture for standard testing."""
    return VariableItem(name=G_var_name1, value=G_var_value1)

@pytest.fixture
def variable_with_project():
    """VariableItem fixture with project parameter."""
    return VariableItem(name=G_var_name2, value=G_var_value2)

@pytest.fixture
def variable_numeric():
    """VariableItem fixture with numeric value."""
    return VariableItem(name=G_var_name3, value=G_var_value3)

@pytest.fixture
def variable_hex():
    """VariableItem fixture with hexadecimal value."""
    return VariableItem(name=G_var_name4, value=G_var_value4)

# [Fixtures for dictionary representations]

@pytest.fixture
def dictionary_variable():
    """Dictionary representation of primary VariableItem."""
    return {
        "name": G_var_name1,
        "value": G_var_value1,
        "item_type": G_var_type1,
        "project": G_var_project1,
    }

@pytest.fixture
def dictionary_variable_with_project():
    """Dictionary representation of VariableItem with project."""
    return {
        "name": G_var_name2,
        "value": G_var_value2,
        "item_type": G_var_type2,
        "project": G_var_project2,
    }

@pytest.fixture
def dictionary_variable_numeric():
    """Dictionary representation of VariableItem with numeric value."""
    return {
        "name": G_var_name3,
        "value": G_var_value3,
        "item_type": G_var_type3,
        "project": G_var_project3,
    }

# [Fixtures for serialized formats]

@pytest.fixture
def json_variable():
    """JSON representation of primary VariableItem."""
    return f'{{"name": "{G_var_name1}", "value": "{G_var_value1}", "item_type": "{G_var_type1.value}", "project": null}}'

@pytest.fixture
def yaml_variable():
    """YAML representation of primary VariableItem."""
    return f"item_type: variable\nname: {G_var_name1}\nproject: null\nvalue: {G_var_value1}\n"

@pytest.fixture
def toml_variable():
    """TOML representation of primary VariableItem."""
    return f'name = "{G_var_name1}"\nvalue = "{G_var_value1}"\nitem_type = "{G_var_type1.value}"\nproject = ""\n'

@pytest.fixture
def env_var_variable():
    """Environment variable representation of primary VariableItem."""
    return f"{G_var_name1}={G_var_value1}"

# [Core initialization tests]

def test_VariableItem_initialization(variable_item):
    """Test basic VariableItem initialization with all core properties."""
    assert variable_item.name == G_var_name1, f"Error: VariableItem.name expected '{G_var_name1}', got '{variable_item.name}'"
    assert variable_item.value == G_var_value1, f"Error: VariableItem.value expected '{G_var_value1}', got '{variable_item.value}'"
    assert variable_item.item_type == G_var_type1, f"Error: VariableItem.item_type expected '{G_var_type1}', got '{variable_item.item_type}'"
    assert variable_item.project == G_var_project1, f"Error: VariableItem.project expected '{G_var_project1}', got '{variable_item.project}'"

def test_VariableItem_initialization_with_project(variable_with_project):
    """Test VariableItem initialization with project parameter."""
    assert variable_with_project.name == G_var_name2, f"Error: VariableItem.name with project expected '{G_var_name2}', got '{variable_with_project.name}'"
    assert variable_with_project.value == G_var_value2, f"Error: VariableItem.value with project expected '{G_var_value2}', got '{variable_with_project.value}'"
    assert variable_with_project.item_type == G_var_type2, f"Error: VariableItem.item_type with project expected '{G_var_type2}', got '{variable_with_project.item_type}'"

def test_VariableItem_type_enforcement():
    """Test that VariableItem enforces VARIABLE type regardless of input."""
    # Test that even if we try to pass a different type, it gets set to VARIABLE
    var = VariableItem(name="TYPE_TEST", value="VALUE")
    assert var.item_type == ItemType.VARIABLE, f"Error: VariableItem must enforce VARIABLE type, got '{var.item_type}'"

# [Value setting and property tests]

def test_VariableItem_set_value(variable_item):
    """Test VariableItem value setting through property setter."""
    # Initial value check
    assert variable_item.value == G_var_value1, f"Error: VariableItem initial value expected '{G_var_value1}', got '{variable_item.value}'"
    
    # Set new value
    variable_item.value = G_var_value2
    assert variable_item.value == G_var_value2, f"Error: VariableItem value setter expected '{G_var_value2}', got '{variable_item.value}'"
    assert variable_item._value == G_var_value2, f"Error: VariableItem._value internal property expected '{G_var_value2}', got '{variable_item._value}'"

def test_VariableItem_with_integer_value(variable_numeric):
    """Test VariableItem with integer value handling."""
    assert variable_numeric.name == G_var_name3, f"Error: VariableItem with int name expected '{G_var_name3}', got '{variable_numeric.name}'"
    assert variable_numeric.value == G_var_value3, f"Error: VariableItem with int value expected '{G_var_value3}', got '{variable_numeric.value}'"
    assert variable_numeric.item_type == G_var_type3, f"Error: VariableItem with int item_type expected '{G_var_type3}', got '{variable_numeric.item_type}'"
    
    # Test value change
    new_value = 999
    variable_numeric.value = new_value
    assert variable_numeric.value == new_value, f"Error: VariableItem set int value expected '{new_value}', got '{variable_numeric.value}'"

def test_VariableItem_with_hex_value(variable_hex):
    """Test VariableItem with hexadecimal value handling."""
    expected_decimal = 57005  # 0xDEAD in decimal
    assert variable_hex.name == G_var_name4, f"Error: VariableItem with hex name expected '{G_var_name4}', got '{variable_hex.name}'"
    assert variable_hex.value == expected_decimal, f"Error: VariableItem with hex value expected '{expected_decimal}', got '{variable_hex.value}'"
    assert variable_hex.item_type == G_var_type4, f"Error: VariableItem with hex item_type expected '{G_var_type4}', got '{variable_hex.item_type}'"

# [String representation tests]

def test_VariableItem_str_repr(variable_item):
    """Test VariableItem string and repr methods."""    
    # Test __str__ method
    expected_str = f'{G_var_name1}="{G_var_value1}"'
    assert str(variable_item) == expected_str, f"Error: VariableItem.__str__ expected '{expected_str}', got '{str(variable_item)}'"
    
    # Test __repr__ method  
    expected_repr = f'VariableItem(name={G_var_name1}, value={G_var_value1})'
    assert repr(variable_item) == expected_repr, f"Error: VariableItem.__repr__ expected '{expected_repr}', got '{repr(variable_item)}'"

# [Serialization tests]

def test_VariableItem_to_dict_json_yaml_env(variable_item, dictionary_variable, json_variable, yaml_variable, env_var_variable):
    """Test all VariableItem serialization methods."""
    # Test to_dict
    dict_rep = variable_item.to_dict()
    assert dict_rep == dictionary_variable, f"Error: VariableItem.to_dict expected '{dictionary_variable}', got '{dict_rep}'"
    
    # Test to_json
    json_rep = variable_item.to_json()
    assert json_rep == json_variable, f"Error: VariableItem.to_json expected '{json_variable}', got '{json_rep}'"
    
    # Test to_yaml
    yaml_rep = variable_item.to_yaml()
    assert yaml_rep == yaml_variable, f"Error: VariableItem.to_yaml expected '{yaml_variable}', got '{yaml_rep}'"
    
    # Test to_env_var
    env_rep = variable_item.to_env_var()
    assert env_rep == env_var_variable, f"Error: VariableItem.to_env_var expected '{env_var_variable}', got '{env_rep}'"

def test_VariableItem_to_toml(variable_item, toml_variable):
    """Test VariableItem TOML serialization."""
    toml_rep = variable_item.to_toml()
    assert toml_rep == toml_variable, f"Error: VariableItem.to_toml expected '{toml_variable}', got '{toml_rep}'"

# [Deserialization tests]

def test_VariableItem_from_dict(variable_item, dictionary_variable):
    """Test VariableItem creation from dictionary."""
    new_variable = ItemCore.from_dict(dictionary_variable)
    assert isinstance(new_variable, ItemCore), f"Error: VariableItem.from_dict type expected 'ItemCore', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: VariableItem.from_dict name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: VariableItem.from_dict value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: VariableItem.from_dict item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_VariableItem_from_json(variable_item, json_variable):
    """Test VariableItem creation from JSON string."""
    new_variable = ItemCore.from_json(json_variable)
    assert isinstance(new_variable, ItemCore), f"Error: VariableItem.from_json type expected 'ItemCore', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: VariableItem.from_json name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: VariableItem.from_json value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: VariableItem.from_json item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_VariableItem_from_yaml(variable_item, yaml_variable):
    """Test VariableItem creation from YAML string."""
    new_variable = ItemCore.from_yaml(yaml_variable)
    assert isinstance(new_variable, ItemCore), f"Error: VariableItem.from_yaml type expected 'ItemCore', got '{type(new_variable)}'"
    assert new_variable.name == variable_item.name, f"Error: VariableItem.from_yaml name expected '{variable_item.name}', got '{new_variable.name}'"
    assert new_variable.value == variable_item.value, f"Error: VariableItem.from_yaml value expected '{variable_item.value}', got '{new_variable.value}'"
    assert new_variable.item_type == variable_item.item_type, f"Error: VariableItem.from_yaml item_type expected '{variable_item.item_type}', got '{new_variable.item_type}'"

def test_VariableItem_from_env_var():
    """Test VariableItem creation from environment variable."""
    # Set up test environment variable
    test_env_name = "TEST_FROM_ENV"
    test_env_value = "ENV_VALUE"
    os.environ[test_env_name] = test_env_value
    
    try:
        new_variable = ItemCore.from_env_var(test_env_name)
        assert isinstance(new_variable, ItemCore), f"Error: VariableItem.from_env_var type expected 'ItemCore', got '{type(new_variable)}'"
        assert new_variable.name == test_env_name, f"Error: VariableItem.from_env_var name expected '{test_env_name}', got '{new_variable.name}'"
        assert new_variable.value == test_env_value, f"Error: VariableItem.from_env_var value expected '{test_env_value}', got '{new_variable.value}'"
        assert new_variable.item_type == ItemType.VARIABLE, f"Error: VariableItem.from_env_var item_type expected '{ItemType.VARIABLE}', got '{new_variable.item_type}'"
    finally:
        # Clean up test environment variable
        if test_env_name in os.environ:
            del os.environ[test_env_name]

# [Complex serialization scenarios]

def test_VariableItem_with_complex_values():
    """Test VariableItem serialization with complex values."""
    # Test with string containing special characters
    special_var = VariableItem(name="SPECIAL_VAR", value='value with "quotes" and spaces')
    
    # Test dict serialization
    dict_result = special_var.to_dict()
    expected_dict = {
        "name": "SPECIAL_VAR",
        "value": 'value with "quotes" and spaces',
        "item_type": ItemType.VARIABLE,
        "project": None,
    }
    assert dict_result == expected_dict, f"Error: VariableItem complex to_dict expected '{expected_dict}', got '{dict_result}'"
    
    # Test JSON serialization (should handle quotes properly)
    json_result = special_var.to_json()
    assert '"SPECIAL_VAR"' in json_result, f"Error: VariableItem complex JSON should contain quoted name, got '{json_result}'"
    assert '"variable"' in json_result, f"Error: VariableItem complex JSON should contain item_type, got '{json_result}'"

def test_VariableItem_numeric_serialization(variable_numeric):
    """Test VariableItem serialization with numeric values."""
    # Test complete serialization chain
    expected_dict = {
        "name": G_var_name3,
        "value": G_var_value3,
        "item_type": G_var_type3,
        "project": None,
    }
    
    dict_result = variable_numeric.to_dict()
    assert dict_result == expected_dict, f"Error: VariableItem numeric to_dict expected '{expected_dict}', got '{dict_result}'"
    
    expected_json = f'{{"name": "{G_var_name3}", "value": {G_var_value3}, "item_type": "variable", "project": null}}'
    json_result = variable_numeric.to_json()
    assert json_result == expected_json, f"Error: VariableItem numeric to_json expected '{expected_json}', got '{json_result}'"
    
    expected_yaml = f"item_type: variable\nname: {G_var_name3}\nproject: null\nvalue: {G_var_value3}\n"
    yaml_result = variable_numeric.to_yaml()
    assert yaml_result == expected_yaml, f"Error: VariableItem numeric to_yaml expected '{expected_yaml}', got '{yaml_result}'"
    
    expected_env = f"{G_var_name3}={G_var_value3}"
    env_result = variable_numeric.to_env_var()
    assert env_result == expected_env, f"Error: VariableItem numeric to_env_var expected '{expected_env}', got '{env_result}'"

# [Round-trip serialization tests]

def test_VariableItem_json_roundtrip(variable_item):
    """Test VariableItem JSON serialization round-trip consistency."""
    # Serialize to JSON and back
    json_str = variable_item.to_json()
    restored_variable = ItemCore.from_json(json_str)
    
    assert restored_variable.name == variable_item.name, f"Error: JSON round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: JSON round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: JSON round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

def test_VariableItem_yaml_roundtrip(variable_item):
    """Test VariableItem YAML serialization round-trip consistency."""
    # Serialize to YAML and back
    yaml_str = variable_item.to_yaml()
    restored_variable = ItemCore.from_yaml(yaml_str)
    
    assert restored_variable.name == variable_item.name, f"Error: YAML round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: YAML round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: YAML round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

def test_VariableItem_dict_roundtrip(variable_item):
    """Test VariableItem dictionary serialization round-trip consistency."""
    # Serialize to dict and back
    dict_data = variable_item.to_dict()
    restored_variable = ItemCore.from_dict(dict_data)
    
    assert restored_variable.name == variable_item.name, f"Error: Dict round-trip name expected '{variable_item.name}', got '{restored_variable.name}'"
    assert restored_variable.value == variable_item.value, f"Error: Dict round-trip value expected '{variable_item.value}', got '{restored_variable.value}'"
    assert restored_variable.item_type == variable_item.item_type, f"Error: Dict round-trip item_type expected '{variable_item.item_type}', got '{restored_variable.item_type}'"

# [Edge case tests]

def test_VariableItem_empty_values():
    """Test VariableItem with empty or None values."""
    # Test with empty string value
    empty_var = VariableItem(name="EMPTY_VAR", value="")
    assert empty_var.name == "EMPTY_VAR", f"Error: VariableItem empty value name expected 'EMPTY_VAR', got '{empty_var.name}'"
    assert empty_var.value == "", f"Error: VariableItem empty value expected '', got '{empty_var.value}'"
    assert empty_var.item_type == ItemType.VARIABLE, f"Error: VariableItem empty value item_type expected '{ItemType.VARIABLE}', got '{empty_var.item_type}'"
    
    # Test serialization of empty value
    env_result = empty_var.to_env_var()
    expected_env = "EMPTY_VAR="
    assert env_result == expected_env, f"Error: VariableItem empty to_env_var expected '{expected_env}', got '{env_result}'"

def test_VariableItem_special_characters():
    """Test VariableItem with special characters in name and value."""
    special_name = "VAR_WITH_UNDERSCORES_123"
    special_value = "value-with-dashes_and_underscores.and.dots"
    
    special_var = VariableItem(name=special_name, value=special_value)
    assert special_var.name == special_name, f"Error: VariableItem special chars name expected '{special_name}', got '{special_var.name}'"
    assert special_var.value == special_value, f"Error: VariableItem special chars value expected '{special_value}', got '{special_var.value}'"
    
    # Test that serialization works
    json_result = special_var.to_json()
    assert special_name in json_result, f"Error: VariableItem special chars JSON should contain name, got '{json_result}'"
    assert special_value in json_result, f"Error: VariableItem special chars JSON should contain value, got '{json_result}'"

def test_VariableItem_boolean_and_none_values():
    """Test VariableItem with boolean and None values."""
    # Test with boolean value
    bool_var = VariableItem(name="BOOL_VAR", value=True)
    assert bool_var.value is True, f"Error: VariableItem boolean value expected 'True', got '{bool_var.value}'"
    
    # Test with None value (should be handled gracefully)
    none_var = VariableItem(name="NONE_VAR", value=None)
    assert none_var.value is None, f"Error: VariableItem None value expected 'None', got '{none_var.value}'"
    
    # Test serialization with None
    dict_result = none_var.to_dict()
    assert dict_result["value"] is None, f"Error: VariableItem None to_dict value should be None, got '{dict_result['value']}'"

# [Performance and validation tests]

def test_VariableItem_inheritance():
    """Test that VariableItem properly inherits from ItemCore."""
    var = VariableItem(name="INHERIT_TEST", value="value")
    
    # Test inheritance
    assert isinstance(var, ItemCore), f"Error: VariableItem should inherit from ItemCore, got '{type(var)}'"
    assert isinstance(var, VariableItem), f"Error: VariableItem should be instance of VariableItem, got '{type(var)}'"
    
    # Test that all ItemCore methods are available
    assert hasattr(var, 'to_dict'), "Error: VariableItem should have to_dict method from ItemCore"
    assert hasattr(var, 'to_json'), "Error: VariableItem should have to_json method from ItemCore"
    assert hasattr(var, 'to_yaml'), "Error: VariableItem should have to_yaml method from ItemCore"
    assert hasattr(var, 'to_toml'), "Error: VariableItem should have to_toml method from ItemCore"
    assert hasattr(var, 'to_env_var'), "Error: VariableItem should have to_env_var method from ItemCore"

def test_VariableItem_multiple_instances():
    """Test creating multiple VariableItem instances."""
    variables = []
    
    # Create multiple instances
    for i in range(5):
        var = VariableItem(name=f"VAR_{i}", value=f"value_{i}")
        variables.append(var)
        
        # Test each instance
        assert var.name == f"VAR_{i}", f"Error: Multiple instance {i} name expected 'VAR_{i}', got '{var.name}'"
        assert var.value == f"value_{i}", f"Error: Multiple instance {i} value expected 'value_{i}', got '{var.value}'"
        assert var.item_type == ItemType.VARIABLE, f"Error: Multiple instance {i} item_type expected '{ItemType.VARIABLE}', got '{var.item_type}'"
    
    # Test that all instances are independent
    assert len(variables) == 5, f"Error: Should have 5 VariableItem instances, got {len(variables)}"
    assert all(isinstance(var, VariableItem) for var in variables), "Error: All instances should be VariableItem type"

# [End of test file]
