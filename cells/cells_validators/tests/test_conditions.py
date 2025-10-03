"""
Tests for value conditions.
"""

import pytest
from bones_validator.conditions.value_conditions import ValueCondition, ContextCondition, CustomCondition
from bones_validator.types.rule_types import ConditionOperator, SeverityType

class TestValueCondition:
    """Test ValueCondition functionality."""
    
    def test_equals_condition(self):
        """Test EQUALS operator."""
        condition = ValueCondition(ConditionOperator.EQUALS, "test")
        
        assert condition.evaluate({'value': 'test'}) == True
        assert condition.evaluate({'value': 'other'}) == False
        assert condition.evaluate({'value': None}) == False
    
    def test_starts_with_condition(self):
        """Test STARTS_WITH operator.""" 
        condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        
        assert condition.evaluate({'value': '.bashrc'}) == True
        assert condition.evaluate({'value': 'bashrc'}) == False
        assert condition.evaluate({'value': '..hidden'}) == True
    
    def test_ends_with_condition(self):
        """Test ENDS_WITH operator."""
        condition = ValueCondition(ConditionOperator.ENDS_WITH, ".txt")
        
        assert condition.evaluate({'value': 'file.txt'}) == True
        assert condition.evaluate({'value': 'file.py'}) == False
        assert condition.evaluate({'value': 'readme.txt'}) == True
    
    def test_contains_condition(self):
        """Test CONTAINS operator."""
        condition = ValueCondition(ConditionOperator.CONTAINS, "test")
        
        assert condition.evaluate({'value': 'test_file'}) == True
        assert condition.evaluate({'value': 'my_test_value'}) == True
        assert condition.evaluate({'value': 'other_file'}) == False
    
    def test_not_contains_condition(self):
        """Test NOT_CONTAINS operator."""
        condition = ValueCondition(ConditionOperator.NOT_CONTAINS, "bad")
        
        assert condition.evaluate({'value': 'good_file'}) == True
        assert condition.evaluate({'value': 'bad_file'}) == False
    
    def test_matches_condition(self):
        """Test MATCHES operator with regex."""
        condition = ValueCondition(ConditionOperator.MATCHES, r"^\d+$")
        
        assert condition.evaluate({'value': '123'}) == True
        assert condition.evaluate({'value': 'abc'}) == False
        assert condition.evaluate({'value': '12a'}) == False
    
    def test_length_conditions(self):
        """Test length-based conditions."""
        gt_condition = ValueCondition(ConditionOperator.LENGTH_GT, 5)
        lt_condition = ValueCondition(ConditionOperator.LENGTH_LT, 10)
        eq_condition = ValueCondition(ConditionOperator.LENGTH_EQ, 4)
        
        test_value = {'value': 'test'}
        long_value = {'value': 'this_is_a_long_filename'}
        
        assert gt_condition.evaluate(test_value) == False  # 4 <= 5
        assert lt_condition.evaluate(test_value) == True   # 4 < 10
        assert eq_condition.evaluate(test_value) == True   # 4 == 4
        
        assert gt_condition.evaluate(long_value) == True   # 21 > 5
        assert lt_condition.evaluate(long_value) == False  # 21 >= 10
    
    def test_case_sensitivity(self):
        """Test case sensitivity options."""
        sensitive = ValueCondition(ConditionOperator.STARTS_WITH, "Test", case_sensitive=True)
        insensitive = ValueCondition(ConditionOperator.STARTS_WITH, "Test", case_sensitive=False)
        
        assert sensitive.evaluate({'value': 'Test_file'}) == True
        assert sensitive.evaluate({'value': 'test_file'}) == False
        
        assert insensitive.evaluate({'value': 'Test_file'}) == True
        assert insensitive.evaluate({'value': 'test_file'}) == True
        assert insensitive.evaluate({'value': 'TEST_file'}) == True
    
    def test_disabled_condition(self):
        """Test disabled condition always returns True."""
        condition = ValueCondition(ConditionOperator.EQUALS, "test")
        condition.enabled = False
        
        assert condition.evaluate({'value': 'different'}) == True
        assert condition.evaluate({'value': 'test'}) == True

class TestContextCondition:
    """Test ContextCondition functionality."""
    
    def test_has_attribute_condition(self):
        """Test HAS_ATTRIBUTE operator."""
        condition = ContextCondition(ConditionOperator.HAS_ATTRIBUTE, "file_type")
        
        context_with_attr = {'attributes': {'file_type': 'document'}}
        context_without_attr = {'attributes': {}}
        
        assert condition.evaluate(context_with_attr) == True
        assert condition.evaluate(context_without_attr) == False
    
    def test_attribute_equals_condition(self):
        """Test ATTRIBUTE_EQUALS operator."""
        condition = ContextCondition(ConditionOperator.ATTRIBUTE_EQUALS, "file_type", "document")
        
        context_match = {'attributes': {'file_type': 'document'}}
        context_no_match = {'attributes': {'file_type': 'image'}}
        context_no_attr = {'attributes': {}}
        
        assert condition.evaluate(context_match) == True
        assert condition.evaluate(context_no_match) == False
        assert condition.evaluate(context_no_attr) == False
    
    def test_is_type_condition(self):
        """Test IS_TYPE operator."""
        condition = ContextCondition(ConditionOperator.IS_TYPE, "type", "str")
        
        context_str = {'type': 'str'}
        context_int = {'type': 'int'}
        
        assert condition.evaluate(context_str) == True
        assert condition.evaluate(context_int) == False

class TestCustomCondition:
    """Test CustomCondition functionality."""
    
    def test_custom_function(self):
        """Test custom validation function."""
        def is_even_length(context):
            value = context.get('value', '')
            return len(str(value)) % 2 == 0
        
        condition = CustomCondition(is_even_length, "Even length check")
        
        assert condition.evaluate({'value': 'test'}) == True   # 4 chars
        assert condition.evaluate({'value': 'hello'}) == False # 5 chars
        assert condition.evaluate({'value': ''}) == True       # 0 chars
    
    def test_custom_function_with_context(self):
        """Test custom function using full context."""
        def has_extension(context):
            value = context.get('value', '')
            return '.' in str(value)
        
        condition = CustomCondition(has_extension, "Has file extension")
        
        assert condition.evaluate({'value': 'file.txt'}) == True
        assert condition.evaluate({'value': 'filename'}) == False
        assert condition.evaluate({'value': '.hidden'}) == True
    
    def test_custom_function_error_handling(self):
        """Test error handling in custom functions."""
        def failing_function(context):
            raise ValueError("Intentional error")
        
        condition = CustomCondition(failing_function, "Failing function")
        
        # Should return False on error and log the error
        assert condition.evaluate({'value': 'test'}) == False