# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "rich-click>=1.7.0",
#     "copier>=9.10.2",
#     "rich>=13.0.0",
# ]
# ///
"""DNA - A CLI tool for Python package development and maintenance.

This script helps with common Python development tasks like:
- Finding classes in files or folder structures
- Checking imports in __init__.py files
- Creating new files from templates
- ... more see ./commands/
"""

# [Standard library imports]
import sys
from pathlib import Path
import subprocess
import os
import importlib.util

# Add the current directory to Python path to import from 'commands' folder
sys.path.insert(0, str(Path(__file__).parent))

# [Local imports (special: use local wheels from ./dist/)]
try:
    from commands.ensure_dependencies_installed import ensure_dependencies_installed
except ImportError:
    # Fallback function when ensure_dependencies_installed is not available
    def ensure_dependencies_installed():
        print("⚠️ ensure_dependencies_installed not available - basic functionality only")
        return True    

try:
    from commands.class_finder import find_classes
except ImportError:
    # Fallback - commands might not exist yet
    def find_classes(*args, **kwargs):
        print("⚠️ class_finder not available - install commands module")
        return {}

try:
    from commands.init_checker import check_init_imports
except ImportError:
    # Fallback - commands might not exist yet
    def check_init_imports(*args, **kwargs):
        print("⚠️ init_checker not available - install commands module")
        return {}

try:
    from commands.file_creator import create_file_from_template
except ImportError:
    # Fallback - commands might not exist yet
    def create_file_from_template(*args, **kwargs):
        print("⚠️ file_creator not available - install commands module")
        return False

# [Third party imports]
# First define a basic console
try:
    from rich.console import Console
    console = Console()
except ImportError:
    # Basic console fallback if Rich not available
    class BasicConsole:
        def print(self, *args, **kwargs):
            print(*args)
    console = BasicConsole()

# Now we can safely call ensure_dependencies_installed with console available
ensure_dependencies_installed()  

try:
    import rich_click as click
    from rich.console import Console
    from rich.table import Table
    # Re-initialize console with Rich if available
    console = Console()
except ImportError:
    # Fallback - rich-click might not be installed yet
    console.print("⚠️ [yellow]rich-click not available - install commands module[/yellow]")
   

console = Console()

# Configure rich-click
click.rich_click.USE_RICH_MARKUP = True
click.rich_click.USE_MARKDOWN = True

@click.group()
@click.version_option(version="1.0.0", prog_name="do")
@click.option('--auto-install', is_flag=True, help='Automatically install missing dependencies')
def cli(auto_install):
    """
    **DO** - A CLI tool for Python package development and maintenance.
    
    This tool provides helpful utilities for Python developers to:
    
    - 🔍 Find and analyze classes in your codebase
    - 📦 Check __init__.py imports and __all__ consistency  
    - 📄 Create new files from custom templates
    
    Use `do COMMAND --help` for more information on specific commands.
    """
    pass


@cli.command()
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
    try:
        from commands.class_finder import find_classes as _find_classes
    except ImportError:
        console.print("❌ [red]class_finder module not available[/red]")
        return
    
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
        import json
        console.print(json.dumps(results, indent=2, default=str))


@cli.command()
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
    try:
        from commands.init_checker import check_init_imports as _check_init
    except ImportError:
        console.print("❌ [red]init_checker module not available[/red]")
        return
    
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


