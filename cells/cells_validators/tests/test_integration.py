"""
Integration tests for the complete bones_validator package.
"""

import pytest
from bones_validator import (
    ValidatorMixin,
    SeverityType,
    ConditionOperator,
    ValueCondition,
    create_dotfile_rules,
    create_absolute_path_rules
)

class TestPackageIntegration:
    """Test complete package integration scenarios."""
    
    def test_import_all_public_components(self):
        """Test that all public components can be imported."""
        # Main exports should be available from package root
        from bones_validator import ValidatorMixin, SeverityType, ConditionOperator
        from bones_validator import ValueCondition, ContextCondition, CustomCondition
        from bones_validator import BaseRule, Rule, ConditionalRule, ValidationViolation
        from bones_validator import RuleEngine, ValidationResult
        
        # Helper functions
        from bones_validator import create_dotfile_rules, create_absolute_path_rules
        
        # All imports should succeed
        assert ValidatorMixin is not None
        assert SeverityType is not None
        assert ConditionOperator is not None

class TestRealWorldScenarios:
    """Test real-world validation scenarios."""
    
    def setup_method(self):
        """Set up test item with realistic validation rules."""
        class FilePathValidator(ValidatorMixin):
            def __init__(self, path: str):
                self.path = path
                super().__init__()
                self._setup_validation_rules()
            
            def _setup_validation_rules(self):
                """Set up realistic file path validation rules."""
                # Dotfile rules (when path starts with .)
                dotfile_rules = create_dotfile_rules()
                self.add_conditional_validation_rules(
                    condition_spec=("starts_with", "."),
                    rules=dotfile_rules,
                    group_name="dotfiles"
                )
                
                # Absolute path rules (when path starts with /)
                absolute_rules = create_absolute_path_rules()
                self.add_conditional_validation_rules(
                    condition_spec=("starts_with", "/"),
                    rules=absolute_rules,
                    group_name="absolute_paths"
                )
                
                # Windows path rules (when path contains :)
                windows_rules = [
                    {
                        'name': 'valid_windows_path',
                        'pattern': r'^[a-zA-Z]:\\[a-zA-Z0-9_\\.-]*$',
                        'severity': SeverityType.ERROR,
                        'description': 'Valid Windows path format'
                    },
                    {
                        'name': 'no_reserved_names',
                        'pattern': r'\\(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|\\|$)',
                        'severity': SeverityType.WARNING,
                        'description': 'Avoid Windows reserved names',
                        'inverse': True
                    }
                ]
                self.add_conditional_validation_rules(
                    condition_spec=("contains", ":"),
                    rules=windows_rules,
                    group_name="windows_paths"
                )
                
                # General filename rules (always active)
                self.add_validation_rule(
                    name="no_null_bytes",
                    pattern=r"\x00",
                    severity=SeverityType.ERROR,
                    description="No null bytes in filenames",
                    inverse=True
                )
                
                self.add_validation_rule(
                    name="reasonable_length",
                    pattern=r"^.{1,255}$",
                    severity=SeverityType.WARNING,
                    description="Filename should be 1-255 characters"
                )
            
            @property
            def value(self):
                return self.path
            
            @value.setter
            def value(self, new_path):
                old_path = self.path
                self.path = new_path
                if old_path != new_path:
                    self._on_value_changed(new_path)
        
        self.FilePathValidator = FilePathValidator
    
    def test_dotfile_validation_scenario(self):
        """Test complete dotfile validation scenario."""
        validator = self.FilePathValidator(".bashrc")
        
        # Valid dotfile
        result = validator.validate_value(".bashrc")
        assert result.is_valid == True
        
        # Invalid dotfile with slash
        result = validator.validate_value(".config/invalid")
        assert result.is_valid == False
        assert any("dotfile" in v.rule_name for v in result.violations)
        
        # Test that only dotfile rules are executed for dotfiles
        summary = validator.get_validation_summary()
        dotfile_rules_executed = [r for r in summary['executed_rules'] if 'dotfile' in r]
        windows_rules_executed = [r for r in summary['executed_rules'] if 'windows' in r]
        
        assert len(dotfile_rules_executed) > 0
        assert len(windows_rules_executed) == 0  # Should not execute Windows rules
    
    def test_absolute_path_validation_scenario(self):
        """Test complete absolute path validation scenario."""
        validator = self.FilePathValidator("/usr/bin/python")
        
        # Valid absolute path
        result = validator.validate_value("/usr/bin/python")
        assert result.is_valid == True
        
        # Path with double slashes (warning)
        result = validator.validate_value("/usr//bin/python")
        assert result.is_valid == True  # Warnings don't make invalid
        assert result.warning_count > 0
        
        # Invalid absolute path with invalid characters
        result = validator.validate_value("/usr/bin/\x00invalid")
        assert result.is_valid == False
    
    def test_windows_path_validation_scenario(self):
        """Test Windows path validation scenario."""
        validator = self.FilePathValidator("C:\\Program Files\\app.exe")
        
        # Valid Windows path
        result = validator.validate_value("C:\\Users\\Documents\\file.txt")
        assert result.is_valid == True
        
        # Windows reserved name (should warn)
        result = validator.validate_value("C:\\temp\\CON.txt")
        assert result.warning_count > 0
        
        # Invalid Windows path format
        result = validator.validate_value("C:/unix/style/path")
        # Might still be valid due to other rules, but Windows-specific rules won't match
    
    def test_rule_networking_priority(self):
        """Test that rule networking works with proper priorities."""
        # Test that condition-specific rules are prioritized
        validator = self.FilePathValidator(".vimrc")
        
        # Add conflicting general rule
        validator.add_validation_rule(
            name="no_dots_general",
            pattern=r"\.",
            severity=SeverityType.ERROR,
            description="No dots allowed (general rule)",
            inverse=True
        )
        
        # Dotfile-specific rules should still allow dots for dotfiles
        result = validator.validate_value(".vimrc")
        
        # Check which rules were executed
        summary = validator.get_validation_summary()
        
        # Both general and conditional rules should execute
        assert "no_dots_general" in summary['executed_rules']
        assert any("dotfile" in rule for rule in summary['executed_rules'])
    
    def test_performance_with_many_rules(self):
        """Test performance characteristics with many rules."""
        validator = self.FilePathValidator("test_file.txt")
        
        # Add many rules
        for i in range(50):
            validator.add_validation_rule(
                name=f"rule_{i}",
                pattern=rf"pattern_{i}",
                severity=SeverityType.INFO,
                description=f"Rule {i}",
                inverse=True  # Most will pass
            )
        
        # Validate multiple times
        import time
        start_time = time.time()
        
        for i in range(10):
            result = validator.validate_value(f"test_file_{i}.txt")
        
        end_time = time.time()
        execution_time = end_time - start_time
        
        # Should complete reasonably quickly (adjust threshold as needed)
        assert execution_time < 1.0  # Less than 1 second for 10 validations with 50+ rules
        
        # Check caching is working
        summary = validator.get_validation_summary()
        engine_stats = summary['engine_stats']
        assert engine_stats['engine_stats']['total_validations'] >= 10
    
    def test_error_recovery_and_resilience(self):
        """Test error recovery and resilience."""
        validator = self.FilePathValidator("test.txt")
        
        # Add rule with bad regex pattern
        validator.add_validation_rule(
            name="bad_regex",
            pattern=r"[invalid",  # Invalid regex
            severity=SeverityType.ERROR,
            description="Bad regex rule"
        )
        
        # Should handle bad regex gracefully
        result = validator.validate_value("test.txt")
        assert result is not None
        
        # Should have violation from bad regex handling
        bad_regex_violations = [v for v in result.violations if v.rule_name == "bad_regex"]
        assert len(bad_regex_violations) > 0
        
        # Other rules should still work
        result = validator.validate_value("test\x00null.txt")
        null_violations = [v for v in result.violations if v.rule_name == "no_null_bytes"]
        assert len(null_violations) > 0
    
    def test_complex_conditional_logic(self):
        """Test complex conditional rule logic."""
        validator = self.FilePathValidator("complex_test")
        
        # Add complex conditional rules using multiple conditions
        from bones_validator.conditions.logical_conditions import AndCondition, OrCondition, NotCondition
        
        # Rule for files that start with "test" AND end with ".py"
        python_test_condition = AndCondition([
            ValueCondition(ConditionOperator.STARTS_WITH, "test"),
            ValueCondition(ConditionOperator.ENDS_WITH, ".py")
        ])
        
        validator.add_conditional_validation_rule(
            name="python_test_naming",
            pattern=r"^test_[a-z_]+\.py$",
            severity=SeverityType.WARNING,
            description="Python test files should follow test_*.py pattern",
            activation_condition=python_test_condition
        )
        
        # Test activation
        result = validator.validate_value("test_example.py")
        # Should activate and potentially warn about naming
        
        result = validator.validate_value("example.py")
        # Should not activate this rule
        
        result = validator.validate_value("test_file.txt")
        # Should not activate this rule
        
        # Check rule execution
        summary = validator.get_validation_summary()
        assert len(summary['executed_rules']) > 0
    
    def test_validation_workflow_lifecycle(self):
        """Test complete validation workflow lifecycle."""
        validator = self.FilePathValidator("initial_value.txt")
        
        # Initial state
        assert validator.validation_enabled == True
        assert validator.auto_validate == True
        
        # Validate initial value
        initial_result = validator.validate_value("initial_value.txt")
        assert initial_result.is_valid == True
        
        # Change value (should auto-validate)
        validator.value = "new_value.txt"
        assert validator.is_valid == True
        
        # Add strict rule that fails
        validator.add_validation_rule(
            name="strict_naming",
            pattern=r"^[a-z]+\.txt$",
            severity=SeverityType.ERROR,
            description="Only lowercase letters and .txt"
        )
        
        # Should now be invalid
        assert validator.is_valid == False
        
        # Fix the value
        validator.value = "lowercase.txt"
        assert validator.is_valid == True
        
        # Disable validation
        validator.validation_enabled = False
        validator.value = "INVALID.txt"
        assert validator.is_valid == True  # Should pass when disabled
        
        # Re-enable
        validator.validation_enabled = True
        assert validator.is_valid == False  # Should fail when re-enabled
        
        # Get comprehensive summary
        summary = validator.get_validation_summary()
        assert 'is_valid' in summary
        assert 'violations' in summary
        assert 'engine_stats' in summary
        assert 'executed_rules' in summary