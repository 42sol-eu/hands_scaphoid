"""
Command to create __init__.py files with automatic imports.

This command scans a directory and creates an __init__.py file with
proper imports from all Python modules found in the directory.
"""

import os
import ast
from pathlib import Path
from typing import List, Set, Optional, Dict, Any
import rich_click as click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def extract_classes_and_functions(file_path: Path) -> Dict[str, List[str]]:
    """Extract class and function names from a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        classes = []
        functions = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                # Only include classes that are defined at module level
                if hasattr(node, 'lineno') and node.col_offset == 0:
                    classes.append(node.name)
            elif isinstance(node, ast.FunctionDef):
                # Only include functions that are defined at module level and don't start with _
                if hasattr(node, 'lineno') and node.col_offset == 0 and not node.name.startswith('_'):
                    functions.append(node.name)
        
        return {
            'classes': classes,
            'functions': functions
        }
    except (SyntaxError, UnicodeDecodeError, FileNotFoundError) as e:
        console.print(f"[yellow]Warning: Could not parse {file_path}: {e}[/yellow]")
        return {'classes': [], 'functions': []}


def scan_directory_for_modules(directory: Path) -> Dict[str, Dict[str, List[str]]]:
    """Scan directory for Python modules and extract their exports."""
    modules = {}
    
    for file_path in directory.glob("*.py"):
        if file_path.name.startswith('_'):
            continue  # Skip private modules and __init__.py
        
        module_name = file_path.stem
        exports = extract_classes_and_functions(file_path)
        
        if exports['classes'] or exports['functions']:
            modules[module_name] = exports
    
    return modules


def generate_init_content(modules: Dict[str, Dict[str, List[str]]], 
                         package_name: str = "",
                         author: str = "",
                         description: str = "") -> str:
    """Generate the content for __init__.py file."""
    
    lines = []
    
    # Add header
    lines.append('"""')
    if description:
        lines.append(f"{description}")
    else:
        lines.append(f"Package initialization for {package_name or 'this package'}.")
    lines.append("")
    lines.append("This file automatically imports public classes and functions")
    lines.append("from all modules in this package.")
    if author:
        lines.append(f"")
        lines.append(f"Author: {author}")
    lines.append('"""')
    lines.append("")
    
    # Add imports
    all_exports = []
    
    for module_name, exports in sorted(modules.items()):
        if exports['classes'] or exports['functions']:
            import_items = exports['classes'] + exports['functions']
            all_exports.extend(import_items)
            
            lines.append(f"from .{module_name} import (")
            for i, item in enumerate(sorted(import_items)):
                comma = "," if i < len(import_items) - 1 else ""
                lines.append(f"    {item}{comma}")
            lines.append(")")
            lines.append("")
    
    # Add __all__ list
    if all_exports:
        lines.append("__all__ = [")
        for i, item in enumerate(sorted(set(all_exports))):
            comma = "," if i < len(set(all_exports)) - 1 else ""
            lines.append(f'    "{item}"{comma}')
        lines.append("]")
        lines.append("")
    
    # Add version if package name provided
    if package_name:
        lines.append(f'__version__ = "1.0.0"')
        lines.append(f'__package_name__ = "{package_name}"')
        lines.append("")
    
    return "\n".join(lines)


def preview_init_content(directory: Path, modules: Dict[str, Dict[str, List[str]]]) -> None:
    """Show a preview of what will be generated."""
    table = Table(title=f"Preview of __init__.py for {directory.name}")
    table.add_column("Module", style="cyan")
    table.add_column("Classes", style="green")
    table.add_column("Functions", style="blue")
    
    for module_name, exports in sorted(modules.items()):
        classes_str = ", ".join(exports['classes']) if exports['classes'] else "-"
        functions_str = ", ".join(exports['functions']) if exports['functions'] else "-"
        table.add_row(module_name, classes_str, functions_str)
    
    console.print(table)
    
    total_classes = sum(len(exports['classes']) for exports in modules.values())
    total_functions = sum(len(exports['functions']) for exports in modules.values())
    
    console.print(f"\n[bold]Summary:[/bold] {len(modules)} modules, {total_classes} classes, {total_functions} functions")


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
@click.option('--package-name', '-n', help='Name of the package')
@click.option('--author', '-a', help='Author name for the header')
@click.option('--description', '-d', help='Package description')
@click.option('--dry-run', is_flag=True, help='Show preview without creating file')
@click.option('--force', is_flag=True, help='Overwrite existing __init__.py file')
@click.option('--output', '-o', help='Output file path (default: directory/__init__.py)')
def create_init(directory: str, package_name: Optional[str], author: Optional[str], 
               description: Optional[str], dry_run: bool, force: bool, output: Optional[str]):
    """
    Create __init__.py file with automatic imports from directory modules.
    
    This command scans the specified directory for Python modules and creates
    an __init__.py file that imports all public classes and functions.
    
    Examples:
        dna create-init .                    # Create __init__.py in current directory
        dna create-init ./src/mypackage      # Create __init__.py in specific directory
        dna create-init . --dry-run          # Preview what would be generated
        dna create-init . --package-name myapp --author "Your Name"
    """
    directory_path = Path(directory).resolve()
    
    console.print(f"[bold]Scanning directory:[/bold] {directory_path}")
    
    # Scan for modules
    modules = scan_directory_for_modules(directory_path)
    
    if not modules:
        console.print("[yellow]No Python modules found in directory![/yellow]")
        return
    
    # Show preview
    preview_init_content(directory_path, modules)
    
    if dry_run:
        console.print("\n[cyan]Dry run mode - no file created[/cyan]")
        content = generate_init_content(
            modules, 
            package_name or directory_path.name,
            author or "",
            description or ""
        )
        console.print(Panel(content, title="Generated __init__.py content", border_style="blue"))
        return
    
    # Determine output path
    if output:
        output_path = Path(output)
    else:
        output_path = directory_path / "__init__.py"
    
    # Check if file exists
    if output_path.exists() and not force:
        console.print(f"[yellow]File {output_path} already exists. Use --force to overwrite.[/yellow]")
        return
    
    # Generate content
    content = generate_init_content(
        modules,
        package_name or directory_path.name,
        author or "",
        description or ""
    )
    
    # Write file
    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        console.print(f"[green]✓ Created {output_path}[/green]")
        
        # Show summary
        total_exports = sum(len(exports['classes']) + len(exports['functions']) 
                          for exports in modules.values())
        console.print(f"[dim]Imported {total_exports} items from {len(modules)} modules[/dim]")
        
    except Exception as e:
        console.print(f"[red]Error writing file: {e}[/red]")


if __name__ == "__main__":
    create_init()