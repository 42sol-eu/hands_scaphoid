#!/usr/bin/env python3
"""
Test module for VariableItem functionality.
---yaml
File:
    name: test_ItemCore.py
    uuid: da1c3297-f9b3-4be2-b3a1-b892c8f05916
    date: 2025-10-03

Description:
    Comprehensive tests for ItemCore functionality including initialization,
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
from hands_scaphoid.objects import ItemCore
from hands_scaphoid.types.ItemType import ItemType
from hands_scaphoid.__base__ import is_instance

# [Test imports]
import pytest 

# [Test data]
G_item_name1 = "TEST NAME"
G_item_value1 = "TEST VALUE"
G_item_type1 = ItemType.ITEM
G_item_project1 = None 

G_item_name2 = "TEST VARIABLE"
G_item_value2 = "TEST VALUE"
G_item_type2 = ItemType.VARIABLE
G_item_project2 = ".env"
    
@pytest.fixture
def item():
    """ïtem 1 fixture == item"""
    return ItemCore(name=G_item_name1, value=G_item_value1)

@pytest.fixture
def variable():
    """ïtem 2 fixture == variable"""
    return ItemCore(name=G_item_name2, value=G_item_value2,
                    type=G_item_type2, project=G_item_project2)

@pytest.fixture
def dictionary_item():
    """ïtem 1 fixture == item as dictionary"""
    return {
        "name": G_item_name1,
        "value": G_item_value1,
        "item_type": G_item_type1,
        "project": G_item_project1,
    }

@pytest.fixture
def dictionary_variable():
    """ïtem 2 fixture == item as dictionary"""
    return {
        "name": G_item_name2,
        "value": G_item_value2,
        "item_type": G_item_type2,
        "project": G_item_project2,
    }
    
@pytest.fixture
def json_item():
    """ïtem 1 fixture == item as json """
    return f'{{"name": "{G_item_name1}", "value": "{G_item_value1}", "item_type": "{G_item_type1}", "project": null}}'


@pytest.fixture
def yaml_item():
    """ïtem 1 fixture == item as dictionary"""
    return f"item_type: item\nname: {G_item_name1}\nproject: null\nvalue: {G_item_value1}\n"

@pytest.fixture
def toml_item():
    """ïtem 1 fixture == item as dictionary"""
    return f'name = "{G_item_name1}"\nvalue = "{G_item_value1}"\nitem_type = "{G_item_type1}"\nproject = ""\n'

@pytest.fixture
def env_var_item():
    """ïtem 1 fixture == item as dictionary"""
    return f"{G_item_name1}={G_item_value1}"

# [Test cases]
def test_ItemCore_initialization(item):
    """Core elements of ItemCore"""
    assert item.name == G_item_name1, "Error: ItemCore_item_name"
    assert item.value == G_item_value1, "Error: ItemCore_item_value"
    assert item.item_type == G_item_type1, "Error: ItemCore.item_type"
    assert item.project == G_item_project1, "Error: ItemCore_item_project != None"


def test_ItemCore_set_item_value(item):
    """Test setting G_item_value"""
    assert item.value == G_item_value1, "Error: ItemCore_item_value setter"
    item.value = G_item_value2
    assert item.value == G_item_value2, "Error: ItemCore_item_value setter"
    assert item._value == G_item_value2, "Error: ItemCore._value "


def test_ItemCore_str_repr(item):
    """Test string and repr methods"""
    assert str(item) == f'{G_item_name1}="{G_item_value1}"', "Error: ItemCore.__str__"
    assert repr(item) == f'ItemCore(name={G_item_name1}, value={G_item_value1}, item_type={G_item_type1.upper()})', "Error: ItemCore.__repr__"

def test_ItemCore_to_dict_json_yaml_env(item, 
                                        dictionary_item, 
                                        json_item, 
                                        yaml_item, 
                                        env_var_item):
    """Test conversion methods"""
    dict_rep = item.to_dict()
    assert dict_rep == dictionary_item, "Error: ItemCore.to_dict"
    
    json_rep = item.to_json()
    assert json_rep == json_item, "Error: ItemCore.to_json"
    
    yaml_rep = item.to_yaml()
    assert yaml_rep == yaml_item, "Error: ItemCore.to_yaml"
    
    env_rep = item.to_env_var()
    assert env_rep == env_var_item, "Error: ItemCore.to_env_var"
    
#TODO: to_toml()


def test_ItemCore_from_dict(item, dictionary_item):
    """Test from_dict class method"""
    new_item = ItemCore.from_dict(dictionary_item)
    assert is_instance(new_item, ItemCore), "Error: ItemCore.from_dict G_item_type"
    assert new_item.name == item.name, "Error: ItemCore.from_dict G_item_name"
    assert new_item.value == item.value, "Error: ItemCore.from_dict G_item_value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_dict item_type"
    

def test_ItemCore_from_json(item, json_item):
    """Test from_json class method"""
    new_item = ItemCore.from_json(json_item)
    assert is_instance(new_item, ItemCore), "Error: ItemCore.from_json G_item_type"
    assert new_item.name == item.name, "Error: ItemCore.from_json G_item_name"
    assert new_item.value == item.value, "Error: ItemCore.from_json G_item_value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_json item_type"

def test_ItemCore_from_yaml(item, yaml_item):
    """Test from_yaml class method"""
    new_item = ItemCore.from_yaml(yaml_item)
    assert is_instance(new_item, ItemCore), "Error: ItemCore.from_yaml G_item_type"
    assert new_item.name == item.name, "Error: ItemCore.from_yaml G_item_name"
    assert new_item.value == item.value, "Error: ItemCore.from_yaml G_item_value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_yaml item_type"
    

def test_ItemCore_from_env_var(item, env_var_item):
    """Test from_env_var class method"""
    # Set up environment variable for testing
    import os
    os.environ["TEST_NAME"] = "TEST_VALUE"
    
    new_item = ItemCore.from_env_var("TEST_NAME")
    assert is_instance(new_item, ItemCore), "Error: ItemCore.from_env_var G_item_type"
    assert new_item.name == "TEST_NAME", "Error: ItemCore.from_env_var G_item_name"
    assert new_item.value == "TEST_VALUE", "Error: ItemCore.from_env_var G_item_value"
    assert new_item.item_type == ItemType.VARIABLE, "Error: ItemCore.from_env_var item_type"
    
    # Clean up
    del os.environ["TEST_NAME"]

#TODO: from_toml()

def test_ItemCore_with_integer_value():
    """Test ItemCore with integer value"""
    item = ItemCore(name="INT_NAME", value=123)
    assert item.name == "INT_NAME", "Error: ItemCore with int name"
    assert item.value == 123, "Error: ItemCore with integer value"
    assert item.item_type == ItemType.ITEM, "Error: ItemCore with int item_type"
    
    item.value = 456
    assert item.value == 456, "Error: ItemCore set int value"
    

def test_ItemCore_with_string_item_type():
    """Test ItemCore with item_type as string"""
    item = ItemCore(name="STR_TYPE", value="VALUE", item_type="variable")
    assert item.name == "STR_TYPE", "Error: ItemCore with string type name"
    assert item.value == "VALUE", "Error: ItemCore with string type value"
    assert item.item_type == "variable", "Error: ItemCore with string type item_type"


def test_ItemCore_with_hex_item_value():
    """Test ItemCore with hexadecimal string value"""
    item = ItemCore(name="HEX_NAME", value=0xCAFE)
    assert item.name == "HEX_NAME", "Error: ItemCore with hex name"
    assert item.value == 51966, f"Error: ItemCore with hex value {item.value}"
    assert item.item_type == ItemType.ITEM, f"Error: ItemCore with hex item_type {item.item_type}"
    assert item.to_dict() == {
        "name": "HEX_NAME",
        "value": 51966,
        "item_type": ItemType.ITEM,
        "project": None,
    }, "Error: ItemCore with hex to_dict"
    assert item.to_json() == '{"name": "HEX_NAME", "value": 51966, "item_type": "item", "project": null}', "Error: ItemCore with hex to_json"
    assert item.to_yaml() == "item_type: item\nname: HEX_NAME\nproject: null\nvalue: 51966\n", "Error: ItemCore with hex to_yaml"
    assert item.to_env_var() == "HEX_NAME=51966", "Error: ItemCore with hex to_env_var"


# [VariableItem Tests]
def test_VariableItem_initialization():
    """Test VariableItem initialization"""
    from hands_scaphoid.objects.VariableItem import VariableItem
    
    var = VariableItem(name="TEST_VAR", value="TEST_VALUE")
    assert var.name == "TEST_VAR", "Error: VariableItem_item_name"
    assert var.value == "TEST_VALUE", "Error: VariableItem_item_value"
    assert var.item_type == ItemType.VARIABLE, "Error: VariableItem.item_type"
    assert var.project is None, "Error: VariableItem_item_project should be None"


def test_VariableItem_repr():
    """Test VariableItem string representation"""
    from hands_scaphoid.objects.VariableItem import VariableItem
    
    var = VariableItem(name="TEST_VAR", value="TEST_VALUE")
    expected_repr = "VariableItem(name=TEST_VAR, value=TEST_VALUE)"
    assert repr(var) == expected_repr, f"Error: VariableItem repr, got {repr(var)}"


def test_VariableItem_serialization():
    """Test VariableItem serialization methods"""
    from hands_scaphoid.objects.VariableItem import VariableItem
    
    var = VariableItem(name="TEST_VAR", value="TEST_VALUE")
    
    # Test to_dict
    expected_dict = {
        "name": "TEST_VAR",
        "value": "TEST_VALUE", 
        "item_type": ItemType.VARIABLE,
        "project": None,
    }
    assert var.to_dict() == expected_dict, "Error: VariableItem.to_dict"
    
    # Test to_json
    expected_json = '{"name": "TEST_VAR", "value": "TEST_VALUE", "item_type": "variable", "project": null}'
    assert var.to_json() == expected_json, "Error: VariableItem.to_json"
    
    # Test to_yaml
    expected_yaml = "item_type: variable\nname: TEST_VAR\nproject: null\nvalue: TEST_VALUE\n"
    assert var.to_yaml() == expected_yaml, "Error: VariableItem.to_yaml"
    
    # Test to_toml
    expected_toml = 'name = "TEST_VAR"\nvalue = "TEST_VALUE"\nitem_type = "variable"\nproject = ""\n'
    assert var.to_toml() == expected_toml, "Error: VariableItem.to_toml"
    
    # Test to_env_var
    expected_env = "TEST_VAR=TEST_VALUE"
    assert var.to_env_var() == expected_env, "Error: VariableItem.to_env_var"


def test_VariableItem_from_methods():
    """Test VariableItem creation from serialized data"""
    from hands_scaphoid.objects.VariableItem import VariableItem
    
    # Test from_dict
    data = {
        "name": "FROM_DICT_VAR",
        "value": "FROM_DICT_VALUE",
        "item_type": "variable",
        "project": None,
    }
    var_from_dict = ItemCore.from_dict(data)
    assert var_from_dict.name == "FROM_DICT_VAR", "Error: from_dict name"
    assert var_from_dict.value == "FROM_DICT_VALUE", "Error: from_dict value"
    assert var_from_dict.item_type == ItemType.VARIABLE, "Error: from_dict item_type"
    
    # Test from_json
    json_str = '{"name": "FROM_JSON_VAR", "value": "FROM_JSON_VALUE", "item_type": "variable", "project": null}'
    var_from_json = ItemCore.from_json(json_str)
    assert var_from_json.name == "FROM_JSON_VAR", "Error: from_json name"
    assert var_from_json.value == "FROM_JSON_VALUE", "Error: from_json value"
    assert var_from_json.item_type == ItemType.VARIABLE, "Error: from_json item_type"
    
    # Test from_yaml
    yaml_str = "item_type: variable\nname: FROM_YAML_VAR\nproject: null\nvalue: FROM_YAML_VALUE\n"
    var_from_yaml = ItemCore.from_yaml(yaml_str)
    assert var_from_yaml.name == "FROM_YAML_VAR", "Error: from_yaml name"
    assert var_from_yaml.value == "FROM_YAML_VALUE", "Error: from_yaml value"
    assert var_from_yaml.item_type == ItemType.VARIABLE, "Error: from_yaml item_type"
