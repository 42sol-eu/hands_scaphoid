#!/usr/bin/env python3
"""
Enhanced example demonstrating all the features of the separated architecture.

This example shows:
1. Rich console output
2. Archive context manager with different archive types  
3. Direct operations vs context managers
4. Method chaining and fluent interfaces
5. Dry-run feature
6. Error handling

File:
    name: enhanced_features_example.py
    date: 2025-09-16

Description:
    Example demonstrating enhanced features with separated architecture

Authors: ["Andreas Häberle"]
"""

import tempfile
from pathlib import Path
from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import Directory, File, Archive


def main():
    """Demonstrate the enhanced features."""
    from rich.console import Console
    console = Console()
    
    console.print("\n[bold green]Enhanced Features Demo - Separated Architecture[/bold green]\n")
    
    # Create a temporary directory for our examples
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        console.print(f"Working in: [cyan]{temp_path}[/cyan]\n")
        
        # === 1. RICH CONSOLE OUTPUT ===
        console.print("[bold blue]1. Rich Console Output[/bold blue]")
        console.print("All operations provide colored console feedback!")
        
        with DirectoryContext(temp_path / 'rich_demo', create=True) as demo:
            with FileContext('demo.txt', create=True) as f:
                f.write_content('Demo content with rich output!')
        
        console.print()
        
        # === 2. MULTIPLE ARCHIVE FORMATS ===
        console.print("[bold blue]2. Multiple Archive Formats[/bold blue]")
        
        # Create some content to archive
        with DirectoryContext(temp_path / 'archive_source', create=True) as source:
            source.create_file('file1.txt', 'Content of file 1')
            source.create_file('file2.txt', 'Content of file 2')
            source.create_directory('subdir')
            with DirectoryContext('subdir') as subdir:
                subdir.create_file('nested.txt', 'Nested file content')
        
        # Create different archive formats
        formats = [
            ('demo.zip', 'zip'),
            ('demo.tar', 'tar'),
            ('demo.tar.gz', 'tar.gz'),
            ('demo.tar.bz2', 'tar.bz2')
        ]
        
        for archive_name, archive_type in formats:
            console.print(f"Creating [yellow]{archive_type}[/yellow] archive...")
            with ArchiveContext(
                source=temp_path / 'archive_source', 
                target=temp_path / archive_name,
                archive_type=archive_type
            ) as archive:
                contents = archive.list_contents()
                info = archive.get_archive_info()
                console.print(f"  Archive: [cyan]{archive_name}[/cyan] ({len(contents)} files)")
                if 'compression_ratio' in info:
                    console.print(f"  Compression ratio: [green]{info['compression_ratio']:.2f}[/green]")
        
        console.print()
        
        # === 3. DIRECT OPERATIONS VS CONTEXT MANAGERS ===
        console.print("[bold blue]3. Direct Operations vs Context Managers[/bold blue]")
        
        # Direct operations - good for simple tasks
        console.print("[yellow]Direct Operations:[/yellow]")
        direct_dir = temp_path / 'direct_ops'
        Directory.create_directory(direct_dir)
        
        file_path = direct_dir / 'direct_file.txt'
        File.write_content(file_path, 'Created with direct operations')
        File.append_line(file_path, 'Line 2')
        File.append_line(file_path, 'Line 3')
        
        files = Directory.list_contents(direct_dir)
        console.print(f"  Created directory with files: {files}")
        
        # Context managers - good for hierarchical operations
        console.print("[yellow]Context Managers:[/yellow]")
        with DirectoryContext(temp_path / 'context_ops', create=True) as ctx_dir:
            with FileContext('context_file.txt', create=True) as f:
                f.write_content('Created with context managers')\
                 .append_line('Line 2')\
                 .append_line('Line 3')
            
            files = ctx_dir.list_contents()
            console.print(f"  Created directory with files: {files}")
        
        console.print()
        
        # === 4. METHOD CHAINING ===
        console.print("[bold blue]4. Method Chaining and Fluent Interfaces[/bold blue]")
        
        with DirectoryContext(temp_path / 'chaining_demo', create=True) as demo:
            # Complex file creation with method chaining
            with FileContext('complex_file.md', create=True) as f:
                f.write_content('# Complex Document')\
                 .append_line('')\
                 .add_heading('Introduction')\
                 .append_line('This document demonstrates method chaining.')\
                 .append_line('')\
                 .add_heading('Features')\
                 .append_line('- Method chaining for fluent interfaces')\
                 .append_line('- Rich console output')\
                 .append_line('- Multiple archive formats')\
                 .append_line('')\
                 .add_heading('Conclusion')\
                 .append_line('Method chaining makes code more readable.')
            
            console.print("Created complex document with [green]method chaining[/green]")
            
            # Read and display content
            with FileContext('complex_file.md') as f:
                content = f.read_content()
                lines = len(content.split('\n'))
                console.print(f"Document has [cyan]{lines}[/cyan] lines")
        
        console.print()
        
        # === 5. DRY-RUN FEATURE ===
        console.print("[bold blue]5. Dry-Run Feature[/bold blue]")
        
        console.print("[yellow]Dry-run mode (no actual changes):[/yellow]")
        with DirectoryContext(temp_path / 'dry_run_test', create=True, dry_run=True) as dry_ctx:
            dry_ctx.create_directory('should_not_exist')
            dry_ctx.create_file('should_not_exist.txt', 'This should not be created')
            
            with FileContext('dry_file.txt', create=True, dry_run=True) as dry_f:
                dry_f.write_content('Dry run content')\
                     .append_line('This line should not be written')
        
        # Check if files were actually created (they shouldn't be)
        dry_test_path = temp_path / 'dry_run_test'
        if dry_test_path.exists():
            console.print("[red]ERROR: Dry-run created actual files![/red]")
        else:
            console.print("[green]✓ Dry-run mode working correctly - no files created[/green]")
        
        console.print()
        
        # === 6. ERROR HANDLING ===
        console.print("[bold blue]6. Error Handling[/bold blue]")
        
        # Demonstrate graceful error handling
        console.print("[yellow]Testing error handling:[/yellow]")
        
        try:
            # Try to read a non-existent file
            File.read_content(temp_path / 'nonexistent.txt')
        except FileNotFoundError:
            console.print("[green]✓ FileNotFoundError handled correctly[/green]")
        
        try:
            # Try to create archive from non-existent source
            Archive.create_zip_archive(temp_path / 'bad.zip', temp_path / 'nonexistent')
        except (FileNotFoundError, Exception) as e:
            console.print(f"[green]✓ Archive error handled: {type(e).__name__}[/green]")
        
        try:
            # Try to list contents of non-existent directory
            Directory.list_contents(temp_path / 'nonexistent')
        except FileNotFoundError:
            console.print("[green]✓ Directory error handled correctly[/green]")
        
        console.print()
        
        # === 7. ARCHIVE EXTRACTION AND MANIPULATION ===
        console.print("[bold blue]7. Archive Extraction and Manipulation[/bold blue]")
        
        # Create a selective archive
        with ArchiveContext(target=temp_path / 'selective.zip') as selective:
            selective.add_file(temp_path / 'direct_ops' / 'direct_file.txt', 'files/direct.txt')
            selective.add_file(temp_path / 'context_ops' / 'context_file.txt', 'files/context.txt')
            
            contents = selective.list_contents()
            console.print(f"Selective archive contains: [cyan]{contents}[/cyan]")
        
        # Extract to different location
        with ArchiveContext(target=temp_path / 'selective.zip') as selective:
            selective.extract_all(temp_path / 'extracted')
            console.print(f"Extracted to: [cyan]{temp_path / 'extracted'}[/cyan]")
        
        console.print()
        
        # === 8. PERFORMANCE COMPARISON ===
        console.print("[bold blue]8. Performance Comparison[/bold blue]")
        
        import time
        
        # Time direct operations
        start_time = time.time()
        for i in range(10):
            test_file = temp_path / f'perf_direct_{i}.txt'
            File.write_content(test_file, f'Performance test file {i}')
            File.append_line(test_file, 'Additional line')
        direct_time = time.time() - start_time
        
        # Time context operations
        start_time = time.time()
        with DirectoryContext(temp_path, create=False) as perf_ctx:
            for i in range(10):
                with FileContext(f'perf_context_{i}.txt', create=True) as f:
                    f.write_content(f'Performance test file {i}')\
                     .append_line('Additional line')
        context_time = time.time() - start_time
        
        console.print(f"Direct operations: [green]{direct_time:.4f}s[/green]")
        console.print(f"Context operations: [green]{context_time:.4f}s[/green]")
        console.print(f"Overhead: [yellow]{((context_time / direct_time - 1) * 100):.1f}%[/yellow]")
        
        console.print()
        
        # === 9. FINAL DIRECTORY TREE ===
        console.print("[bold blue]9. Final Directory Structure[/bold blue]")
        
        def show_tree(path, prefix="", max_depth=2, current_depth=0):
            if current_depth >= max_depth:
                return
            
            try:
                items = sorted(path.iterdir()) if path.exists() and path.is_dir() else []
                for i, item in enumerate(items):
                    is_last = i == len(items) - 1
                    current_prefix = "└── " if is_last else "├── "
                    
                    item_name = item.name
                    if item.is_dir():
                        item_name = f"[blue]{item_name}/[/blue]"
                    elif item.suffix in ['.zip', '.tar', '.gz', '.bz2']:
                        item_name = f"[magenta]{item_name}[/magenta]"
                    elif item.suffix in ['.txt', '.md']:
                        item_name = f"[green]{item_name}[/green]"
                    
                    console.print(f"{prefix}{current_prefix}{item_name}")
                    
                    if item.is_dir() and current_depth < max_depth - 1:
                        next_prefix = prefix + ("    " if is_last else "│   ")
                        show_tree(item, next_prefix, max_depth, current_depth + 1)
            except PermissionError:
                pass
        
        console.print(f"[cyan]{temp_path.name}/[/cyan]")
        show_tree(temp_path, "")
        
        console.print("\n[bold green]Demo completed! 🎉[/bold green]")
        console.print("\n[bold]Summary of demonstrated features:[/bold]")
        console.print("• Rich console output with colors and formatting")
        console.print("• Multiple archive formats (ZIP, TAR, TAR.GZ, TAR.BZ2)")
        console.print("• Direct operations for simple tasks")
        console.print("• Context managers for hierarchical operations")
        console.print("• Method chaining for fluent interfaces")
        console.print("• Dry-run mode for testing")
        console.print("• Comprehensive error handling")
        console.print("• Archive creation, manipulation, and extraction")
        console.print("• Performance comparison between approaches")


if __name__ == "__main__":
    main()