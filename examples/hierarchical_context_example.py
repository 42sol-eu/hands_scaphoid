#!/usr/bin/env python3
"""
Example usage of the hierarchical context managers.

This example demonstrates how to use the Directory, File, and Archive classes
with nested context managers to perform file system operations.

File:
    name: hierarchical_context_example.py
    date: 2025-09-16

Description:
    Example demonstrating hierarchical context usage

Authors: ["Andreas Häberle"]
"""

import tempfile
import shutil
from pathlib import Path
from hands_scaphoid import Directory, File, Archive


def main():
    """Demonstrate hierarchical context usage."""
    print("=== Hierarchical Context Manager Example ===\n")
    
    # Create a temporary directory for the example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Working in temporary directory: {temp_path}\n")
        
        # Example 1: Basic hierarchical directory and file operations
        print("1. Basic hierarchical operations:")
        with Directory(temp_path / 'home') as home:
            print(f"   Created and entered: {home.get_current_path()}")
            
            with Directory('project') as project:
                print(f"   Created and entered: {project.get_current_path()}")
                
                with File('README.md') as readme:
                    print(f"   Created file: {readme.resolve_path()}")
                    readme.add_heading('My Project')
                    readme.add_line('This is a sample project.')
                    readme.add_heading('Contributing', level=2)
                    readme.add_line('Please follow our contribution guidelines.')
                    print(f"   Added content to README.md")
                
                # Create another file
                with File('main.py') as main_file:
                    print(f"   Created file: {main_file.resolve_path()}")
                    main_file.add_line('#!/usr/bin/env python3')
                    main_file.add_line('"""Main module."""')
                    main_file.add_line('')
                    main_file.add_line('def main():')
                    main_file.add_line('    print("Hello, World!")')
                    main_file.add_line('')
                    main_file.add_line('if __name__ == "__main__":')
                    main_file.add_line('    main()')
                    print(f"   Added content to main.py")
        
        print()
        
        # Example 2: Archive operations
        print("2. Archive operations:")
        with Directory(temp_path / 'home') as home:
            # Create an archive of the project
            with Archive(source='project', target='project_backup.zip') as archive:
                print(f"   Created archive: {archive.resolve_path()}")
                
                # The archive automatically includes the source directory
                contents = archive.list_contents()
                print(f"   Archive contents: {contents}")
                
                # Add an additional file
                archive.add_file('project/README.md', 'docs/README.md')
                print(f"   Added additional file to archive")
        
        print()
        
        # Example 3: More complex nested operations
        print("3. Complex nested operations:")
        with Directory(temp_path / 'workspace') as workspace:
            print(f"   Working in: {workspace.get_current_path()}")
            
            # Create multiple project directories
            for project_name in ['project1', 'project2', 'project3']:
                with Directory(project_name) as proj:
                    print(f"   Created project: {proj.get_current_path()}")
                    
                    # Create some files
                    with File('config.json') as config:
                        config.write_content('{\n  "name": "' + project_name + '",\n  "version": "1.0.0"\n}')
                    
                    with File('notes.txt') as notes:
                        notes.add_line(f'Notes for {project_name}')
                        notes.add_line('=' * (10 + len(project_name)))
                        notes.add_line('')
                        notes.add_line('This project contains important work.')
            
            # Create archives for each project
            for project_name in ['project1', 'project2', 'project3']:
                archive_name = f'{project_name}_backup.tar.gz'
                with Archive(source=project_name, target=archive_name, archive_type='tar.gz') as archive:
                    print(f"   Created archive: {archive.resolve_path()}")
                    
                    # Get archive info
                    info = archive.get_archive_info()
                    print(f"   Archive info: {info['file_count']} files, {info['size']} bytes")
        
        print()
        
        # Example 4: Reading and modifying existing files
        print("4. Reading and modifying existing files:")
        with Directory(temp_path / 'home' / 'project') as project:
            with File('README.md') as readme:
                content = readme.read_content()
                print(f"   Current README.md content:")
                print("   " + "\n   ".join(content.split('\n')[:5]) + "...")
                
                # Add more content
                readme.add_heading('Installation', level=2)
                readme.add_line('To install this project:')
                readme.add_line('1. Clone the repository')
                readme.add_line('2. Install dependencies')
                readme.add_line('3. Run the application')
                print(f"   Added installation section")
        
        print()
        
        # Show final directory structure
        print("5. Final directory structure:")
        def show_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            items = sorted(path.iterdir()) if path.exists() else []
            for i, item in enumerate(items):
                is_last = i == len(items) - 1
                current_prefix = "└── " if is_last else "├── "
                print(f"{prefix}{current_prefix}{item.name}")
                
                if item.is_dir() and current_depth < max_depth - 1:
                    next_prefix = prefix + ("    " if is_last else "│   ")
                    show_tree(item, next_prefix, max_depth, current_depth + 1)
        
        print(f"   {temp_path}/")
        show_tree(temp_path, "   ")


if __name__ == "__main__":
    main()