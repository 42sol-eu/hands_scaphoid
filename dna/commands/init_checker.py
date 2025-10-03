"""
__init__.py checker utility for analyzing import consistency.

This module provides functionality to check imports in __init__.py files
against __all__ declarations and identify inconsistencies.
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Set, Union


def check_init_imports(init_file: Union[str, Path]) -> Dict[str, List[str]]:
    """
    Check imports in an __init__.py file against __all__ declarations.
    
    Args:
        init_file: Path to the __init__.py file to analyze
        
    Returns:
        Dictionary containing:
        - missing_in_all: Imports not included in __all__
        - missing_imports: Items in __all__ that are not imported
        - unused_imports: Imports that appear unused
        - all_items: Items found in __all__
        - imports: All imports found
    """
    init_file = Path(init_file)
    
    if not init_file.exists():
        raise FileNotFoundError(f"File not found: {init_file}")
    
    try:
        with open(init_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except UnicodeDecodeError:
        raise ValueError(f"Could not read file {init_file} - encoding issue")
    
    # Parse the AST
    try:
        tree = ast.parse(content, filename=str(init_file))
    except SyntaxError as e:
        raise ValueError(f"Syntax error in {init_file}: {e}")
    
    # Extract imports and __all__
    imports = _extract_imports(tree)
    all_items = _extract_all_items(tree)
    
    # Find inconsistencies
    imported_names = set(imports.keys())
    all_names = set(all_items)
    
    missing_in_all = list(imported_names - all_names)
    missing_imports = list(all_names - imported_names)
    
    # Check for unused imports (simple heuristic)
    unused_imports = _find_unused_imports(content, imports, all_items)
    
    return {
        'missing_in_all': sorted(missing_in_all),
        'missing_imports': sorted(missing_imports),
        'unused_imports': sorted(unused_imports),
        'all_items': sorted(all_items),
        'imports': dict(sorted(imports.items()))
    }


def _extract_imports(tree: ast.AST) -> Dict[str, Dict[str, Union[str, int]]]:
    """
    Extract all imports from an AST.
    
    Args:
        tree: AST tree to analyze
        
    Returns:
        Dictionary mapping import names to their details
    """
    imports = {}
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname or alias.name
                imports[name] = {
                    'type': 'import',
                    'module': alias.name,
                    'line': node.lineno,
                    'alias': alias.asname
                }
        
        elif isinstance(node, ast.ImportFrom):
            if node.module is None:
                continue  # Skip relative imports without module
                
            for alias in node.names:
                if alias.name == '*':
                    # Handle star imports
                    imports['*'] = {
                        'type': 'from_star',
                        'module': node.module,
                        'line': node.lineno,
                        'level': node.level
                    }
                else:
                    name = alias.asname or alias.name
                    imports[name] = {
                        'type': 'from',
                        'module': node.module,
                        'original_name': alias.name,
                        'line': node.lineno,
                        'alias': alias.asname,
                        'level': node.level
                    }
    
    return imports


def _extract_all_items(tree: ast.AST) -> List[str]:
    """
    Extract items from __all__ declarations.
    
    Args:
        tree: AST tree to analyze
        
    Returns:
        List of items declared in __all__
    """
    all_items = []
    
    for node in ast.walk(tree):
        if (isinstance(node, ast.Assign) and 
            len(node.targets) == 1 and 
            isinstance(node.targets[0], ast.Name) and 
            node.targets[0].id == '__all__'):
            
            if isinstance(node.value, ast.List):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Str):
                        all_items.append(elt.s)
                    elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        all_items.append(elt.value)
            
            elif isinstance(node.value, ast.Tuple):
                for elt in node.value.elts:
                    if isinstance(elt, ast.Str):
                        all_items.append(elt.s)
                    elif isinstance(elt, ast.Constant) and isinstance(elt.value, str):
                        all_items.append(elt.value)
    
    return all_items


def _find_unused_imports(content: str, imports: Dict[str, Dict], all_items: List[str]) -> List[str]:
    """
    Find potentially unused imports using simple text search.
    
    Args:
        content: File content as string
        imports: Dictionary of imports
        all_items: Items in __all__
        
    Returns:
        List of potentially unused import names
    """
    unused = []
    
    for name, import_info in imports.items():
        if name == '*':
            continue  # Skip star imports
        
        if name in all_items:
            continue  # Exported in __all__, so it's used
        
        # Simple heuristic: search for the name in the content
        # This is not perfect but gives a good indication
        lines = content.split('\n')
        import_line = import_info['line'] - 1
        
        # Remove the import line itself from the search
        search_content = '\n'.join(lines[:import_line] + lines[import_line + 1:])
        
        # Look for usage patterns
        patterns = [
            rf'\b{re.escape(name)}\b',  # Direct usage
            rf'{re.escape(name)}\.',    # Method/attribute access
            rf'\.{re.escape(name)}\b',  # As an attribute
        ]
        
        found_usage = False
        for pattern in patterns:
            if re.search(pattern, search_content):
                found_usage = True
                break
        
        if not found_usage:
            unused.append(name)
    
    return unused


def suggest_fixes(results: Dict[str, List[str]]) -> List[str]:
    """
    Suggest fixes for import/export inconsistencies.
    
    Args:
        results: Results from check_init_imports
        
    Returns:
        List of suggested fixes
    """
    suggestions = []
    
    if results['missing_in_all']:
        suggestions.append(
            f"Add to __all__: {', '.join(repr(name) for name in results['missing_in_all'])}"
        )
    
    if results['missing_imports']:
        suggestions.append(
            f"Add imports for: {', '.join(results['missing_imports'])}"
        )
    
    if results['unused_imports']:
        suggestions.append(
            f"Consider removing unused imports: {', '.join(results['unused_imports'])}"
        )
    
    return suggestions


def generate_corrected_all(results: Dict[str, List[str]]) -> str:
    """
    Generate a corrected __all__ declaration.
    
    Args:
        results: Results from check_init_imports
        
    Returns:
        String representation of corrected __all__
    """
    all_imports = set(results['imports'].keys()) - {'*'}  # Exclude star imports
    all_exports = set(results['all_items'])
    
    # Combine imported names and existing __all__ items
    corrected_all = sorted(all_imports | all_exports)
    
    # Format as Python list
    if len(corrected_all) <= 3:
        return f"__all__ = {corrected_all!r}"
    else:
        items = ',\n    '.join(repr(item) for item in corrected_all)
        return f"__all__ = [\n    {items}\n]"