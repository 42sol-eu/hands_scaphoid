"""
Tests for rule engine functionality.
"""

import pytest
from bones_validator.core.rule_engine import RuleEngine, ValidationResult
from bones_validator.rules.base_rule import Rule, ConditionalRule
from bones_validator.conditions.value_conditions import ValueCondition
from bones_validator.types.rule_types import SeverityType, ConditionOperator, ExecutionStrategy, EngineConfig

class TestRuleEngine:
    """Test RuleEngine functionality."""
    
    def test_engine_initialization(self):
        """Test basic engine initialization."""
        engine = RuleEngine()
        
        assert len(engine.rules) == 0
        assert len(engine.rule_groups) == 0
        assert engine.config.execution_strategy == ExecutionStrategy.FAIL_FAST
    
    def test_add_basic_rule(self):
        """Test adding a basic rule."""
        engine = RuleEngine()
        rule = Rule("test_rule", r"^test", SeverityType.ERROR, "Must start with test")
        
        engine.add_rule(rule)
        
        assert "test_rule" in engine.rules
        assert engine.rules["test_rule"] == rule
        assert "test_rule" in engine.execution_order
    
    def test_remove_rule(self):
        """Test removing a rule."""
        engine = RuleEngine()
        rule = Rule("test_rule", r"^test", SeverityType.ERROR, "Test rule")
        
        engine.add_rule(rule)
        assert "test_rule" in engine.rules
        
        result = engine.remove_rule("test_rule")
        assert result == True
        assert "test_rule" not in engine.rules
        
        # Try to remove non-existent rule
        result = engine.remove_rule("non_existent")
        assert result == False
    
    def test_basic_validation_success(self):
        """Test successful validation."""
        engine = RuleEngine()
        rule = Rule("starts_with_test", r"^test", SeverityType.ERROR, "Must start with test")
        engine.add_rule(rule)
        
        result = engine.validate("test_value")
        
        assert result.is_valid == True
        assert len(result.violations) == 0
        assert "starts_with_test" in result.executed_rules
        assert len(result.skipped_rules) == 0
    
    def test_basic_validation_failure(self):
        """Test validation failure."""
        engine = RuleEngine()
        rule = Rule("starts_with_test", r"^test", SeverityType.ERROR, "Must start with test")
        engine.add_rule(rule)
        
        result = engine.validate("other_value")
        
        assert result.is_valid == False
        assert len(result.violations) == 1
        assert result.violations[0].rule_name == "starts_with_test"
        assert result.violations[0].severity == SeverityType.ERROR
    
    def test_conditional_rules_dotfiles(self, sample_values):
        """Test conditional rules for dotfiles."""
        engine = RuleEngine()
        
        # Create condition for dotfiles
        dotfile_condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        
        # Create dotfile-specific rules
        dotfile_rules = [
            Rule("valid_dotfile", r"^\.[^/\\]+$", SeverityType.ERROR, "Valid dotfile format"),
            Rule("no_double_dots", r"^\.{2,}", SeverityType.WARNING, "No multiple dots", inverse=True)
        ]
        
        # Add conditional rules
        engine.add_conditional_rules(dotfile_condition, dotfile_rules, "dotfile_group")
        
        # Test dotfile validation
        result = engine.validate(".bashrc")
        assert result.is_valid == True
        assert len([r for r in result.executed_rules if r.startswith("valid_dotfile")]) > 0
        
        # Test non-dotfile (rules should be skipped)
        result = engine.validate("regular_file.txt")
        assert result.is_valid == True  # No rules executed, so valid
        assert len(result.executed_rules) == 0  # Rules were skipped due to condition
    
    def test_conditional_rules_absolute_paths(self, sample_values):
        """Test conditional rules for absolute paths."""
        engine = RuleEngine()
        
        # Create condition for absolute paths  
        absolute_condition = ValueCondition(ConditionOperator.STARTS_WITH, "/")
        
        # Create absolute path rules
        absolute_rules = [
            Rule("valid_absolute", r"^/[a-zA-Z0-9_/.-]*$", SeverityType.ERROR, "Valid absolute path"),
            Rule("no_double_slashes", r"//+", SeverityType.WARNING, "No double slashes", inverse=True)
        ]
        
        # Add conditional rules
        engine.add_conditional_rules(absolute_condition, absolute_rules, "absolute_path_group")
        
        # Test absolute path validation
        result = engine.validate("/usr/bin/python")
        assert result.is_valid == True
        
        # Test relative path (should skip absolute path rules)
        result = engine.validate("relative/path")
        assert result.is_valid == True
        assert len(result.executed_rules) == 0
    
    def test_multiple_conditional_rule_groups(self):
        """Test multiple conditional rule groups working together."""
        engine = RuleEngine()
        
        # Dotfile rules
        dotfile_condition = ValueCondition(ConditionOperator.STARTS_WITH, ".")
        dotfile_rules = [
            Rule("dotfile_rule", r"^\.[^/]+$", SeverityType.ERROR, "Valid dotfile")
        ]
        engine.add_conditional_rules(dotfile_condition, dotfile_rules, "dotfiles")
        
        # Absolute path rules
        absolute_condition = ValueCondition(ConditionOperator.STARTS_WITH, "/")
        absolute_rules = [
            Rule("absolute_rule", r"^/.*", SeverityType.ERROR, "Valid absolute path")
        ]
        engine.add_conditional_rules(absolute_condition, absolute_rules, "absolute")
        
        # Test dotfile - should only execute dotfile rules
        result = engine.validate(".bashrc")
        assert result.is_valid == True
        assert any("dotfile_rule" in r for r in result.executed_rules)
        assert not any("absolute_rule" in r for r in result.executed_rules)
        
        # Test absolute path - should only execute absolute rules
        result = engine.validate("/etc/hosts")
        assert result.is_valid == True
        assert any("absolute_rule" in r for r in result.executed_rules)
        assert not any("dotfile_rule" in r for r in result.executed_rules)
    
    def test_rule_dependencies(self):
        """Test rule dependency ordering."""
        engine = RuleEngine()
        
        # Create rules with dependencies
        rule1 = Rule("rule1", r".*", SeverityType.INFO, "Rule 1")
        rule2 = Rule("rule2", r".*", SeverityType.INFO, "Rule 2")
        rule3 = Rule("rule3", r".*", SeverityType.INFO, "Rule 3")
        
        engine.add_rule(rule3)  # Add in reverse order
        engine.add_rule(rule2)
        engine.add_rule(rule1)
        
        # Add dependencies: rule2 depends on rule1, rule3 depends on rule2
        engine.add_rule_dependency("rule2", "rule1")
        engine.add_rule_dependency("rule3", "rule2")
        
        # Check execution order respects dependencies
        expected_order = ["rule1", "rule2", "rule3"]
        assert engine.execution_order == expected_order
    
    def test_execution_strategies(self):
        """Test different execution strategies."""
        # Fail fast strategy
        fail_fast_config = EngineConfig(execution_strategy=ExecutionStrategy.FAIL_FAST)
        engine = RuleEngine(fail_fast_config)
        
        # Add multiple rules, first one will fail
        rule1 = Rule("fail_rule", r"^success", SeverityType.ERROR, "Must start with success")
        rule2 = Rule("pass_rule", r".*", SeverityType.INFO, "Always passes")
        
        engine.add_rule(rule1)
        engine.add_rule(rule2)
        
        result = engine.validate("failure_value")
        
        # Should stop after first error
        assert result.is_valid == False
        assert len(result.violations) == 1
        assert "pass_rule" not in result.executed_rules  # Should not execute due to fail-fast
    
    def test_caching(self):
        """Test result caching."""
        config = EngineConfig(enable_caching=True)
        engine = RuleEngine(config)
        
        rule = Rule("test_rule", r"^test", SeverityType.ERROR, "Test rule")
        engine.add_rule(rule)
        
        # First validation
        result1 = engine.validate("test_value")
        
        # Second validation with same value (should use cache)
        result2 = engine.validate("test_value")
        
        assert result1.is_valid == result2.is_valid
        assert len(result1.violations) == len(result2.violations)
        
        # Check stats show cache hit
        stats = engine.get_stats()
        assert stats['engine_stats']['cache_hits'] > 0
    
    def test_performance_stats(self):
        """Test performance statistics tracking."""
        engine = RuleEngine()
        rule = Rule("test_rule", r".*", SeverityType.INFO, "Test rule")
        engine.add_rule(rule)
        
        # Perform multiple validations
        for i in range(5):
            engine.validate(f"value_{i}")
        
        stats = engine.get_stats()
        
        assert stats['engine_stats']['total_validations'] == 5
        assert stats['engine_stats']['rule_executions'] == 5
        assert stats['rule_stats']['test_rule']['executions'] == 5
    
    def test_validation_result_properties(self):
        """Test ValidationResult properties and methods."""
        engine = RuleEngine()
        
        # Add rules with different severities
        error_rule = Rule("error_rule", r"^error", SeverityType.ERROR, "Error rule", inverse=True)
        warning_rule = Rule("warning_rule", r"^warning", SeverityType.WARNING, "Warning rule", inverse=True)
        info_rule = Rule("info_rule", r"^info", SeverityType.INFO, "Info rule", inverse=True)
        
        engine.add_rule(error_rule)
        engine.add_rule(warning_rule)
        engine.add_rule(info_rule)
        
        # Validate value that violates all rules
        result = engine.validate("test_value")
        
        assert result.error_count == 1
        assert result.warning_count == 1  
        assert result.info_count == 1
        assert result.is_valid == False  # Has errors
        
        # Test to_dict method
        result_dict = result.to_dict()
        assert 'value' in result_dict
        assert 'is_valid' in result_dict
        assert 'violations' in result_dict
        assert result_dict['error_count'] == 1