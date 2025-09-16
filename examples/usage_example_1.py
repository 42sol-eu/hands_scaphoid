#!/usr/bin/env python3
"""
Basic usage example for Hands Scaphoid - File System Operations

This example shows the basic usage patterns for file, directory, and archive operations
using both context managers and direct operations.
"""

from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import File, Directory, Archive
from pathlib import Path
import tempfile

def main():
    """Demonstrate basic usage patterns."""
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        print(f"Working in: {temp_path}\n")
        
        # === CONTEXT MANAGER APPROACH ===
        print("=== Context Manager Approach ===")
        
        # Basic file operations with context
        with DirectoryContext(temp_path / 'context_example', create=True) as ctx:
            print(f"Created directory: {ctx.resolve_path()}")
            
            # Create a file with context manager
            with FileContext('hello.txt', create=True) as f:
                f.write_content('Hello, World!')
                f.append_line('This is created with context managers.')
                print(f"Created file: {f.resolve_path()}")
            
            # Read the file back
            with FileContext('hello.txt') as f:
                content = f.read_content()
                print(f"File content: {content}")
        
        print()
        
        # === DIRECT OPERATIONS APPROACH ===
        print("=== Direct Operations Approach ===")
        
        # Basic file operations without context
        direct_dir = temp_path / 'direct_example'
        Directory.create_directory(direct_dir)
        print(f"Created directory: {direct_dir}")
        
        # Create a file directly
        hello_file = direct_dir / 'hello.txt'
        File.write_content(hello_file, 'Hello, World!')
        File.append_line(hello_file, 'This is created with direct operations.')
        print(f"Created file: {hello_file}")
        
        # Read the file back
        content = File.read_content(hello_file)
        print(f"File content: {content}")
        
        print()
        
        # === HIERARCHICAL OPERATIONS ===
        print("=== Hierarchical Operations ===")
        
        with DirectoryContext(temp_path / 'project', create=True) as project:
            # Create nested structure
            with DirectoryContext('src', create=True) as src:
                with FileContext('main.py', create=True) as main:
                    main.write_content('#!/usr/bin/env python3')\
                        .append_line('print("Hello from hierarchical context!")')
                
            with DirectoryContext('docs', create=True) as docs:
                with FileContext('README.md', create=True) as readme:
                    readme.write_content('# My Project')\
                          .add_heading('Description')\
                          .append_line('This project demonstrates hierarchical file operations.')
            
            # List project contents
            contents = project.list_contents()
            print(f"Project contains: {contents}")
        
        print()
        
        # === ARCHIVE OPERATIONS ===
        print("=== Archive Operations ===")
        
        # Create an archive of our project
        with ArchiveContext(source=temp_path / 'project', target=temp_path / 'project.zip') as archive:
            contents = archive.list_contents()
            print(f"Archive created with {len(contents)} items")
            
            # Add an extra file to the archive
            extra_file = temp_path / 'extra.txt'
            File.write_content(extra_file, 'Extra file content')
            archive.add_file(extra_file, 'extra.txt')
            print("Added extra file to archive")
        
        # Extract to a new location
        with ArchiveContext(target=temp_path / 'project.zip') as archive:
            archive.extract_all(temp_path / 'extracted')
            print(f"Extracted archive to: {temp_path / 'extracted'}")
        
        print()
        
        # === COMPARISON OF APPROACHES ===
        print("=== Method Chaining vs Step-by-step ===")
        
        # Method chaining approach
        with DirectoryContext(temp_path / 'chaining', create=True) as chain_dir:
            with FileContext('report.txt', create=True) as report:
                report.write_content('Monthly Report')\
                      .add_heading('Summary')\
                      .append_line('Sales: $10,000')\
                      .append_line('Expenses: $3,000')\
                      .add_heading('Details')\
                      .append_line('This month showed strong performance.')
                print("Created report with method chaining")
        
        # Step-by-step approach
        step_dir = temp_path / 'step_by_step'
        Directory.create_directory(step_dir)
        
        report_file = step_dir / 'report.txt'
        File.write_content(report_file, 'Monthly Report')
        File.add_heading(report_file, 'Summary')
        File.append_line(report_file, 'Sales: $10,000')
        File.append_line(report_file, 'Expenses: $3,000')
        File.add_heading(report_file, 'Details')
        File.append_line(report_file, 'This month showed strong performance.')
        print("Created report step-by-step")
        
        # Both approaches create identical files
        chain_content = File.read_content(temp_path / 'chaining' / 'report.txt')
        step_content = File.read_content(report_file)
        print(f"Both approaches create identical content: {chain_content == step_content}")
        
        print()
        print("=== Summary ===")
        print("Context managers provide:")
        print("• Automatic path resolution in hierarchical structures")
        print("• Method chaining for fluent interfaces")
        print("• Automatic cleanup and error handling")
        print()
        print("Direct operations provide:")
        print("• Lower overhead for simple operations")
        print("• More explicit control over paths")
        print("• Easier integration with existing code")

if __name__ == "__main__":
    main()