#!/usr/bin/env python3
"""
Example usage of the hierarchical context managers with separated architecture.

This example demonstrates how to use the DirectoryContext, FileContext, and ArchiveContext classes
with nested context managers to perform file system operations, as well as direct operations
using the File, Directory, and Archive classes.

File:
    name: hierarchical_context_example.py
    date: 2025-09-16

Description:
    Example demonstrating hierarchical context usage with separated architecture

Authors: ["Andreas Häberle"]
"""

import tempfile
import shutil
from pathlib import Path
from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import File, Directory, Archive


def main():
    """Demonstrate hierarchical context usage with the new separated architecture."""
    print("=== Hierarchical Context Manager Example (Separated Architecture) ===\n")
    
    # Create a temporary directory for the example
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Working in temporary directory: {temp_path}\n")
        
        # Example 1: Basic hierarchical directory and file operations with context managers
        print("1. Context Manager approach - Hierarchical operations:")
        with DirectoryContext(temp_path / 'home', create=True) as home:
            print(f"   Created and entered: {home.resolve_path()}")
            
            with DirectoryContext('project', create=True) as project:
                print(f"   Created and entered: {project.resolve_path()}")
                
                with FileContext('README.md', create=True) as readme:
                    print(f"   Created file: {readme.resolve_path()}")
                    readme.write_content('# My Project')\
                          .append_line('')\
                          .append_line('This is a sample project.')\
                          .add_heading('Contributing')\
                          .append_line('Please follow our contribution guidelines.')
                    print(f"   Added content to README.md")
                
                # Create another file
                with FileContext('main.py', create=True) as main_file:
                    print(f"   Created file: {main_file.resolve_path()}")
                    main_file.write_content('#!/usr/bin/env python3')\
                             .append_line('"""Main module."""')\
                             .append_line('')\
                             .append_line('def main():')\
                             .append_line('    print("Hello, World!")')\
                             .append_line('')\
                             .append_line('if __name__ == "__main__":')\
                             .append_line('    main()')
                    print(f"   Added content to main.py")
        
        print()
        
        # Example 2: Direct operations approach (no context managers)
        print("2. Direct Operations approach - Same functionality without context:")
        
        # Create directory structure directly
        direct_project_path = temp_path / 'direct_project'
        Directory.create_directory(direct_project_path)
        print(f"   Created directory: {direct_project_path}")
        
        # Create files directly
        readme_path = direct_project_path / 'README.md'
        File.create_file(readme_path, '# Direct Project')
        File.append_line(readme_path, '')
        File.append_line(readme_path, 'Created using direct operations.')
        File.add_heading(readme_path, 'Features')
        File.append_line(readme_path, '- Direct file operations')
        File.append_line(readme_path, '- No context management overhead')
        print(f"   Created file: {readme_path}")
        
        main_path = direct_project_path / 'main.py'
        File.create_file(main_path, '''#!/usr/bin/env python3
"""Direct operations main module."""

def main():
    print("Hello from direct operations!")

if __name__ == "__main__":
    main()''')
        print(f"   Created file: {main_path}")
        
        print()
        
        # Example 3: Archive operations - both approaches
        print("3. Archive operations - Context vs Direct:")
        
        # Context manager approach
        with DirectoryContext(temp_path / 'home') as home:
            with ArchiveContext(source='project', target='project_backup.zip') as archive:
                print(f"   [Context] Created archive: {archive.resolve_path()}")
                
                contents = archive.list_contents()
                print(f"   [Context] Archive contents: {len(contents)} items")
                
                # Add an additional file
                archive.add_file(temp_path / 'home' / 'project' / 'README.md', 'docs/README.md')
                print(f"   [Context] Added additional file to archive")
        
        # Direct operations approach
        direct_archive_path = temp_path / 'direct_backup.zip'
        Archive.create_zip_archive(direct_archive_path, direct_project_path)
        print(f"   [Direct] Created archive: {direct_archive_path}")
        
        direct_contents = Archive.list_archive_contents(direct_archive_path)
        print(f"   [Direct] Archive contents: {len(direct_contents)} items")
        
        print()
        
        # Example 4: Complex nested operations with method chaining
        print("4. Complex nested operations with method chaining:")
        with DirectoryContext(temp_path / 'workspace', create=True) as workspace:
            print(f"   Working in: {workspace.resolve_path()}")
            
            # Create multiple project directories
            for project_name in ['project1', 'project2', 'project3']:
                with DirectoryContext(project_name, create=True) as proj:
                    print(f"   Created project: {proj.resolve_path()}")
                    
                    # Create config file with method chaining
                    with FileContext('config.json', create=True) as config:
                        config.write_content('{')\
                              .append_line(f'  "name": "{project_name}",')\
                              .append_line('  "version": "1.0.0",')\
                              .append_line('  "type": "sample"')\
                              .append_line('}')
                    
                    # Create notes with method chaining
                    with FileContext('notes.txt', create=True) as notes:
                        notes.write_content(f'Notes for {project_name}')\
                             .append_line('=' * (10 + len(project_name)))\
                             .append_line('')\
                             .add_heading('Overview')\
                             .append_line('This project contains important work.')\
                             .append_line('')\
                             .add_heading('Status')\
                             .append_line('In development')
            
            # Create archives for each project using context managers
            for project_name in ['project1', 'project2', 'project3']:
                archive_name = f'{project_name}_backup.tar.gz'
                with ArchiveContext(source=project_name, target=archive_name, archive_type='tar.gz') as archive:
                    print(f"   Created TAR.GZ archive: {archive.resolve_path()}")
                    
                    # Get archive info
                    info = archive.get_archive_info()
                    print(f"   Archive info: {info.get('file_count', 0)} files")
        
        print()
        
        # Example 5: Comparing approaches - reading and modifying files
        print("5. Comparing approaches - reading and modifying files:")
        
        # Context manager approach
        print("   [Context Manager approach]:")
        with DirectoryContext(temp_path / 'home' / 'project') as project:
            with FileContext('README.md') as readme:
                content = readme.read_content()
                print(f"   Current README.md length: {len(content)} characters")
                
                # Add more content with method chaining
                readme.add_heading('Installation')\
                      .append_line('To install this project:')\
                      .append_line('1. Clone the repository')\
                      .append_line('2. Install dependencies')\
                      .append_line('3. Run the application')\
                      .add_heading('Usage')\
                      .append_line('```python')\
                      .append_line('from myproject import main')\
                      .append_line('main()')\
                      .append_line('```')
                print(f"   Added installation and usage sections")
        
        # Direct operations approach
        print("   [Direct Operations approach]:")
        direct_readme = direct_project_path / 'README.md'
        content = File.read_content(direct_readme)
        print(f"   Current README.md length: {len(content)} characters")
        
        File.add_heading(direct_readme, 'Installation')
        File.append_line(direct_readme, 'To install this project:')
        File.append_line(direct_readme, '1. Clone the repository')
        File.append_line(direct_readme, '2. Install dependencies')
        File.append_line(direct_readme, '3. Run the application')
        print(f"   Added installation section")
        
        print()
        
        # Example 6: Global functions with context managers
        print("6. Global functions approach:")
        with DirectoryContext(temp_path / 'global_example', create=True, enable_globals=True) as global_ctx:
            print(f"   Working in: {global_ctx.resolve_path()}")
            
            # Now we can use global functions (uncomment if globals are implemented)
            # create_file('global_test.txt', 'Created with global functions!')
            # create_directory('subdir')
            # change_directory('subdir')
            # create_file('nested_file.txt', 'Nested file content')
            
            # For now, use the context methods
            global_ctx.create_file('global_test.txt', 'Created with context methods!')
            global_ctx.create_directory('subdir')
            
            print(f"   Created files using context methods")
        
        print()
        
        # Show final directory structure
        print("7. Final directory structure:")
        def show_tree(path, prefix="", max_depth=3, current_depth=0):
            if current_depth >= max_depth:
                return
            
            try:
                items = sorted(path.iterdir()) if path.exists() and path.is_dir() else []
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    item_name = item.name
                    if item.is_dir():
                        item_name += "/"
                    elif item.suffix in ['.zip', '.tar', '.gz']:
                        # Show archive info
                        try:
                            if Archive.is_archive_file(item):
                                info = Archive.archive_info(item)
                                item_name += f" ({info.get('file_count', 0)} files)"
                        except:
                            pass
                    
                    print(f"{prefix}{current_prefix}{item_name}")
                    
                    if item.is_dir() and current_depth < max_depth - 1:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        show_tree(item, next_prefix, max_depth, current_depth + 1)
            except PermissionError:
                pass
        
        print(f"   {temp_path.name}/")
        show_tree(temp_path, "   ")
        
        print()
        print("=== Summary ===")
        print("This example demonstrated:")
        print("• Context managers (DirectoryContext, FileContext, ArchiveContext) for hierarchical operations")
        print("• Direct operations (File, Directory, Archive) for simple tasks")
        print("• Method chaining for fluent interfaces")
        print("• Archive operations with different formats")
        print("• File reading and modification")
        print("• Both approaches achieve the same results with different trade-offs:")
        print("  - Context managers: Better for hierarchical operations, automatic path resolution")
        print("  - Direct operations: Lower overhead, more explicit control")


if __name__ == "__main__":
    main()