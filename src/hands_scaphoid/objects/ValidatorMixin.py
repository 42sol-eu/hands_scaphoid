#!/usr/bin/env python3
"""
ValidationMixin module for flexible validation system.

File:
    name: ValidatorMixin.py
    uuid: c7ea69be-ea5c-4368-ae2f-30e7acb858fd
    date: 2025-10-03

Description:
    Comprehensive validation mixin with rule-based system, severity levels,
    and support for complex logical operations and cross-platform validation

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]

Abbreviations:
- OS[system]: Operating System
- AND/OR[logic]: Logical operators for rule combinations
"""

# [Standard library imports]
import re
import platform
from typing import List, Dict, Optional, Callable, Union, Any
from dataclasses import dataclass

# [Local imports]  
from ..__base__ import logger, console
from ..types.SeverityType import SeverityType

# [Third party imports]
# - none

@dataclass
class ValidationRule:
    """
    Represents a single validation rule.
    
    Attributes:
        name: Unique identifier for the rule
        pattern: Regex pattern or custom validator function
        severity: ERROR, WARNING, or INFO
        description: Human-readable explanation
        inverse: If True, inverts the logic (allow only matching)
        enabled: Whether this rule is active
    """
    name: str
    pattern: Union[str, Callable[[str], bool]]
    severity: SeverityType
    description: str
    inverse: bool = False
    enabled: bool = True

@dataclass  
class ValidationViolation:
    """
    Represents a validation rule violation.
    
    Attributes:
        rule_name: Name of the violated rule
        severity: Severity level of the violation
        message: Detailed violation message
        value: The value that caused the violation
    """
    rule_name: str
    severity: SeverityType
    message: str
    value: str

