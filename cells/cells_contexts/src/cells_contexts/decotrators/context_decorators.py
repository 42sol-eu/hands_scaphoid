# -*- coding: utf-8 -*-
"""
Decorator utilities for creating context-aware functions.
---yaml
File:
    name:       context_decorators.py
    uuid:       5cdc2141-5203-4414-96eb-10a2dfae136f
    date:       2025-10-03

Description:    Decorator utilities for creating context-aware functions.

Project:
    name:       cells_contexts
    uuid:       6a9002e9-d271-4569-a9f8-739355829f14
    url:        https://github.com/42sol-eu/cells_contexts

Authors: ["Andreas Häberle"]
"""


# [Standard library imports]
from contextvars import ContextVar
from functools import wraps
from typing import Callable, TypeVar, Type, Optional

# [Local imports]
# - none 

# [Third party imports]
# - none 

# [Context Variables]
_T = TypeVar('T')

# [Functions]

def context_function_with_check(context_var: ContextVar[Optional[_T]], 
                    expected_type: Type[_T] = None,
                    context_name: str = None) -> Callable:
    """
    Decorator factory to create context-aware functions that delegate to instance methods.
    Ensures the function is called within the correct context and optionally checks type.

    Args:
        context_var: The ContextVar to get the current instance from.
        expected_type: Optional type to check the context instance against.
        context_name: Name of the context for error messages (auto-derived if None).

    Returns:
        Decorator function that wraps the target function.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator that wraps the function to enforce context and type checks.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper that checks for the correct context and delegates to the instance method.
            """
            current_instance = context_var.get()
            if not current_instance:
                ctx_name = context_name or (expected_type.__name__ if expected_type else "context")
                raise RuntimeError(f"{func.__name__}() must be called within a {ctx_name} context manager")
            if expected_type and not isinstance(current_instance, expected_type):
                ctx_name = context_name or expected_type.__name__
                raise TypeError(f"{func.__name__}() can only be used within a {ctx_name} context")
            method_name = func.__name__
            if not hasattr(current_instance, method_name):
                raise AttributeError(f"{type(current_instance).__name__} has no method '{method_name}'")
            method = getattr(current_instance, method_name)
            return method(*args, **kwargs)
        return wrapper
    return decorator

# Alternative simpler decorator for single-type contexts
def context_function(context_var: ContextVar) -> Callable:
    """
    Simple decorator factory for context functions without type checking.
    Ensures the function is called within the correct context.

    Args:
        context_var: The ContextVar to get the current instance from.

    Returns:
        Decorator function that wraps the target function.
    """
    def decorator(func: Callable) -> Callable:
        """
        Decorator that wraps the function to enforce context presence.
        """
        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper that checks for the correct context and delegates to the instance method.
            """
            current_instance = context_var.get()
            if not current_instance:
                raise RuntimeError(f"{func.__name__}() must be called within a context manager")
            method = getattr(current_instance, func.__name__)
            return method(*args, **kwargs)
        return wrapper
    return decorator


def auto_context_function_with_checks(  context_var: ContextVar[Optional[_T]], 
                                        expected_type: Type[_T],
                                        context_name: str,
                                        methods: Optional[list[str]] = None
    ) -> dict[str, Callable]:
    """
    Utility to automatically create multiple context-aware functions for specified methods.
    
    Args:
        context_var: The ContextVar to get the current instance from.
        expected_type: Type to check the context instance against.
        context_name: Name of the context for error messages.
        methods: List of method names to create functions for. If None or empty, returns empty dict.
        
    Returns:
        Dictionary mapping method names to their context-aware function wrappers.
    """
    if not methods:
        return {}
    
    functions = {}
    
    for method_name in methods:
        def create_function(name: str):
            def context_function_wrapper(*args, **kwargs):
                current_instance = context_var.get()
                if not current_instance:
                    raise RuntimeError(f"{name}() must be called within a {context_name} context manager")
                if not isinstance(current_instance, expected_type):
                    raise TypeError(f"{name}() can only be used within a {context_name} context")
                if not hasattr(current_instance, name):
                    raise AttributeError(f"{type(current_instance).__name__} has no method '{name}'")
                method = getattr(current_instance, name)
                return method(*args, **kwargs)
            return context_function_wrapper
        
        functions[method_name] = create_function(method_name)
    
    return functions