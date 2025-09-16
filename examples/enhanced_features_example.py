#!/usr/bin/env python3
"""
Enhanced example demonstrating all the new features of hands-scaphoid.

This example shows:
1. Rich console output
2. Archive context manager with existing archives
3. Standalone method usage
4. Proper method naming (list_files, write_line)
5. Dry-run feature

File:
    name: enhanced_features_example.py
    date: 2025-09-16

Description:
    Example demonstrating enhanced features

Authors: ["Andreas Häberle"]
"""

import tempfile
from pathlib import Path
from hands_scaphoid import Directory, File, Archive


def main():
    """Demonstrate the enhanced features."""
    from rich.console import Console
    console = Console()
    
    console.print("=== Enhanced Features Example ===\n", style="bold blue")
    
    # Create a temporary directory for the example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        console.print(f"Working in temporary directory: {temp_path}\n")
        
        # Change to the temp directory
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            console.print("1. [bold]Standalone method usage (no context managers)[/bold]")
            
            # Create directories and files without context managers
            project_dir = Directory('my_project')
            project_dir.create_directory()
            console.print(f"   Directory exists: {project_dir.exists()}")
            
            # Create a README file
            readme = File('my_project/README.md')
            readme.create_file().write_content("# My Project\n\nThis is my awesome project.\n")
            
            # Create a config file with method chaining
            config = File('my_project/config.json')
            config.create_file().write_line('{')\
                  .write_line('  "name": "my_project",')\
                  .write_line('  "version": "1.0.0"')\
                  .write_line('}')
            
            console.print("   Created project files using standalone methods")
            
            # List files using the new method name
            files = project_dir.list_files()
            console.print(f"   Project contains {len(files)} files:")
            for file in files:
                console.print(f"     - {file.name}")
            
            console.print("\n2. [bold]Dry-run feature demonstration[/bold]")
            
            # Create dry-run instances
            dry_project = Directory('dry_project', dry_run=True)
            dry_readme = File('dry_project/README.md', dry_run=True)
            dry_archive = Archive(source='dry_project', dry_run=True)
            
            console.print("   Dry-run operations (no actual changes):")
            dry_project.create_directory()
            dry_readme.create_file().add_heading("Dry Run Project").write_line("This is a simulation.")
            dry_archive.add_directory('dry_project')
            
            console.print("\n3. [bold]Working with existing archives[/bold]")
            
            # Create an archive first
            with Archive(source='my_project', target='project_backup.zip') as archive:
                archive.add_directory('my_project')
            
            console.print("   Created initial archive")
            
            # Now work with the existing archive
            with Archive(source='project_backup.zip') as existing_archive:
                console.print(f"   Archive contents: {existing_archive.list_contents()}")
                
                # Add an additional file to the existing archive (create outside context)
                import os
                current_dir = os.getcwd()
                extra_file = File(f'{current_dir}/extra.txt')
                extra_file.create_file().write_content("This is an extra file added to the archive.\n")
                existing_archive.add_file(f'{current_dir}/extra.txt', 'additional_files/extra.txt')
                
            console.print("   Added file to existing archive")
            
            # Verify the archive was updated
            with Archive(source='project_backup.zip') as updated_archive:
                contents = updated_archive.list_contents()
                console.print(f"   Updated archive contents: {contents}")
            
            console.print("\n4. [bold]Context manager with enhanced features[/bold]")
            
            # Demonstrate enhanced context manager usage
            with Directory('enhanced_project') as project:
                console.print(f"   Working in: {project.get_current_path()}")
                
                with File('main.py') as main_file:
                    main_file.add_heading("Main Module", level=2)\
                             .write_line('#!/usr/bin/env python3')\
                             .write_line('"""Main module."""')\
                             .write_line('')\
                             .write_line('def main():')\
                             .write_line('    print("Hello, World!")')\
                             .write_line('')\
                             .write_line('if __name__ == "__main__":')\
                             .write_line('    main()')
                
                # List files in the current directory context
                project_files = project.list_files()
                console.print(f"   Enhanced project files: {[f.name for f in project_files]}")
            
            console.print("\n5. [bold]Method chaining and fluent interface[/bold]")
            
            # Demonstrate method chaining
            File('chained_example.txt')\
                .create_file()\
                .add_heading("Chained Operations")\
                .write_line("This file was created using method chaining.")\
                .write_line("Each method returns self, allowing fluent syntax.")\
                .add_heading("Features", level=2)\
                .write_line("- Method chaining")\
                .write_line("- Fluent interface")\
                .write_line("- Rich console output")
            
            console.print("   Created file using method chaining")
            
            # Show the content
            content = File('chained_example.txt').read_content()
            console.print("   File content preview:")
            for i, line in enumerate(content.split('\n')[:5]):
                if line.strip():
                    console.print(f"     {i+1}: {line}")
            
            console.print("\n[green]✓ All enhanced features demonstrated successfully![/green]")
            
        finally:
            # Restore original working directory
            os.chdir(original_cwd)


if __name__ == "__main__":
    main()