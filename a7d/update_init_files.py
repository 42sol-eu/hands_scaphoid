#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Simple constants for python projects.
----
file:
    name:        update_init_files.py  
    uuid:        5d9f9244-9783-4db3-a037-690ebbc99b70
description:     Simple generator helper for python projects
authors:         felix@42sol.eu
project:
project:
    name:        a7d
    uuid:        2cc2a024-ae2a-4d2c-91c2-f41348980f7f
    url:         https://github.com/42sol-eu/a7d
"""
# %% [External imports]
import ast               #!md| [docs](https://docs.python.org/3/library/ast.html)
from enum import Enum    #!md| [docs](https://docs.python.org/3/library/enum.html)
from pathlib import (    #!md| [docs](https://docs.python.org/3/library/pathlib.html)
    Path as FsPath,
)
import subprocess        #!md| [docs](https://docs.python.org/3/library/subprocess.html)
from typing import Any, Union, Optional
PathLike = Union[str, FsPath]

from click import (      #!md| [docs](https://click.palletsprojects.com/en/8.1.x/)
    command,
    argument,
    option,
    Path,
    prompt,
    secho,
    echo,
    confirm,
#    Choice,
)


# %% [Parameters]


class Parameter:
    """Parameter for execution.""" 
    init_file_name:     str = "__init__.py"

P = Parameter()


# %% [Types]


class PrivacyLevel(Enum):
    """
    An enumeration representing different levels of privacy for entities.

    Attributes:
        PUBLIC: Indicates the entity is publicly accessible.
        INTERNAL: Indicates the entity is accessible within the internal scope.
        PRIVATE: Indicates the entity is private and should not be accessed externally.
        DUNDER: Indicates the entity uses double underscore (dunder) naming, 
                typically for special or magic methods.
    """
    PUBLIC = "public"
    INTERNAL = "internal"
    PRIVATE = "private"
    DUNDER = "dunder"


# %% [Functions]
def is_private_name(name: str) -> PrivacyLevel:
    """Determine the privacy level of a Python name.
    
    Returns: (PrivacyLevel)
        'public': Normal public name
        'internal': Single underscore prefix (internal use)
        'private': Double underscore prefix (name mangled)
        'dunder': Double underscore prefix and suffix (special methods)
    """
    if name.startswith('__') and name.endswith('__'):
        return PrivacyLevel.DUNDER
    elif name.startswith('__') :
        return PrivacyLevel.PRIVATE
    elif name.startswith('_'):
        return PrivacyLevel.INTERNAL
    else:
        return PrivacyLevel.PUBLIC


def scan_init_file(folder: PathLike) -> list:
    """Scan __init__.py and return a list of import statements."""
    if isinstance(folder, str):
        folder = FsPath(folder)

    init_path = folder / P.init_file_name
    if not init_path.exists():
        return []
    with open(init_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
    imports = [line.strip() for line in lines \
               if line.strip().startswith("from ") or line.strip().startswith("import ")]
    return imports


def scan_python_file(file_path: PathLike, include_private: bool = False) -> list:
    """Scan a Python file and return top-level classes, functions, and global variables.
    
    Args:
        file_path: Path to the Python file to scan
        include_private: If True, include private names (starting with _)
    
    By default, excludes private names as per Python conventions.
    """
    if isinstance(file_path, str):
        file_path = FsPath(file_path)

    with open(file_path, "r", encoding="utf-8") as f:
        node = ast.parse(f.read(), filename=str(file_path))
    elements = []
    for n in node.body:
        if isinstance(n, ast.ClassDef):
            # Include all classes if include_private=True, otherwise skip private ones
            if include_private or not n.name.startswith('_'):
                elements.append(("class", n.name))
        elif isinstance(n, ast.FunctionDef):
            # Include all functions if include_private=True,
            # otherwise skip private ones and dunder methods
            if include_private or not n.name.startswith('_'):
                elements.append(("function", n.name))
        elif isinstance(n, ast.Assign):
            # Check for global variable assignments
            for target in n.targets:
                if isinstance(target, ast.Name):
                    # Include all variables if include_private=True, otherwise skip private ones
                    if include_private or not target.id.startswith('_'):
                        elements.append(("variable", target.id))
        elif isinstance(n, ast.AnnAssign):
            # Type annotated assignments: var: Type = value
            if isinstance(n.target, ast.Name):
                # Include all variables if include_private=True, otherwise skip private ones
                if include_private or not n.target.id.startswith('_'):
                    elements.append(("variable", n.target.id))
    return elements


def suggest_edit(init_imports: list, file_elements: list) -> list:
    """Suggest which elements to add to __init__.py."""
    suggestions = []
    for typ, name in file_elements:
        import_stmt = f"from .{name.lower()} import {name}" \
                    if typ == "class" else f"from . import {name}"
        if not any(name in imp for imp in init_imports):
            suggestions.append(import_stmt)
    return suggestions


def update_init_file(folder: PathLike,
                     new_imports: list,
                     cleanup: bool = True,
                     available_names: set = None,
                     group_by_file: bool = False,
                     element_sources: dict = None,
                     element_order: list = None
    ):
    """Add new imports to __init__.py and sort, optionally cleaning up stale imports."""
    if isinstance(folder, str):
        folder = FsPath(folder)
    if element_sources is None:
        element_sources = {}
    if element_order is None:
        element_order = []
    init_path = folder / P.init_file_name
    if init_path.exists():
        with open(init_path, "r", encoding="utf-8") as f:
            content = f.read()
    else:
        content = ""

    # Parse the AST to safely extract existing imports and __all__
    try:
        tree = ast.parse(content)
        existing_imports = []
        existing_all_names = []
        imported_names = {}  # Track what names are imported from which modules

        for node in tree.body:
            if isinstance(node, ast.ImportFrom):
                module = node.module or ""
                if node.names[0].name == '*':
                    import_stmt = f"from .{module} import *"
                    existing_imports.append(import_stmt)
                    # For wildcard imports, we can't track specific names
                    imported_names[f".{module}"] = {"*"}
                else:
                    names = [alias.name for alias in node.names]
                    import_stmt = f"from .{module} import {', '.join(names)}"
                    existing_imports.append(import_stmt)
                    # Track imported names for this module
                    if f".{module}" not in imported_names:
                        imported_names[f".{module}"] = set()
                    imported_names[f".{module}"].update(names)
            elif isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
                existing_imports.append(f"import {', '.join(names)}")
            elif isinstance(node, ast.Assign):
                # Check for __all__ assignment
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        if isinstance(node.value, ast.List):
                            existing_all_names = []
                            for elem in node.value.elts:
                                if isinstance(elem, ast.Constant) and isinstance(elem.value, str):
                                    existing_all_names.append(elem.value)
                                elif hasattr(elem, 's'):  # For backward compatibility
                                    existing_all_names.append(elem.s)
                        elif isinstance(node.value, ast.Constant):
                            existing_all_names = node.value.value if isinstance(node.value.value, list)
                                                                else []
    except SyntaxError:
        # Fallback to line-by-line parsing if AST fails
        lines = content.splitlines()
        existing_imports = []
        existing_all_names = []
        imported_names = {}
        
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("from ") or stripped.startswith("import "):
                existing_imports.append(stripped)
    
    # Add new imports and consolidate
    all_imports = existing_imports + new_imports
    
    # Parse and consolidate imports by module
    consolidated_imports = {}
    
    for import_stmt in all_imports:
        if import_stmt.startswith("from ."):
            # Parse: "from .module import name1, name2"
            parts = import_stmt.split(" import ")
            if len(parts) == 2:
                module = parts[0].replace("from ", "")
                names_part = parts[1].strip()
                
                # Handle multi-line imports or parentheses
                names_part = names_part.replace("(", "").replace(")", "").strip()
                if names_part == "*":
                    names = ["*"]
                else:
                    names = [name.strip() for name in names_part.split(",") if name.strip()]
                
                if module not in consolidated_imports:
                    consolidated_imports[module] = set()
                consolidated_imports[module].update(names)
    
    # Generate sorted import statements
    sorted_imports = []
    for module in sorted(consolidated_imports.keys()):
        names = sorted(consolidated_imports[module])
        
        # Cleanup: Filter out names that don't exist in source files
        if cleanup and available_names is not None:
            original_count = len(names)
            names = [name for name in names if name in available_names or name == "*"]
            removed_count = original_count - len(names)
            if removed_count > 0:
                secho(f"Removed {removed_count} non-existing imports from {module}", fg="yellow")
        
        if "*" in names:
            sorted_imports.append(f"from {module} import *")
        elif names:  # Only add if there are still names left after cleanup
            if len(names) == 1:
                sorted_imports.append(f"from {module} import {names[0]}")
            elif len(names) <= 3:
                sorted_imports.append(f"from {module} import {', '.join(names)}")
            else:
                # Multi-line import for many names
                names_str = ",\n    ".join(names)
                sorted_imports.append(f"from {module} import (\n    {names_str},\n)")
    
    # Extract header (everything before first import)
    lines = content.splitlines()
    header_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("from ") or stripped.startswith("import ") or stripped.startswith("__all__"):
            break
        header_lines.append(line)
    
    # Write the file with header, imports, and reserve space for __all__
    with open(init_path, "w", encoding="utf-8") as f:
        for line in header_lines:
            f.write(line + "\n")
        if header_lines and header_lines[-1].strip() != "":
            f.write("\n")
        for imp in sorted_imports:
            f.write(imp + "\n")
    
    return existing_all_names


def check_cog_consistency(folder_path: PathLike, include_private: bool, cleanup: bool, group_by_file: bool) -> bool:
    """Check if COG-generated content matches what would be generated now.
    
    Returns:
        True if content matches, False if there are differences
    """
    if isinstance(folder_path, str):
        folder_path = FsPath(folder_path)

    init_file = folder_path / P.init_file_name
    if not init_file.exists():
        secho(f"❌ No {P.init_file_name} file found in {folder_path}", fg="red")
        return False

    # Check if file has COG markers and checksum
    content = init_file.read_text()
    if not ("# [[[cog" in content and "# [[[end]]]" in content):
        secho(f"❌ No COG markers found in {init_file}", fg="red")
        return False

    if "(sum:" not in content:
        secho(f"⚠️  No COG checksum found in {init_file}", fg="yellow")
        secho("   Run: cog -c -r to add checksum protection", fg="yellow")
        return False

    secho(f"🔍 Checking COG consistency for {init_file}...", fg="cyan")

    # Use COG's built-in check functionality
    try:
        result = subprocess.run(
            ["cog", "--check", str(init_file)], 
            capture_output=True, 
            text=True, 
            cwd=folder_path.parent
        )
        
        if result.returncode == 0:
            secho(f"✅ COG content is up-to-date", fg="green")
            return True
        else:
            secho(f"❌ COG content differs from expected", fg="red")
            if result.stdout:
                echo(result.stdout)
            if result.stderr:
                echo(result.stderr)
            secho(f"💡 Run: cog -c -r {init_file} to update", fg="cyan")
            return False

    except FileNotFoundError:
        secho(f"❌ COG not found. Install with: pip install cogapp", fg="red")
        return False
    except Exception as e:
        secho(f"❌ Error running COG check: {e}", fg="red")
        return False

# %% [Main]
@command()
@argument("folder",          type=Path(exists=True, file_okay=False, dir_okay=True))
@option("--all-files",       type=bool,
    is_flag=True,
    default=False,
    help="Scan all Python files in the folder and add all classes/functions to __init__.py.",
)
@option("--include-private", type=bool,
    is_flag=True,
    default=False,
    help="Include private names (starting with _) in the scan and __all__ list.",
)
@option("--cleanup",         type=bool,
    is_flag=True,
    default=True,
    help="Remove non-existing elements from imports and __all__. Use --no-cleanup to disable.",
)
@option("--group-by-file",   type=bool,
    is_flag=True,
    default=False,
    help="Group __all__ entries by source file instead of alphabetical sorting.",
)
@option("--cog-check",       type=bool,
    is_flag=True,
    default=False,
    help="Check if COG-generated content matches what would be generated (requires existing COG checksums).",
)
def cli(folder, all_files, include_private, cleanup, group_by_file, cog_check):
    """Semi-manual CLI for updating __init__.py files in a folder."""
    folder_path = FsPath(folder)
    
    # Handle COG checksum validation
    if cog_check:
        return check_cog_consistency(folder_path, include_private, cleanup, group_by_file)
    
    # Get the relative path from current working directory
    try:
        relative_folder = folder_path.relative_to(FsPath().cwd())
    except ValueError:
        # If folder is not relative to cwd, use absolute path
        relative_folder = folder_path

    secho(f"Scanning {P.init_file_name} in {folder_path}...", fg="cyan")
    if include_private:
        secho("Including private names (starting with _)", fg="yellow")
    else:
        secho("Excluding private names (starting with _) - use --include-private to include them", fg="yellow")

    if cleanup:
        secho("Cleanup mode: Will remove non-existing elements from imports and __all__", fg="yellow")
    else:
        secho("Cleanup disabled: Will preserve existing imports and __all__ entries", fg="yellow")
    init_imports = scan_init_file(folder_path)
    secho(f"Current imports in {P.init_file_name}:", fg="yellow")
    for imp in init_imports:
        echo(f"  {imp}")

    py_files = [f for f in folder_path.iterdir() if f.suffix == ".py" and f.name != P.init_file_name]
    if not py_files:
        secho("No Python files found.", fg="red")
        return

    # First, collect all available names from all files for cleanup validation
    all_available_names = set()
    all_elements = []
    element_sources = {}
    element_order = []  # Track order for file-based grouping
    to_add = []

    for file_path in py_files:
        secho(f"Scanning {file_path.name}...", fg="cyan")
        elements = scan_python_file(file_path, include_private)
        if elements:
            secho(f"Found elements in {file_path.name}:", fg="yellow")
            public_count = internal_count = private_count = dunder_count = 0
            for typ, name in elements:
                privacy = is_private_name(name)
                if privacy == 'public':
                    public_count += 1
                    echo(f"  {typ}: {name}")
                elif privacy == 'internal':
                    internal_count += 1
                    echo(f"  {typ}: {name} (internal)")
                elif privacy == 'private':
                    private_count += 1
                    echo(f"  {typ}: {name} (private)")
                elif privacy == 'dunder':
                    dunder_count += 1
                    echo(f"  {typ}: {name} (dunder)")

                all_available_names.add(name)
                import_stmt = f"from .{file_path.stem} import {name}"
                to_add.append(import_stmt)
                all_elements.append((typ, name))
                # Store full relative path
                element_sources[name] = str(relative_folder / file_path.name)
                # Track order for grouping
                element_order.append((name, str(relative_folder / file_path.name)))

            # Summary
            if not include_private and (internal_count + private_count + dunder_count > 0):
                skipped = internal_count + private_count + dunder_count
                secho(f"  (Skipped {skipped} private names - use --include-private to include)", fg="dim")

    if not all_elements:
        secho("No classes or functions found in any file.", fg="red")
        return

    # Handle interactive mode vs all mode
    if not all_files:
        # Interactive mode - show file selection
        secho("Python files in folder:", fg="cyan")
        for idx, f in enumerate(py_files):
            echo(f"{idx}: {f.name}")

        idx = prompt("Select file to scan", type=Choice([str(i) for i in range(len(py_files))]))
        file_path = py_files[int(idx)]

        elements = scan_python_file(file_path, include_private)
        if not elements:
            secho("No classes or functions found.", fg="red")
            return

        secho(f"Elements in {file_path.name}:", fg="cyan")
        for i, (typ, name) in enumerate(elements):
            echo(f"{i}: {typ} {name}")

        # Reset for interactive mode
        to_add = []
        all_elements = elements
        element_sources = {}
        all_available_names = set()

        for i, (typ, name) in enumerate(elements):
            import_stmt = f"from .{file_path.stem} import {name}"
            if confirm(f"Add '{import_stmt}' to {P.init_file_name}?", default=True):
                to_add.append(import_stmt)
                all_available_names.add(name)
                # Store full relative path
                element_sources[name] = str(relative_folder / file_path.name)

    if to_add:
        existing_all_names = update_init_file(folder_path, to_add, cleanup, all_available_names, group_by_file, element_sources, element_order)
        secho(f"Updated {P.init_file_name} with new imports.", fg="green")

        # Add new names to __all__
        all_names = list(existing_all_names) if existing_all_names else []
        for typ, name in all_elements:
            if name not in all_names and any(name in stmt for stmt in to_add):
                all_names.append(name)

        # Cleanup: Remove names that no longer exist in source files
        if cleanup:
            original_count = len(all_names)
            all_names = [name for name in all_names if name in all_available_names]
            removed_count = original_count - len(all_names)
            if removed_count > 0:
                secho(f"Removed {removed_count} non-existing elements from __all__", fg="yellow")

        # Sort and prepare __all__ list
        if group_by_file and element_order:
            # Group by source file, maintaining file order
            file_groups = {}

            # Group elements by source file while preserving order
            for name, source_path in element_order:
                if name in all_names:  # Only include names that are actually in __all__
                    if source_path not in file_groups:
                        file_groups[source_path] = []
                    file_groups[source_path].append(name)

            # Create ordered list for __all__ with grouping
            grouped_all_names = []
            for source_path in dict.fromkeys(source_path for _, source_path in element_order):
                if source_path in file_groups and file_groups[source_path]:
                    # Add elements from this file, sorted alphabetically
                    sorted_elements = sorted(file_groups[source_path], key=str.lower)
                    grouped_all_names.extend(sorted_elements)

            # Add any remaining names not in element_order (existing ones)
            remaining_names = [name for name in all_names if name not in grouped_all_names]
            if remaining_names:
                grouped_all_names.extend(sorted(remaining_names, key=str.lower))

            all_names = grouped_all_names
        else:
            all_names = sorted(set(all_names), key=str.lower)  # Case-insensitive sort

        # Append the __all__ list to the file
        if all_names:
            init_path = folder_path / P.init_file_name
            with open(init_path, "a", encoding="utf-8") as f:
                f.write("\n")
                if len(all_names) <= 3:
                    # Single line for short lists
                    f.write(f"__all__ = {all_names}\n")
                elif group_by_file and element_order:
                    # Write grouped __all__ with file comments
                    f.write("__all__ = [\n")

                    # Group by source file again for output
                    file_groups = {}
                    for name, source_path in element_order:
                        if name in all_names:
                            if source_path not in file_groups:
                                file_groups[source_path] = []
                            file_groups[source_path].append(name)

                    # Write groups with headers
                    files_list = list(dict.fromkeys(source_path for _, source_path in element_order))
                    for i, source_path in enumerate(files_list):
                        if source_path in file_groups and file_groups[source_path]:
                            # Add comment header for this file
                            f.write(f"    # From {source_path}\n")

                            # Add elements from this file, sorted alphabetically
                            sorted_elements = sorted(file_groups[source_path], key=str.lower)
                            for name in sorted_elements:
                                f.write(f'    "{name}",\n')

                            # Add blank line between file groups (except for last)
                            if i < len(files_list) - 1:
                                f.write("\n")

                    # Add any remaining names not in element_order (existing ones)
                    remaining_names = [name for name in all_names if name not in [n for _, path in element_order for n in file_groups.get(path, [])]]
                    if remaining_names:
                        if files_list:  # Add blank line if there were grouped files
                            f.write("\n")
                        f.write("    # Existing entries\n")
                        for name in sorted(remaining_names, key=str.lower):
                            f.write(f'    "{name}",\n')

                    f.write("]\n")
                else:
                    # Standard multi-line for longer lists with source comments
                    f.write("__all__ = [\n")
                    for name in all_names:
                        if element_sources and name in element_sources:
                            f.write(f'    "{name}",  # {element_sources[name]}\n')
                        else:
                            # For items that were already in __all__ but we don't know their source
                            f.write(f'    "{name}",\n')
                    f.write("]\n")

        # Format code
        init_path = folder_path / P.init_file_name
        secho(f'ruff {str(init_path)}')
        subprocess.run(["ruff", "format", str(init_path)], check=False)

        secho(f"Updated {P.init_file_name} with selected imports and __all__.", fg="green")
    else:
        secho("No changes made.", fg="yellow")

if __name__ == "__main__":
    cli() #-E1120