# Dynamic plugin system for command discovery
def discover_and_load_commands():
    """Automatically discover and load all command plugins from the commands directory."""
    commands_dir = Path(__file__).parent / "commands"
    loaded_commands = []
    failed_commands = []
    
    # Add commands directory to Python path for imports
    commands_path = str(commands_dir)
    if commands_path not in sys.path:
        sys.path.insert(0, commands_path)
    
    # Skip these files as they're not commands or utilities
    skip_files = {
        '__init__.py', 
        'file_creator.py',                    # Utility module
        'setup_console.py',                   # Utility module  
        'ensure_dependencies_installed.py',   # Utility module
        'init_checker.py',                    # Old version - use check_init.py
        'class_finder.py'                     # Old version - use find_classes.py
    }
    
    # Auto-discover commands from the commands package
    try:
        import commands
        
        # Get all attributes from commands module that might be commands
        for attr_name in dir(commands):
            if attr_name.startswith('_'):
                continue
                
            attr = getattr(commands, attr_name)
            
            # Check if it's a click command
            is_click_command = (
                hasattr(attr, '__click_params__') or 
                hasattr(attr, 'callback') or
                str(type(attr)).find('Command') != -1 or
                str(type(attr)).find('RichCommand') != -1
            )
            
            if is_click_command:
                # Convert function name to CLI command name
                cli_name = attr_name.replace('_', '-')
                
                # Special naming rules for better CLI experience
                if cli_name == 'list-py-files':
                    cli_name = 'list-py'
                elif cli_name == 'install-wheels-command':
                    cli_name = 'install-wheels-alt'
                
                try:
                    cli.add_command(attr, name=cli_name)
                    loaded_commands.append(f"{cli_name} (auto-discovered)")
                except Exception as e:
                    failed_commands.append(f"{cli_name}: {e}")
                    
    except ImportError as e:
        failed_commands.append(f"commands package import failed: {e}")
    
    # Then scan for any additional command files not in the mapping
    for py_file in commands_dir.glob("*.py"):
        if py_file.name in skip_files or py_file.name.startswith('_'):
            continue
            
        module_name = py_file.stem
        
        # Skip utility modules that aren't commands
        if module_name in ['file_creator', 'setup_console', 'ensure_dependencies_installed']:
            continue
            
        try:
            # Import module directly
            spec = importlib.util.spec_from_file_location(f"plugin_{module_name}", py_file)
            if spec is None or spec.loader is None:
                continue
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for click commands
            command_found = False
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                
                # Check if it's a click command
                if hasattr(attr, '__click_params__'):
                    cmd_name = attr_name.replace('_', '-')
                    
                    try:
                        cli.add_command(attr, name=cmd_name)
                        loaded_commands.append(f"{cmd_name} (plugin from {module_name})")
                        command_found = True
                        break
                    except Exception as e:
                        failed_commands.append(f"{cmd_name}: {e}")
            
            if not command_found:
                # Check for common function names that should be commands
                common_funcs = ['main', module_name, f"{module_name}_command"]
                for func_name in common_funcs:
                    if hasattr(module, func_name):
                        func = getattr(module, func_name)
                        if callable(func) and hasattr(func, '__click_params__'):
                            cmd_name = module_name.replace('_', '-')
                            cli.add_command(func, name=cmd_name)
                            loaded_commands.append(f"{cmd_name} (auto from {module_name})")
                            command_found = True
                            break
                            
        except Exception as e:
            failed_commands.append(f"{module_name}: {e}")
    
    # Report results (only show details with --help on main command)
    show_details = '--help' in sys.argv and len(sys.argv) == 2  # Only main help
    
    if loaded_commands and show_details:
        console.print(f"[green]✓ Loaded {len(loaded_commands)} command plugins[/green]")
        for cmd in loaded_commands:
            console.print(f"  [dim]• {cmd}[/dim]")
    
    if failed_commands and show_details:
        console.print(f"[yellow]⚠ Failed to load {len(failed_commands)} commands:[/yellow]")
        for cmd in failed_commands:
            console.print(f"  [dim]• {cmd}[/dim]")
    
    return len(loaded_commands), len(failed_commands)

# Auto-discover and load all command plugins
loaded_count, failed_count = discover_and_load_commands()


@cli.command()
@click.option('--create-dist', is_flag=True, help='Create dist folder and download wheels')
def install_wheels(create_dist):
    """
    📦 **Install dependencies** from local wheel files.
    
    This command installs required dependencies (copier, rich-cli, rich-click)
    from wheel files in the dist/ directory. If --create-dist is used,
    it will create the dist folder and download wheels first.
    
    **Examples:**
    
    ```bash
    # Install from existing wheel files
    dna install-wheels
    
    # Create dist folder and download wheels, then install
    dna install-wheels --create-dist
    ```
    """
    if create_dist:
        dist_path = Path(__file__).parent.parent / 'dist'
        dist_path.mkdir(exist_ok=True)
        
        console.print("📡 Downloading wheel files...")
        packages = ['copier>=9.10.2', 'rich-cli>=1.8.0', 'rich-click>=1.7.0']
        
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pip', 'download'
            ] + packages + [
                '--dest', str(dist_path),
                '--only-binary=:all:'
            ], check=True)
            console.print("✅ Successfully downloaded wheel files to dist/")
        except subprocess.CalledProcessError as e:
            console.print(f"❌ Failed to download wheels: {e}")
            return
    
    # Install wheels
    success = ensure_dependencies_installed()
    if success:
        console.print("🎉 [green]Wheel installation completed![/green]")
    else:
        console.print("❌ [red]Wheel installation failed![/red]")


if __name__ == '__main__':
    # Check and install dependencies if needed
    if '--auto-install' in sys.argv or not ensure_dependencies_installed():
        console.print("🔧 Missing dependencies detected, attempting installation...")
        if not ensure_dependencies_installed():
            console.print("❌ [red]Failed to install dependencies. Use 'do install-wheels --create-dist'[/red]")
            sys.exit(1)
    
    cli()