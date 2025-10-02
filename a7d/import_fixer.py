#!/usr/bin/env python3
"""
Enhanced Import Fixer Tool

A more robust tool specifically designed to fix import issues in Python projects,
with special handling for the hands_scaphoid project structure.
"""

#%% [Standard library imports]
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional
import re

#%% [Third party imports]
import rich_click as click

PathLike = Union[str, Path]

class EnhancedImportFixer:
    """Enhanced import fixer with project-aware logic."""
    
    def __init__(self):
        self.project_structure = self._analyze_project_structure()
    
    def _analyze_project_structure(self) -> Dict[str, List[Path]]:
        """Analyze the project structure to understand module locations."""
        structure = {}
        
        # Find project root
        cwd = Path.cwd()
        project_root = cwd
        
        for parent in cwd.parents:
            if any((parent / indicator).exists() for indicator in [
                'pyproject.toml', 'setup.py', '.git'
            ]):
                project_root = parent
                break
        
        # Scan for Python modules
        if (project_root / 'src').exists():
            src_path = project_root / 'src'
            for py_file in src_path.rglob('*.py'):
                if py_file.name != '__init__.py':
                    module_name = py_file.stem
                    if module_name not in structure:
                        structure[module_name] = []
                    structure[module_name].append(py_file)
            
            # Also scan for directories with __init__.py
            for init_file in src_path.rglob('__init__.py'):
                module_name = init_file.parent.name
                if module_name not in structure:
                    structure[module_name] = []
                structure[module_name].append(init_file.parent)
        
        return structure
    
    def calculate_relative_import(self, module_name: str, current_file: Path) -> Optional[str]:
        """Calculate the correct relative import path."""
        if module_name.startswith('.'):
            return module_name  # Already relative
        
        current_path = current_file.resolve()
        
        # Special handling for hands_scaphoid project
        if 'hands_scaphoid' in str(current_path) or module_name in ['base', '__base__', 'core_commands', 'objects', 'commands', 'contexts']:
            return self._hands_scaphoid_relative_import(module_name, current_path)
        
        # Generic approach using project structure analysis
        if module_name in self.project_structure:
            for module_path in self.project_structure[module_name]:
                try:
                    relative_path = module_path.relative_to(current_path.parent)
                    parts = relative_path.parts
                    
                    if not parts:
                        return f".{module_name}"
                    
                    dots = '.' * (parts.count('..') + 1)
                    remaining = [p for p in parts if p != '..']
                    
                    if remaining and remaining[-1] == f"{module_name}.py":
                        remaining = remaining[:-1]
                    
                    if remaining:
                        return f"{dots}{'.'.join(remaining)}.{module_name}"
                    else:
                        return f"{dots}{module_name}"
                        
                except ValueError:
                    continue
        
        return None
    
    def _hands_scaphoid_relative_import(self, module_name: str, current_path: Path) -> Optional[str]:
        """Handle hands_scaphoid specific import patterns."""
        
        # Base mappings for the hands_scaphoid project
        base_mappings = {
            'base': '..base',
            '__base__': '..__base__',
            'objects': '..objects',
            'commands': '..commands', 
            'contexts': '..contexts',
        }
        
        # If we're in the commands directory
        if 'commands' in current_path.parts:
            command_mappings = {
                'core_commands': '.core_commands',
                'directory_commands': '.directory_commands',
                'archive_commands': '.archive_commands', 
                'file_commands': '.file_commands',
                'archive_handlers': '.archive_handlers',
            }
            if module_name in command_mappings:
                return command_mappings[module_name]
        
        # If we're in the contexts directory
        if 'contexts' in current_path.parts:
            context_mappings = {
                'DirectoryContext': '.DirectoryContext',
                'FileContext': '.FileContext', 
                'ArchiveContext': '.ArchiveContext',
                'ContextCore': '.ContextCore',
            }
            if module_name in context_mappings:
                return context_mappings[module_name]
        
        # If we're in the objects directory
        if 'objects' in current_path.parts:
            object_mappings = {
                'FileObject': '.FileObject',
                'DirectoryObject': '.DirectoryObject',
                'ArchiveCore': '.ArchiveCore',
                'ObjectItem': '.ObjectItem',
            }
            if module_name in object_mappings:
                return object_mappings[module_name]
        
        # General mappings
        if module_name in base_mappings:
            return base_mappings[module_name]
        
        return None

@click.command()
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True))
@click.option('--dry-run', is_flag=True, help='Show what would be changed')
@click.option('--verbose', '-v', is_flag=True, help='Show detailed output')
def main(files, dry_run, verbose):
    """
    Enhanced Import Fixer Tool
    
    Fix relative imports in Python files based on project structure.
    Specifically designed for the hands_scaphoid project but works generically.
    """
    fixer = EnhancedImportFixer()
    
    for file_path in files:
        file_path = Path(file_path)
        
        if verbose:
            click.secho(f"Processing {file_path}...", fg='blue')
        
        # Read the file
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse and fix imports
        try:
            tree = ast.parse(content)
            changes = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module:
                    if not node.module.startswith('.'):
                        relative_import = fixer.calculate_relative_import(node.module, file_path)
                        if relative_import and relative_import != node.module:
                            changes.append((node.lineno, node.module, relative_import))
            
            if changes:
                if dry_run:
                    click.secho(f"\nChanges for {file_path}:", fg='yellow', bold=True)
                    for line_no, old_import, new_import in changes:
                        click.secho(f"  Line {line_no}: ", nl=False)
                        click.secho(f"from {old_import}", fg='red', nl=False)
                        click.secho(" → ", nl=False)
                        click.secho(f"from {new_import}", fg='green')
                else:
                    # Apply changes
                    lines = content.split('\n')
                    for line_no, old_import, new_import in changes:
                        line_idx = line_no - 1
                        if line_idx < len(lines):
                            lines[line_idx] = lines[line_idx].replace(f"from {old_import}", f"from {new_import}")
                    
                    # Write back
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write('\n'.join(lines))
                    
                    if verbose:
                        click.secho(f"  ✓ Fixed {len(changes)} imports", fg='green')
            else:
                if verbose:
                    click.secho(f"  No changes needed", fg='dim')
                    
        except SyntaxError as e:
            click.secho(f"  ❌ Syntax error in {file_path}: {e}", fg='red')

if __name__ == '__main__':
    main()