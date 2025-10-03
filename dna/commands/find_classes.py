"""
Find classes command module.
"""

import json
from pathlib import Path

import rich_click as click
from rich.console import Console
from rich.table import Table

from .class_finder import find_classes as _find_classes

console = Console()


@click.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--recursive', '-r', is_flag=True, help='Search recursively in subdirectories')
@click.option('--output-format', '-f', type=click.Choice(['table', 'list', 'json']), default='table', help='Output format')
def find_classes(path, recursive, output_format):
    """
    🔍 **Find all classes** in a file or directory.
    
    This command scans Python files and extracts all class definitions,
    showing their names, file locations, and line numbers.
    
    **Examples:**
    
    ```bash
    do find-classes src/
    do find-classes --recursive src/
    do find-classes -f json myfile.py
    ```
    """
    results = _find_classes(path, recursive)
    
    if output_format == 'table':
        table = Table(title="Classes Found")
        table.add_column("Class Name", style="cyan")
        table.add_column("File", style="green")
        table.add_column("Line", style="yellow")
        
        for result in results:
            table.add_row(result['class_name'], str(result['file']), str(result['line']))
        
        console.print(table)
    elif output_format == 'list':
        for result in results:
            console.print(f"{result['class_name']} - {result['file']}:{result['line']}")
    elif output_format == 'json':
        console.print(json.dumps(results, indent=2, default=str))