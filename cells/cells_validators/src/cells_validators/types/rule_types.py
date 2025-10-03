"""
Rule types and enums for bones_validator.
"""

from ..__base__ import Enum, BaseModel, Field, Optional, List, Dict, Any

class SeverityType(str, Enum):
    """Severity levels for validation violations."""
    ERROR = "error"
    WARNING = "warning" 
    INFO = "info"

    @property
    def is_error(self) -> bool:
        """Check if this severity represents an error."""
        return self == SeverityType.ERROR
        
    @property
    def is_warning(self) -> bool:
        """Check if this severity represents a warning."""
        return self == SeverityType.WARNING
        
    @property
    def is_info(self) -> bool:
        """Check if this severity represents info."""
        return self == SeverityType.INFO

class RuleType(str, Enum):
    """Types of validation rules."""
    BASIC = "basic"
    CONDITIONAL = "conditional"
    CHAIN = "chain"
    GROUP = "group"

class ConditionType(str, Enum):
    """Types of rule conditions."""
    VALUE = "value"
    LOGICAL = "logical"
    CONTEXT = "context"
    CUSTOM = "custom"

class ConditionOperator(str, Enum):
    """Operators for condition evaluation."""
    # Value conditions
    EQUALS = "equals"
    NOT_EQUALS = "not_equals"
    STARTS_WITH = "starts_with"
    ENDS_WITH = "ends_with"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    MATCHES = "matches"
    NOT_MATCHES = "not_matches"
    LENGTH_GT = "length_gt"
    LENGTH_LT = "length_lt"
    LENGTH_EQ = "length_eq"
    
    # Logical conditions
    AND = "and"
    OR = "or"
    NOT = "not"
    XOR = "xor"
    
    # Context conditions
    HAS_ATTRIBUTE = "has_attribute"
    ATTRIBUTE_EQUALS = "attribute_equals"
    IS_TYPE = "is_type"

class ConnectorType(str, Enum):
    """Types of rule connectors."""
    DEPENDENCY = "dependency"
    CONDITION = "condition"
    SEQUENCE = "sequence"
    PARALLEL = "parallel"

class ExecutionStrategy(str, Enum):
    """Rule execution strategies."""
    FAIL_FAST = "fail_fast"
    COLLECT_ALL = "collect_all"
    CONDITIONAL = "conditional"
    OPTIMIZED = "optimized"

# Pydantic models for configuration

class RuleConfig(BaseModel):
    """Configuration for a validation rule."""
    name: str = Field(..., description="Unique rule identifier")
    pattern: str = Field(..., description="Validation pattern or function name")
    severity: SeverityType = Field(default=SeverityType.ERROR, description="Violation severity")
    description: str = Field(default="", description="Human-readable description")
    inverse: bool = Field(default=False, description="Invert the rule logic")
    enabled: bool = Field(default=True, description="Whether rule is active")
    tags: List[str] = Field(default_factory=list, description="Rule tags for organization")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional rule metadata")

class ConditionConfig(BaseModel):
    """Configuration for a rule condition."""
    type: ConditionType = Field(..., description="Type of condition")
    operator: ConditionOperator = Field(..., description="Condition operator")
    value: Any = Field(None, description="Comparison value")
    attribute: Optional[str] = Field(None, description="Attribute name for context conditions")
    conditions: Optional[List['ConditionConfig']] = Field(None, description="Sub-conditions for logical operations")

    class Config:
        # Allow forward references for recursive structure
        arbitrary_types_allowed = True

class ConnectorConfig(BaseModel):
    """Configuration for rule connectors."""
    type: ConnectorType = Field(..., description="Type of connector")
    source_rules: List[str] = Field(..., description="Source rule names")
    target_rules: List[str] = Field(..., description="Target rule names")
    condition: Optional[ConditionConfig] = Field(None, description="Activation condition")
    priority: int = Field(default=0, description="Execution priority")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional connector metadata")

class EngineConfig(BaseModel):
    """Configuration for the rule engine."""
    execution_strategy: ExecutionStrategy = Field(default=ExecutionStrategy.FAIL_FAST, description="How to execute rules")
    max_depth: int = Field(default=10, description="Maximum recursion depth for rule chains")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    enable_optimization: bool = Field(default=True, description="Enable execution optimization")
    parallel_execution: bool = Field(default=False, description="Enable parallel rule execution")
    timeout_seconds: Optional[float] = Field(None, description="Maximum execution time")

# Update forward references
ConditionConfig.model_rebuild()