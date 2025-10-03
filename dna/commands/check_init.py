"""
Check init command module.
"""

import rich_click as click
from rich.console import Console

from .init_checker import check_init_imports as _check_init

console = Console()


@click.command()
@click.argument('init_file', type=click.Path(exists=True))
def check_init(init_file):
    """
    📦 **Check __init__.py imports** against __all__ list.
    
    This command analyzes an __init__.py file and reports:
    - Imports that are not included in __all__
    - Items in __all__ that are not imported
    - Unused imports
    
    **Example:**
    
    ```bash
    do check-init src/mypackage/__init__.py
    ```
    """
    results = _check_init(init_file)
    
    if results['missing_in_all']:
        console.print("❌ [red]Imports missing from __all__:[/red]")
        for item in results['missing_in_all']:
            console.print(f"  • {item}")
        console.print()
    
    if results['missing_imports']:
        console.print("❌ [red]Items in __all__ not imported:[/red]")
        for item in results['missing_imports']:
            console.print(f"  • {item}")
        console.print()
    
    if results['unused_imports']:
        console.print("⚠️  [yellow]Potentially unused imports:[/yellow]")
        for item in results['unused_imports']:
            console.print(f"  • {item}")
        console.print()
    
    if not any([results['missing_in_all'], results['missing_imports'], results['unused_imports']]):
        console.print("✅ [green]All imports and __all__ entries are consistent![/green]")