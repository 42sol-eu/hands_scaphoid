# Bones Validator

A rule-based validation framework with conditional rule networks.

## Features

- **Rule-based validation** with flexible pattern matching
- **Conditional rule networks** - rules can be enabled/disabled based on conditions
- **Rule chaining and dependencies** - create complex validation workflows
- **Multiple condition types** - value-based, logical, and contextual conditions
- **Extensible architecture** - easy to add new rule types and conditions
- **High performance** - optimized execution planning and dependency resolution

## Architecture

The bones_validator package provides:

- **Core Engine**: Rule execution and condition evaluation
- **Rule System**: Base rules, conditional rules, and rule groups
- **Condition System**: Various condition types for complex logic
- **Connectors**: Rule networking and dependency management
- **Validation Framework**: Integration mixin and result handling

## Example Usage

```python
from bones_validator import RuleEngine, ValueCondition, ConditionalRule

# Create a rule engine
engine = RuleEngine()

# Create conditional rules
dotfile_condition = ValueCondition("starts_with", ".")
dotfile_rules = [
    Rule("hidden_file", r"^\.[^/]*$", "Must be valid hidden file"),
    Rule("no_double_dots", r"^\.{2,}", "No multiple dots", inverse=True)
]

absolute_condition = ValueCondition("starts_with", "/")  
absolute_rules = [
    Rule("valid_absolute", r"^/[a-zA-Z0-9_/.-]*$", "Valid absolute path"),
    Rule("no_root_access", r"^/root/", "No root access", inverse=True)
]

# Add conditional rule groups
engine.add_conditional_rules(dotfile_condition, dotfile_rules)
engine.add_conditional_rules(absolute_condition, absolute_rules)

# Validate values
result = engine.validate(".bashrc")  # Uses dotfile rules
result = engine.validate("/usr/bin/python")  # Uses absolute path rules
```