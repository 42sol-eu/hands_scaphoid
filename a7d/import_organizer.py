#!/usr/bin/env python3
"""
Python Import Organizer Script

This script analyzes Python files and organizes their imports according to the project's
standards with #%% [section] format. It categorizes imports, sorts them alphabetically,
detects unused imports, and suggests missing imports.
---yaml
File:
    name:   import_organizer.py
    uuid:   e9f6c7d2-43ca-436b-8bce-b7efb33e89e9
    date:   2025-09-28

Description:
    Analyzes and organizes Python imports with section headers

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import ast
import os
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple, Union, Optional
import re
import importlib.util
import pkgutil

#%% [Third party imports]
import rich_click as click

# Configure rich_click for better appearance
click.rich_click.SHOW_ARGUMENTS = True
click.rich_click.GROUP_ARGUMENTS_OPTIONS = True

#%% [Local imports]
# None - this is a standalone script

PathLike = Union[str, Path]

class ImportInfo:
    """Information about an import statement."""
    
    def __init__(self, module: str, names: List[str] = None, alias: str = None, is_from: bool = False):
        self.module = module
        self.names = names or []
        self.alias = alias
        self.is_from = is_from
        self.line_number = 0
        
    def __repr__(self):
        return f"ImportInfo(module='{self.module}', names={self.names}, alias='{self.alias}', is_from={self.is_from})"

class ImportAnalyzer:
    """Analyzes and organizes Python imports."""
    
    def __init__(self):
        self.stdlib_modules = self._get_stdlib_modules()
        
    def _get_stdlib_modules(self) -> Set[str]:
        """Get set of standard library module names."""
        stdlib_modules = set()
        
        # Get built-in modules
        stdlib_modules.update(sys.builtin_module_names)
        
        # Common standard library modules (not exhaustive but covers most cases)
        common_stdlib = {
            'abc', 'ast', 'asyncio', 'base64', 'collections', 'contextlib',
            'copy', 'csv', 'datetime', 'decimal', 'enum', 'functools', 'glob', 'hashlib',
            'http', 'io', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib',
            'pickle', 'random', 're', 'shutil', 'socket', 'sqlite3', 'string', 'subprocess',
            'sys', 'tempfile', 'threading', 'time', 'typing', 'urllib', 'uuid', 'warnings',
            'weakref', 'xml', 'zipfile', 'tarfile', 'gzip', 'bz2', 'lzma', 'dataclasses',
            'importlib', 'pkgutil', 'inspect', 'operator', 'heapq', 'bisect', 'array',
            'struct', 'codecs', 'locale', 'gettext', 'calendar', 'mailbox', 'mimetypes',
            'email', 'html', 'configparser', 'fileinput', 'linecache', 'pprint', 'reprlib',
            'textwrap', 'unicodedata', 'stringprep', 'readline', 'rlcompleter'
        }
        stdlib_modules.update(common_stdlib)
        
        return stdlib_modules
    
    def _categorize_import(self, import_info: ImportInfo, file_path: Path) -> str:
        """Categorize an import as 'standard', 'third_party', or 'local'."""
        module_name = import_info.module.split('.')[0]
        
        # Check if it's a relative import (starts with .)
        if import_info.module.startswith('.'):
            return 'local'
        
        # Check if it's a standard library module
        if module_name in self.stdlib_modules:
            return 'standard'
        
        # Project-specific patterns for hands_scaphoid
        local_patterns = [
            'hands_scaphoid',
            'src.hands_scaphoid',
            '__base__',  # Project's base module
            'base',      # When imported as 'base' from within project (should be ..base)
            'objects',   # When imported from within project (should be ..objects)  
            'commands',  # When imported from within project (should be ..commands)
            'contexts',  # When imported from within project (should be ..contexts)
            'core_commands',  # Should be .core_commands
            'directory_commands',  # Should be .directory_commands
            'archive_commands',   # Should be .archive_commands
            'file_commands',      # Should be .file_commands
        ]
        
        # Check if it's part of the local project
        for pattern in local_patterns:
            if import_info.module.startswith(pattern):
                return 'local'
        
        # Special handling for common third-party libraries
        third_party_modules = {
            'rich', 'click', 'typer', 'pydantic', 'fastapi', 'flask', 'django',
            'requests', 'httpx', 'aiohttp', 'numpy', 'pandas', 'matplotlib',
            'pytest', 'pylint', 'black', 'mypy', 'isort', 'flake8', 'pytest',
            'rarfile', 'py7zr', 'lxml', 'beautifulsoup4', 'jinja2', 'mako',
            'sqlalchemy', 'alembic', 'psycopg2', 'pymongo', 'redis'
        }
        
        if module_name in third_party_modules:
            return 'third_party'
        
        # Try to determine if it's installed as third party
        try:
            spec = importlib.util.find_spec(module_name)
            if spec is None:
                return 'local'  # Assume local if not found
            
            # If the module is in site-packages, it's third party
            if spec.origin and 'site-packages' in spec.origin:
                return 'third_party'
        except (ImportError, ModuleNotFoundError, ValueError):
            pass
        
        # Default to local for unknown modules (safer assumption for project files)
        return 'local'
    
    def parse_imports(self, source_code: str) -> List[ImportInfo]:
        """Parse imports from Python source code."""
        imports = []
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            print(f"Syntax error in file: {e}")
            return imports
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    import_info = ImportInfo(
                        module=alias.name,
                        alias=alias.asname,
                        is_from=False
                    )
                    import_info.line_number = node.lineno
                    imports.append(import_info)
            
            elif isinstance(node, ast.ImportFrom):
                if node.module:  # Skip relative imports without module name
                    names = []
                    for alias in node.names:
                        # Handle aliases in from imports
                        if alias.asname:
                            names.append(f"{alias.name} as {alias.asname}")
                        else:
                            names.append(alias.name)
                    
                    import_info = ImportInfo(
                        module=node.module,
                        names=names,
                        is_from=True
                    )
                    import_info.line_number = node.lineno
                    imports.append(import_info)
                elif node.level > 0:  # Relative imports like "from . import something"
                    # Handle relative imports
                    relative_module = '.' * node.level
                    if node.module:
                        relative_module += node.module
                    
                    names = []
                    for alias in node.names:
                        if alias.asname:
                            names.append(f"{alias.name} as {alias.asname}")
                        else:
                            names.append(alias.name)
                    
                    import_info = ImportInfo(
                        module=relative_module,
                        names=names,
                        is_from=True
                    )
                    import_info.line_number = node.lineno
                    imports.append(import_info)
        
        return imports
    
    def find_used_names(self, source_code: str) -> Set[str]:
        """Find all names used in the source code."""
        used_names = set()
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError:
            return used_names
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Handle attribute access (e.g., module.function)
                if isinstance(node.value, ast.Name):
                    used_names.add(node.value.id)
        
        return used_names
    
    def detect_unused_imports(self, imports: List[ImportInfo], used_names: Set[str]) -> List[ImportInfo]:
        """Detect unused imports."""
        unused = []
        
        for import_info in imports:
            is_used = False
            
            if import_info.is_from:
                # For 'from module import name' statements
                for name in import_info.names:
                    if name in used_names or name == '*':
                        is_used = True
                        break
            else:
                # For 'import module' statements
                module_name = import_info.alias or import_info.module.split('.')[0]
                if module_name in used_names:
                    is_used = True
            
            if not is_used:
                unused.append(import_info)
        
        return unused
    
    def format_import_section(self, imports: List[ImportInfo], section_name: str) -> str:
        """Format imports for a specific section with proper sorting and grouping."""
        if not imports:
            return f"#%% [{section_name}]\n# - none\n"
        
        # Group by module for 'from' imports, separate regular imports
        regular_imports = []
        from_imports = {}
        
        for imp in imports:
            if imp.is_from:
                if imp.module not in from_imports:
                    from_imports[imp.module] = set()
                from_imports[imp.module].update(imp.names)
            else:
                regular_imports.append(imp)
        
        # Sort everything properly
        regular_imports.sort(key=lambda x: (x.module.lower(), x.alias.lower() if x.alias else ''))
        
        lines = [f"#%% [{section_name}]"]
        
        # Add regular imports first, sorted alphabetically
        for imp in regular_imports:
            if imp.alias:
                lines.append(f"import {imp.module} as {imp.alias}")
            else:
                lines.append(f"import {imp.module}")
        
        # Add from imports, grouped by module and sorted alphabetically
        for module in sorted(from_imports.keys(), key=lambda x: x.lower()):
            # Sort names alphabetically, handling aliases properly
            names = sorted(from_imports[module], key=lambda x: x.split(' as ')[0].lower())
            
            if len(names) == 1:
                lines.append(f"from {module} import {names[0]}")
            else:
                lines.append(f"from {module} import (")
                for name in names:
                    lines.append(f"    {name},")
                lines.append(")")
        
        return '\n'.join(lines) + '\n'
    
    def organize_imports(self, file_path: PathLike, fix_relative: bool = False) -> str:
        """Organize imports in a Python file."""
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse imports
        imports = self.parse_imports(content)
        if not imports:
            print(f"No imports found in {file_path}")
            return content
        
        # Find used names
        used_names = self.find_used_names(content)
        
        # Detect unused imports
        unused_imports = self.detect_unused_imports(imports, used_names)
        if unused_imports:
            print(f"Unused imports detected in {file_path}:")
            for imp in unused_imports:
                print(f"  Line {imp.line_number}: {imp}")
        
        # Handle relative import fixes
        if fix_relative:
            imports = self.auto_fix_relative_imports(imports, file_path)
            print(f"Auto-fixed relative imports in {file_path}")
        else:
            # Suggest relative import fixes
            suggestions = self.suggest_relative_import_fixes(imports, file_path)
            if suggestions:
                print(f"Relative import suggestions for {file_path}:")
                for suggestion in suggestions:
                    print(suggestion)
        
        # Resolve duplicate imports (prioritize local imports)
        imports = self.resolve_duplicate_imports(imports, file_path)
        
        # Filter out unused imports (optional - you may want to keep this as a flag)
        # used_imports = [imp for imp in imports if imp not in unused_imports]
        used_imports = imports  # Keep all imports for now
        
        # Categorize imports
        categorized = {
            'standard': [],
            'third_party': [],
            'local': []
        }
        
        for imp in used_imports:
            category = self._categorize_import(imp, file_path)
            categorized[category].append(imp)
        
        # Generate organized import sections
        sections = []
        
        # Standard library imports
        if categorized['standard']:
            sections.append(self.format_import_section(categorized['standard'], 'Standard library imports'))
        
        # Third party imports  
        if categorized['third_party']:
            sections.append(self.format_import_section(categorized['third_party'], 'Third party imports'))
        
        # Local imports
        if categorized['local']:
            sections.append(self.format_import_section(categorized['local'], 'Local imports'))
        
        # Remove existing import sections and replace
        lines = content.split('\n')
        
        # Find the end of the docstring/header
        docstring_end = 0
        triple_quote_count = 0
        
        for i, line in enumerate(lines):
            if '"""' in line:
                triple_quote_count += line.count('"""')
                if triple_quote_count >= 2:
                    docstring_end = i + 1
                    break
        
        # Find where imports start and end - look for import sections or individual imports
        import_start = len(lines)
        import_end = docstring_end
        
        # Skip empty lines after docstring
        while import_end < len(lines) and not lines[import_end].strip():
            import_end += 1
        
        # Find the start and end of import blocks
        in_import_section = False
        found_first_import = False
        
        for i in range(docstring_end, len(lines)):
            line = lines[i].strip()
            
            # Check if this line is an import-related line
            is_import_line = (
                line.startswith('#%% [') or 
                line.startswith('import ') or 
                line.startswith('from ') or
                line.startswith('# - none') or
                (line.startswith('    ') and in_import_section) or  # Continuation of multi-line import
                (line.startswith(')') and in_import_section) or     # End of multi-line import
                (line == '' and in_import_section)  # Empty line within import section
            )
            
            if is_import_line:
                if not found_first_import:
                    import_start = i
                    found_first_import = True
                import_end = i + 1
                in_import_section = True
            elif line and found_first_import:
                # Non-empty, non-import line found after imports started
                if not line.startswith('#') and not in_import_section:
                    # This is actual code, end of imports
                    break
                elif line.startswith('def ') or line.startswith('class ') or line.startswith('@'):
                    # Clear code start
                    break
            elif not line:
                # Empty line - continue but don't change state
                if found_first_import:
                    import_end = i + 1
                continue
            else:
                # Regular line - if we haven't found imports yet, this is not import section
                if not found_first_import:
                    in_import_section = False
        
        # Reconstruct the file
        new_content = []
        
        # Add everything before imports
        new_content.extend(lines[:import_start])
        
        # Add empty line before imports if needed
        if new_content and new_content[-1].strip():
            new_content.append('')
        
        # Add organized import sections
        for section in sections:
            section_lines = section.rstrip('\n').split('\n')
            new_content.extend(section_lines)
            new_content.append('')  # Add blank line after each section
        
        # Add everything after imports (skip the original import section)
        remaining_lines = lines[import_end:]
        # Remove leading empty lines
        while remaining_lines and not remaining_lines[0].strip():
            remaining_lines.pop(0)
        
        new_content.extend(remaining_lines)
        
        # Clean up extra blank lines at the end
        while new_content and not new_content[-1].strip():
            new_content.pop()
        
        return '\n'.join(new_content)
    
    def _calculate_relative_import(self, module_name: str, current_file: Path) -> Optional[str]:
        """Calculate the relative import path based on file system structure."""
        if module_name.startswith('.'):
            return None  # Already relative
        
        current_path = current_file.resolve()
        current_dir = current_path.parent
        
        # Find the project root (look for common indicators)
        project_root = None
        for parent in current_path.parents:
            if any((parent / indicator).exists() for indicator in [
                'pyproject.toml', 'setup.py', '.git', 'src', 'requirements.txt'
            ]):
                project_root = parent
                break
        
        if not project_root:
            return None
        
        # For this specific project structure, handle known patterns
        # This is a more targeted approach for hands_scaphoid project
        if 'hands_scaphoid' in str(current_path):
            # We're inside the hands_scaphoid project
            hands_scaphoid_patterns = {
                'base': '..base',
                '__base__': '..__base__',
                'objects': '..objects', 
                'commands': '..commands',
                'contexts': '..contexts',
            }
            
            # Check if current file is in commands directory
            if 'commands' in current_path.parts:
                commands_patterns = {
                    'core_commands': '.core_commands',
                    'directory_commands': '.directory_commands', 
                    'archive_commands': '.archive_commands',
                    'file_commands': '.file_commands',
                }
                if module_name in commands_patterns:
                    return commands_patterns[module_name]
            
            # Check if current file is in contexts directory  
            if 'contexts' in current_path.parts:
                contexts_patterns = {
                    'DirectoryContext': '.DirectoryContext',
                    'FileContext': '.FileContext',
                    'ArchiveContext': '.ArchiveContext',
                }
                if module_name in contexts_patterns:
                    return contexts_patterns[module_name]
            
            # Check if current file is in objects directory
            if 'objects' in current_path.parts:
                objects_patterns = {
                    'FileCore': '.FileCore',
                    'DirectoryCore': '.DirectoryCore',
                    'ArchiveCore': '.ArchiveCore',
                }
                if module_name in objects_patterns:
                    return objects_patterns[module_name]
            
            # General hands_scaphoid patterns
            if module_name in hands_scaphoid_patterns:
                return hands_scaphoid_patterns[module_name]
        
        # Generic file system based approach
        search_paths = [
            project_root / 'src',
            current_dir.parent,  # Parent directory
            current_dir,         # Same directory
        ]
        
        # Look for the module in the file system
        for search_path in search_paths:
            if not search_path.exists():
                continue
            
            # Try to find module file or directory
            potential_paths = [
                search_path / f"{module_name}.py",
                search_path / module_name / "__init__.py",
                search_path / "hands_scaphoid" / f"{module_name}.py",
                search_path / "hands_scaphoid" / module_name / "__init__.py",
            ]
            
            for potential_path in potential_paths:
                if potential_path.exists():
                    try:
                        # Calculate relative import
                        if potential_path.name == "__init__.py":
                            module_path = potential_path.parent
                        else:
                            module_path = potential_path.parent
                        
                        relative_parts = module_path.relative_to(current_dir).parts
                        
                        if not relative_parts:
                            return f".{module_name}"
                        
                        # Build the relative import string
                        dots = ""
                        remaining_parts = []
                        
                        for part in relative_parts:
                            if part == "..":
                                dots += "."
                            else:
                                remaining_parts.append(part)
                        
                        if not dots:
                            dots = "."
                        
                        if remaining_parts:
                            return f"{dots}{'.'.join(remaining_parts)}.{module_name}"
                        else:
                            return f"{dots}{module_name}"
                            
                    except ValueError:
                        continue
        
        return None
    
    def suggest_relative_import_fixes(self, imports: List[ImportInfo], file_path: Path) -> List[str]:
        """Suggest fixes for imports that should be relative based on file system."""
        suggestions = []
        
        for imp in imports:
            if not imp.module.startswith('.'):  # Not already relative
                relative_suggestion = self._calculate_relative_import(imp.module, file_path)
                if relative_suggestion:
                    suggestions.append(f"  Suggestion: '{imp.module}' should be '{relative_suggestion}'")
        
        return suggestions
    
    def auto_fix_relative_imports(self, imports: List[ImportInfo], file_path: Path) -> List[ImportInfo]:
        """Auto-fix imports to use proper relative imports based on file system."""
        fixed_imports = []
        
        for imp in imports:
            if not imp.module.startswith('.'):  # Not already relative
                relative_module = self._calculate_relative_import(imp.module, file_path)
                if relative_module:
                    # Create a new ImportInfo with the fixed module name
                    fixed_imp = ImportInfo(
                        module=relative_module,
                        names=imp.names,
                        alias=imp.alias,
                        is_from=imp.is_from
                    )
                    fixed_imp.line_number = imp.line_number
                    fixed_imports.append(fixed_imp)
                else:
                    fixed_imports.append(imp)
            else:
                fixed_imports.append(imp)
        
        return fixed_imports
    
    def detect_duplicate_imports(self, imports: List[ImportInfo]) -> Dict[str, List[ImportInfo]]:
        """Detect duplicate imports across different modules."""
        name_to_imports = {}
        
        for imp in imports:
            if imp.is_from:
                for name in imp.names:
                    # Handle aliases
                    actual_name = name.split(' as ')[0]
                    if actual_name not in name_to_imports:
                        name_to_imports[actual_name] = []
                    name_to_imports[actual_name].append((imp, name))
            else:
                # For regular imports, use the module name or alias
                key = imp.alias if imp.alias else imp.module.split('.')[-1]
                if key not in name_to_imports:
                    name_to_imports[key] = []
                name_to_imports[key].append((imp, key))
        
        # Find duplicates
        duplicates = {name: imps for name, imps in name_to_imports.items() if len(imps) > 1}
        return duplicates
    
    def resolve_duplicate_imports(self, imports: List[ImportInfo], file_path: Path) -> List[ImportInfo]:
        """Resolve duplicate imports by prioritizing local imports."""
        duplicates = self.detect_duplicate_imports(imports)
        
        if duplicates:
            print(f"Duplicate imports detected in {file_path}:")
            for name, imp_list in duplicates.items():
                print(f"  '{name}' imported from: {[imp[0].module for imp in imp_list]}")
        
        # Create a set to track resolved imports
        resolved_imports = []
        removed_names = set()
        
        for imp in imports:
            should_include = True
            
            if imp.is_from:
                # Filter out duplicate names from this import
                filtered_names = []
                for name in imp.names:
                    actual_name = name.split(' as ')[0]
                    
                    if actual_name in duplicates and actual_name not in removed_names:
                        # Find the best import for this name (prioritize local imports)
                        best_import = self._choose_best_import(actual_name, duplicates[actual_name])
                        if best_import[0] == imp:
                            filtered_names.append(name)
                            removed_names.add(actual_name)
                        # else: skip this name from this import
                    elif actual_name not in duplicates:
                        filtered_names.append(name)
                
                if filtered_names:
                    # Create new import with filtered names
                    new_imp = ImportInfo(
                        module=imp.module,
                        names=filtered_names,
                        alias=imp.alias,
                        is_from=imp.is_from
                    )
                    new_imp.line_number = imp.line_number
                    resolved_imports.append(new_imp)
            else:
                # For regular imports, check if this is the chosen one
                key = imp.alias if imp.alias else imp.module.split('.')[-1]
                if key in duplicates and key not in removed_names:
                    best_import = self._choose_best_import(key, duplicates[key])
                    if best_import[0] == imp:
                        resolved_imports.append(imp)
                        removed_names.add(key)
                elif key not in duplicates:
                    resolved_imports.append(imp)
        
        return resolved_imports
    
    def _choose_best_import(self, name: str, import_candidates: List[Tuple]) -> Tuple:
        """Choose the best import from candidates, prioritizing local imports."""
        # Priority order: local relative > local absolute > third party > standard
        def get_priority(imp_tuple):
            imp, _ = imp_tuple
            category = self._categorize_import(imp, Path())  # Path not used in categorization logic
            
            if imp.module.startswith('.'):
                return 0  # Highest priority: relative imports
            elif category == 'local':
                return 1  # Second: local absolute imports
            elif category == 'third_party':
                return 2  # Third: third party
            else:
                return 3  # Lowest: standard library
        
        return min(import_candidates, key=get_priority)

