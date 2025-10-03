"""
Class finder utility for analyzing Python files.

This module provides functionality to find and extract class definitions
from Python files and directory structures.
"""

import ast
from pathlib import Path
from typing import List, Dict, Union


def find_classes(path: Union[str, Path], recursive: bool = False) -> List[Dict[str, Union[str, int]]]:
    """
    Find all class definitions in a file or directory.
    
    Args:
        path: Path to a file or directory to search
        recursive: Whether to search subdirectories recursively
        
    Returns:
        List of dictionaries containing class information:
        - class_name: Name of the class
        - file: Path to the file containing the class
        - line: Line number where the class is defined
        - docstring: Class docstring (if available)
    """
    path = Path(path)
    results = []
    
    if path.is_file():
        if path.suffix == '.py':
            results.extend(_find_classes_in_file(path))
    elif path.is_dir():
        if recursive:
            pattern = '**/*.py'
        else:
            pattern = '*.py'
        
        for py_file in path.glob(pattern):
            results.extend(_find_classes_in_file(py_file))
    
    return results


def _find_classes_in_file(file_path: Path) -> List[Dict[str, Union[str, int]]]:
    """
    Find all class definitions in a single Python file.
    
    Args:
        file_path: Path to the Python file
        
    Returns:
        List of class information dictionaries
    """
    results = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_info = {
                    'class_name': node.name,
                    'file': file_path,
                    'line': node.lineno,
                    'docstring': ast.get_docstring(node) or ''
                }
                
                # Get base classes if any
                bases = []
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        bases.append(base.id)
                    elif isinstance(base, ast.Attribute):
                        bases.append(_get_full_name(base))
                
                class_info['bases'] = bases
                results.append(class_info)
                
    except (SyntaxError, UnicodeDecodeError) as e:
        # Skip files with syntax errors or encoding issues
        pass
    
    return results


def _get_full_name(node: ast.AST) -> str:
    """
    Get the full name of an attribute node (e.g., 'module.Class').
    
    Args:
        node: AST node to extract name from
        
    Returns:
        Full name as a string
    """
    if isinstance(node, ast.Name):
        return node.id
    elif isinstance(node, ast.Attribute):
        return f"{_get_full_name(node.value)}.{node.attr}"
    else:
        return str(node)


def get_class_methods(file_path: Union[str, Path], class_name: str) -> List[Dict[str, Union[str, int]]]:
    """
    Get all methods of a specific class in a file.
    
    Args:
        file_path: Path to the Python file
        class_name: Name of the class to analyze
        
    Returns:
        List of method information dictionaries
    """
    file_path = Path(file_path)
    methods = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content, filename=str(file_path))
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                for item in node.body:
                    if isinstance(item, ast.FunctionDef):
                        method_info = {
                            'method_name': item.name,
                            'line': item.lineno,
                            'is_private': item.name.startswith('_'),
                            'is_dunder': item.name.startswith('__') and item.name.endswith('__'),
                            'docstring': ast.get_docstring(item) or '',
                            'args': [arg.arg for arg in item.args.args]
                        }
                        methods.append(method_info)
                break
                
    except (SyntaxError, UnicodeDecodeError):
        pass
    
    return methods