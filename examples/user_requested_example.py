#!/usr/bin/env python3
"""
Simple example matching the user's requested usage pattern.

This example demonstrates the exact usage pattern specified by the user.

File:
    name: user_requested_example.py
    date: 2025-09-16

Description:
    Example matching the user's requested usage pattern

Authors: ["Andreas Häberle"]
"""

import tempfile
from pathlib import Path
from hands_scaphoid import Directory, File, Archive


def main():
    """Demonstrate the exact usage pattern requested by the user."""
    print("=== User Requested Example ===\n")
    
    # Create a temporary directory for the example to work in a safe space
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Working in temporary directory: {temp_path}\n")
        
        # Change to the temp directory to simulate starting from a clean state
        import os
        original_cwd = os.getcwd()
        os.chdir(temp_path)
        
        try:
            # Create a home directory structure first
            home_path = temp_path / 'home'
            home_path.mkdir(exist_ok=True)
            
            # Now run the exact example from the user's request
            print("Running the user's requested example:")
            print()
            
            with DirectoryObject('home') as home:
                print(f"Entered directory: {home.get_current_path()}")
                
                with DirectoryObject('project') as project:
                    print(f"Entered project directory: {project.get_current_path()}")
                    
                    with FileObject('README.md') as readme:
                        print(f"Opened file: {readme.resolve_path()}")
                        readme.add_heading('Contributing')
                        print("Added 'Contributing' heading to README.md")
                
                with ArchiveFile(source='project') as archive:
                    print(f"Created archive: {archive.resolve_path()}")
                    archive.add_directory('project')
                    print("Added 'project' directory to archive")
            
            print()
            print("Example completed successfully!")
            
            # Show what was created
            print("\nFiles created:")
            for item in temp_path.rglob('*'):
                if item.is_file():
                    rel_path = item.relative_to(temp_path)
                    print(f"  {rel_path}")
                    
                    # Show content of text files
                    if item.suffix in ['.md', '.txt']:
                        try:
                            content = item.read_text()
                            print(f"    Content: {repr(content[:100])}")
                        except Exception:
                            pass
        
        finally:
            # Restore original working directory
            os.chdir(original_cwd)


if __name__ == "__main__":
    main()