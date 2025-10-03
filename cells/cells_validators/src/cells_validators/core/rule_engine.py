"""
Core rule engine for bones_validator.
"""

from collections import defaultdict, deque
from ..__base__ import Any, Dict, List, Optional, Set, Tuple, logger
from ..types.rule_types import ExecutionStrategy, EngineConfig, SeverityType
from ..rules.base_rule import BaseRule, ValidationViolation
from ..conditions.base_condition import EvaluationContext
from ..conditions.value_conditions import ValueCondition, ContextCondition
from ..conditions.logical_conditions import LogicalCondition

class ValidationResult:
    """
    Result of a validation operation.
    
    Contains information about rule execution, violations found,
    and performance metrics.
    """
    
    def __init__(
        self,
        value: Any,
        is_valid: bool,
        violations: List[ValidationViolation],
        executed_rules: List[str],
        skipped_rules: List[str],
        execution_time: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ):
        self.value = value
        self.is_valid = is_valid
        self.violations = violations
        self.executed_rules = executed_rules
        self.skipped_rules = skipped_rules
        self.execution_time = execution_time
        self.metadata = metadata or {}
    
    @property
    def error_count(self) -> int:
        """Count of error-level violations."""
        return sum(1 for v in self.violations if v.severity == SeverityType.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of warning-level violations."""
        return sum(1 for v in self.violations if v.severity == SeverityType.WARNING)
    
    @property
    def info_count(self) -> int:
        """Count of info-level violations."""
        return sum(1 for v in self.violations if v.severity == SeverityType.INFO)
    
    def get_violations_by_severity(self, severity) -> List[ValidationViolation]:
        """Get violations of a specific severity level."""
        return [v for v in self.violations if v.severity == severity]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert result to dictionary."""
        return {
            'value': self.value,
            'is_valid': self.is_valid,
            'violations': [
                {
                    'rule_name': v.rule_name,
                    'severity': v.severity.value,
                    'message': v.message,
                    'value': v.value
                }
                for v in self.violations
            ],
            'executed_rules': self.executed_rules,
            'skipped_rules': self.skipped_rules,
            'execution_time': self.execution_time,
            'error_count': self.error_count,
            'warning_count': self.warning_count,
            'info_count': self.info_count,
            'metadata': self.metadata
        }
    
    def __str__(self) -> str:
        """String representation of validation result."""
        status = "valid" if self.is_valid else "invalid"
        return f"ValidationResult({status}, {len(self.violations)} violations)"

class RuleEngine:
    """
    Core rule engine for validation.
    
    Manages rules, conditions, and execution strategies.
    Supports rule networking through conditions and dependencies.
    """
    
    def __init__(self, config: Optional[EngineConfig] = None):
        self.config = config or EngineConfig()
        self.rules: Dict[str, BaseRule] = {}
        self.rule_groups: Dict[str, List[str]] = {}
        self.execution_order: List[str] = []
        self._cache: Dict[str, ValidationResult] = {}
        self._stats = {
            'total_validations': 0,
            'cache_hits': 0,
            'rule_executions': 0,
            'condition_evaluations': 0
        }
    
    def add_rule(self, rule: BaseRule) -> None:
        """Add a rule to the engine."""
        if rule.name in self.rules:
            logger.warning(f"Rule '{rule.name}' already exists, replacing")
        
        self.rules[rule.name] = rule
        self._update_execution_order()
        logger.debug(f"Added rule '{rule.name}' to engine")
    
    def remove_rule(self, rule_name: str) -> bool:
        """Remove a rule from the engine."""
        if rule_name not in self.rules:
            return False
        
        # Remove from dependencies
        rule = self.rules[rule_name]
        for dep_name in rule.dependencies:
            if dep_name in self.rules:
                self.rules[dep_name].dependents.remove(rule_name)
        
        for dep_name in rule.dependents:
            if dep_name in self.rules:
                self.rules[dep_name].dependencies.remove(rule_name)
        
        del self.rules[rule_name]
        self._update_execution_order()
        logger.debug(f"Removed rule '{rule_name}' from engine")
        return True
    
    def get_rule(self, rule_name: str) -> Optional[BaseRule]:
        """Get a rule by name."""
        return self.rules.get(rule_name)
    
    def add_rule_dependency(self, rule_name: str, dependency_name: str) -> bool:
        """Add a dependency relationship between rules."""
        if rule_name not in self.rules or dependency_name not in self.rules:
            return False
        
        rule = self.rules[rule_name]
        dependency = self.rules[dependency_name]
        
        if dependency_name not in rule.dependencies:
            rule.dependencies.append(dependency_name)
        
        if rule_name not in dependency.dependents:
            dependency.dependents.append(rule_name)
        
        self._update_execution_order()
        return True
    
    def add_conditional_rules(
        self,
        condition: Any,  # Can be BaseCondition or simple parameters
        rules: List[BaseRule],
        group_name: Optional[str] = None
    ) -> None:
        """
        Add a group of rules that are activated by a condition.
        
        This is the key method for rule networking - rules are only
        executed when their activation condition is met.
        """
        # Convert simple condition parameters to ValueCondition
        if isinstance(condition, tuple) and len(condition) >= 2:
            operator, value = condition[0], condition[1]
            condition = ValueCondition(operator, value)
        elif isinstance(condition, str):
            # Assume starts_with condition
            from ..types.rule_types import ConditionOperator
            condition = ValueCondition(ConditionOperator.STARTS_WITH, condition)
        
        # Add condition to all rules
        for rule in rules:
            rule.add_activation_condition(condition)
            self.add_rule(rule)
        
        # Optionally group the rules
        if group_name:
            self.rule_groups[group_name] = [rule.name for rule in rules]
    
    def validate(
        self,
        value: Any,
        context: Optional[EvaluationContext] = None,
        rule_names: Optional[List[str]] = None
    ) -> ValidationResult:
        """
        Validate a value against rules.
        
        Args:
            value: Value to validate
            context: Optional evaluation context
            rule_names: Optional list of specific rules to execute
            
        Returns:
            ValidationResult with validation details
        """
        import time
        start_time = time.time()
        
        self._stats['total_validations'] += 1
        
        # Check cache if enabled
        cache_key = f"{value}_{rule_names}"
        if self.config.enable_caching and cache_key in self._cache:
            self._stats['cache_hits'] += 1
            return self._cache[cache_key]
        
        # Create context if not provided
        if context is None:
            context = EvaluationContext(value)
        
        # Determine which rules to execute
        rules_to_execute = self._get_rules_to_execute(rule_names, context)
        
        # Execute rules
        violations = []
        executed_rules = []
        skipped_rules = []
        
        for rule_name in rules_to_execute:
            rule = self.rules[rule_name]
            
            # Check if rule is active
            if not rule.is_active(context.to_dict()):
                skipped_rules.append(rule_name)
                continue
            
            # Execute rule
            try:
                violation = rule.validate(value, context)
                if violation:
                    violations.append(violation)
                    
                    # Fail fast strategy
                    if (self.config.execution_strategy == ExecutionStrategy.FAIL_FAST and 
                        violation.severity.is_error):
                        break
                
                executed_rules.append(rule_name)
                self._stats['rule_executions'] += 1
                
            except Exception as e:
                logger.error(f"Error executing rule '{rule_name}': {e}")
                # Continue with other rules
        
        # Determine validity (no error-level violations)
        is_valid = not any(v.severity.is_error for v in violations)
        
        # Create result
        execution_time = time.time() - start_time
        result = ValidationResult(
            value=value,
            is_valid=is_valid,
            violations=violations,
            executed_rules=executed_rules,
            skipped_rules=skipped_rules,
            execution_time=execution_time
        )
        
        # Cache result if enabled
        if self.config.enable_caching:
            self._cache[cache_key] = result
        
        return result
    
    def _get_rules_to_execute(
        self,
        rule_names: Optional[List[str]],
        context: EvaluationContext
    ) -> List[str]:
        """Determine which rules should be executed."""
        if rule_names:
            # Execute specific rules
            return [name for name in rule_names if name in self.rules]
        
        # Execute all rules in dependency order
        return self.execution_order
    
    def _update_execution_order(self) -> None:
        """Update rule execution order based on dependencies."""
        # Topological sort to handle dependencies
        in_degree = defaultdict(int)
        graph = defaultdict(list)
        
        # Build dependency graph
        for rule_name, rule in self.rules.items():
            for dep_name in rule.dependencies:
                if dep_name in self.rules:
                    graph[dep_name].append(rule_name)
                    in_degree[rule_name] += 1
                else:
                    logger.warning(f"Rule '{rule_name}' depends on non-existent rule '{dep_name}'")
        
        # Ensure all rules are in in_degree
        for rule_name in self.rules:
            if rule_name not in in_degree:
                in_degree[rule_name] = 0
        
        # Kahn's algorithm for topological sorting
        queue = deque([name for name, degree in in_degree.items() if degree == 0])
        execution_order = []
        
        while queue:
            current = queue.popleft()
            execution_order.append(current)
            
            for neighbor in graph[current]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)
        
        # Check for cycles
        if len(execution_order) != len(self.rules):
            logger.warning("Circular dependency detected in rules")
            # Fallback to simple ordering
            execution_order = list(self.rules.keys())
        
        self.execution_order = execution_order
    
    def clear_cache(self) -> None:
        """Clear the validation result cache."""
        self._cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get engine statistics."""
        rule_stats = {name: rule.get_stats() for name, rule in self.rules.items()}
        
        return {
            'engine_stats': self._stats.copy(),
            'rule_count': len(self.rules),
            'group_count': len(self.rule_groups),
            'cache_size': len(self._cache),
            'execution_order': self.execution_order,
            'rule_stats': rule_stats
        }
    
    def reset_stats(self) -> None:
        """Reset all statistics."""
        self._stats = {
            'total_validations': 0,
            'cache_hits': 0,
            'rule_executions': 0,
            'condition_evaluations': 0
        }
        
        for rule in self.rules.values():
            rule.reset_stats()
    
    def __str__(self) -> str:
        """String representation of the engine."""
        return f"RuleEngine({len(self.rules)} rules, {len(self.rule_groups)} groups)"