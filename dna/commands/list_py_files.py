"""
List Python files command - demonstrates the dynamic plugin system.

This command scans directories and lists Python files with basic information.
"""

import os
from pathlib import Path
from typing import List
import rich_click as click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()


def count_lines_in_file(file_path: Path) -> int:
    """Count lines in a Python file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def get_file_info(file_path: Path) -> dict:
    """Get basic information about a Python file."""
    stat = file_path.stat()
    return {
        'size': stat.st_size,
        'lines': count_lines_in_file(file_path),
        'modified': stat.st_mtime
    }


@click.command()
@click.argument('directory', type=click.Path(exists=True, file_okay=False, dir_okay=True), default='.')
@click.option('--recursive', '-r', is_flag=True, help='Search recursively in subdirectories')
@click.option('--min-lines', type=int, default=0, help='Minimum lines to include')
@click.option('--sort-by', type=click.Choice(['name', 'size', 'lines']), default='name', help='Sort files by')
def list_py_files(directory: str, recursive: bool, min_lines: int, sort_by: str):
    """
    📋 List Python files in a directory with basic information.
    
    This command scans the specified directory for Python files and displays
    information about each file including size, line count, and modification date.
    
    Examples:
        dna list-py-files .                     # List files in current directory
        dna list-py-files . --recursive         # Search recursively  
        dna list-py-files . --min-lines 50      # Only files with 50+ lines
        dna list-py-files . --sort-by lines     # Sort by line count
    """
    directory_path = Path(directory).resolve()
    
    console.print(f"[bold]Scanning directory:[/bold] {directory_path}")
    
    # Find Python files
    if recursive:
        pattern = "**/*.py"
    else:
        pattern = "*.py"
    
    files = []
    for py_file in directory_path.glob(pattern):
        if py_file.is_file() and not py_file.name.startswith('.'):
            info = get_file_info(py_file)
            if info['lines'] >= min_lines:
                files.append({
                    'path': py_file,
                    'name': py_file.name,
                    'relative_path': py_file.relative_to(directory_path),
                    **info
                })
    
    if not files:
        console.print("[yellow]No Python files found matching criteria![/yellow]")
        return
    
    # Sort files
    if sort_by == 'size':
        files.sort(key=lambda x: x['size'], reverse=True)
    elif sort_by == 'lines':
        files.sort(key=lambda x: x['lines'], reverse=True)
    else:
        files.sort(key=lambda x: x['name'])
    
    # Create table
    table = Table(title=f"Python Files in {directory_path.name}")
    table.add_column("File", style="cyan")
    table.add_column("Lines", justify="right", style="green")
    table.add_column("Size", justify="right", style="blue")
    
    if recursive:
        table.add_column("Path", style="dim")
    
    total_lines = 0
    total_size = 0
    
    for file_info in files:
        size_str = f"{file_info['size']:,} bytes"
        if file_info['size'] > 1024:
            size_str = f"{file_info['size']/1024:.1f}KB"
        
        row = [
            file_info['name'],
            str(file_info['lines']),
            size_str
        ]
        
        if recursive:
            row.append(str(file_info['relative_path'].parent) if file_info['relative_path'].parent != Path('.') else '.')
        
        table.add_row(*row)
        
        total_lines += file_info['lines']
        total_size += file_info['size']
    
    console.print(table)
    
    # Summary
    total_size_str = f"{total_size:,} bytes"
    if total_size > 1024:
        total_size_str = f"{total_size/1024:.1f}KB"
    
    console.print(f"\n[bold]Summary:[/bold] {len(files)} files, {total_lines:,} total lines, {total_size_str}")


if __name__ == "__main__":
    list_py_files()