class ValidationMixin:
    """
    Mixin class providing comprehensive validation functionality.

    This mixin adds validation capabilities with:
    - Rule-based validation system with severity levels
    - Support for regex patterns and custom validator functions
    - Cross-platform path validation
    - Strict mode for enhanced validation
    - Logical rule combinations (AND/OR)
    - Built-in rules for common validation scenarios
    """

    def __init__(self, strict_mode: bool = False, cross_platform: bool = False):
        # Don't call super() to avoid issues with multiple inheritance
        # Let the concrete class handle the MRO properly
        
        self._validation_rules: Dict[str, ValidationRule] = {}
        self._strict_mode = strict_mode
        self._cross_platform = cross_platform
        self._validation_enabled = True
        
        # Initialize built-in rules
        self._setup_builtin_rules()
        
        # Update rule severities based on mode settings
        self._update_rule_severities()

    @property
    def strict_mode(self) -> bool:
        """Get strict mode setting."""
        return self._strict_mode
        
    @strict_mode.setter  
    def strict_mode(self, value: bool):
        """Set strict mode and update rule severities."""
        self._strict_mode = value
        self._update_rule_severities()
        
    @property
    def cross_platform(self) -> bool:
        """Get cross-platform mode setting."""
        return self._cross_platform
        
    @cross_platform.setter
    def cross_platform(self, value: bool):
        """Set cross-platform mode and update rule severities."""
        self._cross_platform = value
        self._update_rule_severities()
        
    @property
    def validation_enabled(self) -> bool:
        """Get validation enabled status."""
        return self._validation_enabled
        
    @validation_enabled.setter
    def validation_enabled(self, value: bool):
        """Enable or disable validation."""
        self._validation_enabled = value

    def add_rule(self, 
                 name: str,
                 pattern: Union[str, Callable[[str], bool]],
                 severity: SeverityType = SeverityType.ERROR,
                 description: str = "",
                 inverse: bool = False) -> None:
        """
        Add a validation rule.

        Args:
            name: Unique identifier for the rule
            pattern: Regex pattern string or custom validator function
            severity: ERROR, WARNING, or INFO
            description: Human-readable explanation
            inverse: If True, inverts the logic (reject matches instead of requiring them)
        """
        if not description:
            description = f"Custom rule: {name}"
            
        rule = ValidationRule(
            name=name,
            pattern=pattern, 
            severity=severity,
            description=description,
            inverse=inverse
        )
        
        self._validation_rules[name] = rule
        logger.debug(f"Added validation rule '{name}' with severity {severity.name}")

    def remove_rule(self, name: str) -> bool:
        """
        Remove a validation rule.
        
        Args:
            name: Name of the rule to remove
            
        Returns:
            bool: True if rule was removed, False if not found
        """
        if name in self._validation_rules:
            del self._validation_rules[name]
            logger.debug(f"Removed validation rule '{name}'")
            return True
        return False

    def enable_rule(self, name: str) -> bool:
        """Enable a specific validation rule."""
        if name in self._validation_rules:
            self._validation_rules[name].enabled = True
            return True
        return False
        
    def disable_rule(self, name: str) -> bool:
        """Disable a specific validation rule."""
        if name in self._validation_rules:
            self._validation_rules[name].enabled = False
            return True
        return False

    def get_rules(self) -> Dict[str, ValidationRule]:
        """Get all validation rules."""
        return self._validation_rules.copy()

    def validate(self) -> tuple[bool, List[ValidationViolation]]:
        """
        Validate the item's value against all enabled rules.

        Returns:
            tuple: (is_valid, list_of_violations)
                - is_valid: True if no ERROR-level violations found
                - violations: List of all violations found
        """
        if not self._validation_enabled:
            return True, []
            
        violations = []
        value_str = str(getattr(self, 'value', ''))
        
        for rule in self._validation_rules.values():
            if not rule.enabled:
                continue
                
            violation = self._check_rule(rule, value_str)
            if violation:
                violations.append(violation)
                
        # Log violations
        for violation in violations:
            if violation.severity.is_error:
                logger.error(f"Validation error: {violation.message}")
            elif violation.severity.is_warning:
                logger.warning(f"Validation warning: {violation.message}")
            else:
                logger.debug(f"Validation info: {violation.message}")
        
        # Valid if no ERROR-level violations
        is_valid = not any(v.severity.is_error for v in violations)
        return is_valid, violations

    def _check_rule(self, rule: ValidationRule, value: str) -> Optional[ValidationViolation]:
        """Check a single rule against the value."""
        try:
            if isinstance(rule.pattern, str):
                # Regex pattern
                match = re.search(rule.pattern, value) is not None
            else:
                # Custom validator function
                match = rule.pattern(value)
                
            # Apply inverse logic if needed
            if rule.inverse:
                match = not match
                
            # If rule fails, create violation
            if not match:
                message = f"{rule.description}: '{value}'"
                return ValidationViolation(
                    rule_name=rule.name,
                    severity=rule.severity,
                    message=message,
                    value=value
                )
                
        except Exception as e:
            logger.error(f"Error checking rule '{rule.name}': {e}")
            return ValidationViolation(
                rule_name=rule.name,
                severity=SeverityType.ERROR,
                message=f"Rule check failed: {e}",
                value=value
            )
            
        return None

    def _setup_builtin_rules(self) -> None:
        """Set up built-in validation rules."""
        # Invalid characters that should never be in paths
        self.add_rule(
            name="invalid_chars",
            pattern=r'[<>:"|?*\x00-\x1f]',
            severity=SeverityType.ERROR,
            description="Contains invalid characters",
            inverse=True  # Reject if matches found
        )
        
        # Uncommon characters that are questionable but not invalid
        self.add_rule(
            name="uncommon_chars", 
            pattern=r'[^\w\-_./\\:~@+%=]',
            severity=SeverityType.WARNING,
            description="Contains uncommon characters",
            inverse=True  # Reject if matches found
        )
        
        # Leading/trailing spaces
        self.add_rule(
            name="whitespace_trim",
            pattern=r'^\s+|\s+$',
            severity=SeverityType.WARNING,
            description="Has leading or trailing whitespace",
            inverse=True
        )
        
        # Multiple consecutive separators
        self.add_rule(
            name="multiple_separators",
            pattern=r'[/\\]{2,}',
            severity=SeverityType.WARNING,
            description="Contains multiple consecutive path separators",
            inverse=True
        )
        
        # Path traversal patterns that could be dangerous
        self.add_rule(
            name="path_traversal_safe",
            pattern=r'^\.\./|/\.\./|\\\.\.\\|\\\.\.$|/\.\.$',
            severity=SeverityType.INFO,
            description="Contains path traversal patterns",
            inverse=True
        )

    def _update_rule_severities(self) -> None:
        """Update rule severities based on strict_mode and cross_platform settings."""
        # In strict mode, warnings become errors
        if self._strict_mode:
            for rule in self._validation_rules.values():
                if rule.name == "uncommon_chars":
                    rule.severity = SeverityType.ERROR
                    
        # Cross-platform mode: check OS-specific path separators
        if self._cross_platform:
            current_os = platform.system().lower()
            
            if current_os == "windows":
                # Warn about Unix separators on Windows
                self.add_rule(
                    name="cross_platform_separator",
                    pattern=r'/',
                    severity=SeverityType.WARNING,
                    description="Uses Unix path separator on Windows",
                    inverse=True
                )
            else:
                # Warn about Windows separators on Unix-like systems
                self.add_rule(
                    name="cross_platform_separator", 
                    pattern=r'\\',
                    severity=SeverityType.WARNING,
                    description="Uses Windows path separator on Unix-like system",
                    inverse=True
                )

    def add_path_rules(self) -> None:
        """Add path-specific validation rules."""
        # Allow relative path components
        self.add_rule(
            name="relative_path_components",
            pattern=r'^\./|^\.\.$|/\./|/\.\.$',
            severity=SeverityType.INFO,
            description="Uses relative path components",
            inverse=False  # Allow these patterns
        )
        
        # Validate absolute paths
        self.add_rule(
            name="absolute_path_format",
            pattern=r'^([a-zA-Z]:[/\\]|/).*',
            severity=SeverityType.INFO,
            description="Absolute path format",
            inverse=False
        )
        
        # Check for reserved Windows names
        windows_reserved = r'^(CON|PRN|AUX|NUL|COM[1-9]|LPT[1-9])(\.|$)'
        self.add_rule(
            name="windows_reserved_names",
            pattern=windows_reserved,
            severity=SeverityType.WARNING,
            description="Uses Windows reserved name",
            inverse=True
        )

    def add_custom_rule_group(self, 
                             group_name: str,
                             rules: List[Dict[str, Any]],
                             operator: str = "AND") -> None:
        """
        Add a group of related rules.
        
        Args:
            group_name: Name for the rule group
            rules: List of rule dictionaries with keys: name, pattern, severity, description
            operator: "AND" or "OR" - how to combine rules (future enhancement)
        """
        for i, rule_data in enumerate(rules):
            rule_name = f"{group_name}_{i}" if 'name' not in rule_data else rule_data['name']
            
            self.add_rule(
                name=rule_name,
                pattern=rule_data.get('pattern', '.*'),
                severity=rule_data.get('severity', SeverityType.ERROR),
                description=rule_data.get('description', f"Rule {rule_name}"),
                inverse=rule_data.get('inverse', False)
            )

    def to_dict(self) -> dict:
        """
        Serialize the validation configuration to a dictionary.

        Returns:
            dict: Dictionary representation including validation rules
        """
        data = super().to_dict() if hasattr(super(), 'to_dict') else {}
        
        data.update({
            "strict_mode": self._strict_mode,
            "cross_platform": self._cross_platform,
            "validation_enabled": self._validation_enabled,
            "validation_rules": {
                name: {
                    "pattern": rule.pattern if isinstance(rule.pattern, str) else "custom_function",
                    "severity": rule.severity.value,
                    "description": rule.description,
                    "inverse": rule.inverse,
                    "enabled": rule.enabled
                }
                for name, rule in self._validation_rules.items()
            }
        })
        
        return data

    @classmethod
    def from_dict(cls, data: dict) -> "ValidationMixin":
        """
        Create ValidationMixin from dictionary representation. 
        
        Args:
            data: Dictionary containing validation configuration
            
        Returns:
            ValidationMixin: Configured instance
        """
        strict_mode = data.get("strict_mode", False)
        cross_platform = data.get("cross_platform", False)
        
        # Create base instance
        instance = cls(strict_mode=strict_mode, cross_platform=cross_platform)
        
        # Set validation enabled state
        instance.validation_enabled = data.get("validation_enabled", True)
        
        # Load custom rules (built-in rules are loaded automatically)
        rules_data = data.get("validation_rules", {})
        for name, rule_data in rules_data.items():
            if name not in instance._validation_rules:  # Don't override built-in rules
                instance.add_rule(
                    name=name,
                    pattern=rule_data.get("pattern", ".*"),
                    severity=SeverityType(rule_data.get("severity", "error")),
                    description=rule_data.get("description", ""),
                    inverse=rule_data.get("inverse", False)
                )
                
        return instance