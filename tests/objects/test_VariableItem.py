# [Test imports]
import pytest 

# [Device under test import]
from hands_scaphoid.objects import VariableItem
from hands_scaphoid.types import ItemType

# [Test data]

name = "VARIABLE_NAME"
value= "VARIABLE_VALUE"

@pytest.fixture
def variable():
    global name, value
    return VariableItem(name=name, value=value)

@pytest.fixture
def dictionary_item():
    global name, value
    return {
        "name": name,
        "value": value,
        "item_type": ItemType.VARIABLE,
    }

@pytest.fixture
def dictionary_variable():
    global name, value
    return {
        "name": name,
        "value": value,
        "item_type": ItemType.VARIABLE,
    }
    
@pytest.fixture
def json_item():
    global name, value
    return f'{"name": {name}, "value": {value}, "item_type": "variable"}'
    
    
@pytest.fixture
def yaml_item():
    global name, value
    return f"item_type: variable\nname: {name}\nvalue: {value}\n"

@pytest.fixture
def toml_item():
    global name, value
    return f'[variable_item]\nvalue = {value}\nname = {name}\n'

@pytest.fixture
def env_var_item():
    return "TEST_NAME=TEST_VALUE"

# [Test cases]
def test_ItemCore_initialization(item):
    """Core elements of ItemCore"""
    assert item.name == "TEST_NAME", "Error: ItemCore.name"
    assert item.value == "TEST_VALUE", "Error: ItemCore.value"
    assert item.item_type == ItemType.ITEM, "Error: ItemCore.item_type"
