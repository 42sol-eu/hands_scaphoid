#%% [Test imports]
import pytest 

#%% [Device under test import]
from hands_scaphoid.objects import ItemCore
from hands_scaphoid.types import ItemType

#%% [Test data]

@pytest.fixture
def item():
    return ItemCore(name="TEST_NAME", value="TEST_VALUE")

@pytest.fixture
def dictionary_item():
    return {
        "name": "TEST_NAME",
        "value": "TEST_VALUE",
        "item_type": ItemType.ITEM,
    }

@pytest.fixture
def dictionary_variable():
    return {
        "name": "DICT_NAME",
        "value": "DICT_VALUE",
        "item_type": ItemType.VARIABLE,
    }
    
@pytest.fixture
def json_item():
    return '{"name": "TEST_NAME", "value": "TEST_VALUE", "item_type": "item"}'
    
    
@pytest.fixture
def yaml_item():
    return "item_type: item\nname: TEST_NAME\nvalue: TEST_VALUE\n"

@pytest.fixture
def toml_item():
    return '[item_type]\nvalue = 0\nname = "TEST_NAME"\nvalue = "TEST_VALUE"\n'

@pytest.fixture
def env_var_item():
    return "TEST_NAME=TEST_VALUE"

#%% [Test cases]
def test_ItemCore_initialization(item):
    """Core elements of ItemCore"""
    assert item.name == "TEST_NAME", "Error: ItemCore.name"
    assert item.value == "TEST_VALUE", "Error: ItemCore.value"
    assert item.item_type == ItemType.ITEM, "Error: ItemCore.item_type"


def test_ItemCore_set_value(item):
    """Test setting value"""
    assert item.value == "TEST_VALUE", "Error: ItemCore.value setter"
    item.value = "NEW_VALUE"
    assert item.value == "NEW_VALUE", "Error: ItemCore.value setter"
    assert item._value == "NEW_VALUE", "Error: ItemCore._value "
    
    
def test_ItemCore_str_repr(item):
    """Test string and repr methods"""
    assert str(item) == 'TEST_NAME="TEST_VALUE"', "Error: ItemCore.__str__"
    assert repr(item) == "ItemCore(name=TEST_NAME, value=TEST_VALUE, item_type=ITEM)", "Error: ItemCore.__repr__"

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
    

def test_ItemCore_from_dict(item, dictionary_item):
    """Test from_dict class method"""
    new_item = ItemCore.from_dict(dictionary_item)
    assert isinstance(new_item, ItemCore), "Error: ItemCore.from_dict type"
    assert new_item.name == item.name, "Error: ItemCore.from_dict name"
    assert new_item.value == item.value, "Error: ItemCore.from_dict value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_dict item_type"
    

def test_ItemCore_from_json(item, json_item):
    """Test from_json class method"""
    new_item = ItemCore.from_json(json_item)
    assert isinstance(new_item, ItemCore), "Error: ItemCore.from_json type"
    assert new_item.name == item.name, "Error: ItemCore.from_json name"
    assert new_item.value == item.value, "Error: ItemCore.from_json value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_json item_type"

def test_ItemCore_from_yaml(item, yaml_item):
    """Test from_yaml class method"""
    new_item = ItemCore.from_yaml(yaml_item)
    assert isinstance(new_item, ItemCore), "Error: ItemCore.from_yaml type"
    assert new_item.name == item.name, "Error: ItemCore.from_yaml name"
    assert new_item.value == item.value, "Error: ItemCore.from_yaml value"
    assert new_item.item_type == item.item_type, "Error: ItemCore.from_yaml item_type"
    

def test_ItemCore_from_env_var(item, env_var_item):
    """Test from_env_var class method"""
    # Set up environment variable for testing
    import os
    os.environ["TEST_NAME"] = "TEST_VALUE"
    
    new_item = ItemCore.from_env_var("TEST_NAME")
    assert isinstance(new_item, ItemCore), "Error: ItemCore.from_env_var type"
    assert new_item.name == "TEST_NAME", "Error: ItemCore.from_env_var name"
    assert new_item.value == "TEST_VALUE", "Error: ItemCore.from_env_var value"
    assert new_item.item_type == ItemType.VARIABLE, "Error: ItemCore.from_env_var item_type"
    
    # Clean up
    del os.environ["TEST_NAME"]


def test_ItemCore_with_integer_value():
    """Test ItemCore with integer value"""
    item = ItemCore(name="INT_NAME", value=123)
    assert item.name == "INT_NAME", "Error: ItemCore with int name"
    assert item.value == 123, "Error: ItemCore with int value"
    assert item.item_type == ItemType.ITEM, "Error: ItemCore with int item_type"
    
    item.value = 456
    assert item.value == 456, "Error: ItemCore set int value"
    

def test_ItemCore_with_string_type():
    """Test ItemCore with item_type as string"""
    item = ItemCore(name="STR_TYPE", value="VALUE", item_type="variable")
    assert item.name == "STR_TYPE", "Error: ItemCore with string type name"
    assert item.value == "VALUE", "Error: ItemCore with string type value"
    assert item.item_type == "variable", "Error: ItemCore with string type item_type"


def test_ItemCore_with_hex_value():
    """Test ItemCore with hexadecimal string value"""
    item = ItemCore(name="HEX_NAME", value=0xCAFE)
    assert item.name == "HEX_NAME", "Error: ItemCore with hex name"
    assert item.value == 51966, f"Error: ItemCore with hex value {item.value}"
    assert item.item_type == ItemType.ITEM, f"Error: ItemCore with hex item_type {item.item_type}"
    assert item.to_dict() == {
        "name": "HEX_NAME",
        "value": 51966,
        "item_type": ItemType.ITEM,
    }, "Error: ItemCore with hex to_dict"
    assert item.to_json() == '{"name": "HEX_NAME", "value": 51966, "item_type": "item"}', "Error: ItemCore with hex to_json"
    assert item.to_yaml() == "item_type: item\nname: HEX_NAME\nvalue: 51966\n", "Error: ItemCore with hex to_yaml"
    assert item.to_env_var() == "HEX_NAME=51966", "Error: ItemCore with hex to_env_var"