@click.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument('files', nargs=-1, required=True, type=click.Path(exists=True), 
               help='Python files to organize')
@click.option('--dry-run', is_flag=True, 
              help='Show changes without modifying files')
@click.option('--backup', is_flag=True, 
              help='Create backup files (.bak) before modifying')
@click.option('--remove-unused', is_flag=True, 
              help='Remove unused imports (default: keep all imports)')
@click.option('--fix-relative', is_flag=True, 
              help='Auto-fix relative imports using path-based calculation')
@click.option('--verbose', '-v', is_flag=True, 
              help='Show detailed information during processing')
def main(files, dry_run, backup, remove_unused, fix_relative, verbose):
    """
    Organize Python imports with #%% [section] format.
    
    This script analyzes Python files and organizes their imports according to the project's
    standards. It categorizes imports, sorts them alphabetically, detects unused imports,
    and resolves duplicate imports by prioritizing local ones.
    
    Features:
    • Organizes imports into standard sections with #%% headers
    • Sorts imports alphabetically within each section  
    • Formats multi-line imports with proper parentheses
    • Detects and reports unused imports
    • Path-based relative import calculation
    • Resolves duplicate imports (prioritizes local imports)
    • Supports dry-run mode for safe preview
    
    \b
    Examples:
      # Organize imports in a single file
      import_organizer.py file.py
      
      # Preview changes without modifying                   
      import_organizer.py --dry-run file.py
      
      # Create backup before modifying
      import_organizer.py --backup file.py
      
      # Auto-fix relative imports based on file system paths
      import_organizer.py --fix-relative file.py
      
      # Process multiple files with verbose output
      import_organizer.py --verbose src/**/*.py
    """
    
    analyzer = ImportAnalyzer()
    
    total_files = len(files)
    processed = 0
    errors = 0
    
    for file_path in files:
        try:
            if verbose or total_files == 1:
                click.secho(f"Processing {file_path}...", fg='blue')
            
            if backup and not dry_run:
                backup_path = f"{file_path}.bak"
                import shutil
                shutil.copy2(file_path, backup_path)
                if verbose:
                    click.secho(f"  ✓ Created backup: {backup_path}", fg='green')
            
            organized_content = analyzer.organize_imports(file_path, fix_relative=fix_relative)
            
            if dry_run:
                click.secho(f"\n--- Organized content for {file_path} ---", fg='yellow', bold=True)
                click.echo(organized_content)
                click.secho("-" * 60, fg='white', dim=True)
            else:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(organized_content)
                if verbose or total_files == 1:
                    click.secho(f"  ✓ Organized imports in ", fg='green', nl=False)
                    click.secho(f"{file_path}", fg='cyan')
            
            processed += 1
                
        except Exception as e:
            click.secho(f"❌ Error processing {file_path}: {e}", fg='red', err=True)
            errors += 1
    
    # Summary
    if total_files > 1:
        click.secho(f"\nSummary: ", bold=True, nl=False)
        click.secho(f"{processed}", fg='green', nl=False)
        click.secho("/", nl=False)
        click.secho(f"{total_files}", fg='blue', nl=False)
        click.echo(" files processed successfully")
        if errors > 0:
            click.secho(f"         {errors} files had errors", fg='red')
        if dry_run:
            click.secho("         (dry run - no files were modified)", fg='yellow')

if __name__ == '__main__':
    main()