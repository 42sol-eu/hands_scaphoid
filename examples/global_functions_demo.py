#!/usr/bin/env python3
"""
Example demonstrating context manager usage with separated architecture.

This example shows how to use the DirectoryContext, FileContext, and ArchiveContext
with the new separated architecture design.
"""

import sys
from pathlib import Path

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import Directory, File, Archive


def demo_context_managers():
    """Demonstrate context managers with the new separated architecture."""
    print("=== Context Manager Demo ===")
    
    # Directory context
    print("\n1. Directory context operations:")
    with DirectoryContext("test_dir", create=True) as dir_ctx:
        print("  - Listing contents...")
        dir_ctx.list_contents()
        print("  - Creating subdirectory...")
        dir_ctx.create_directory("subdir")
        print("  - Listing contents again...")
        dir_ctx.list_contents()
        print("  ✅ Directory context working!")
    
    # File context
    print("\n2. File context operations:")
    with FileContext("test_dir/example.txt", create=True) as file_ctx:
        print("  - Appending line...")
        file_ctx.append_line("Hello from context managers!")
        print("  - Appending another line...")
        file_ctx.append_line("This is written using context management.")
        print("  - Adding heading...")
        file_ctx.add_heading("Context Managers")
        print("  - Writing content...")
        file_ctx.write_content("Content added via context manager.")
        print("  ✅ File context working!")
    
    # Archive context
    print("\n3. Archive context operations:")
    with ArchiveContext(target="test_archive.zip") as archive_ctx:
        print("  - Adding file...")
        archive_ctx.add_file("test_dir/example.txt", "example.txt")
        print("  - Adding directory...")
        archive_ctx.add_directory("test_dir", "test_directory")
        print("  - Listing contents...")
        contents = archive_ctx.list_contents()
        print(f"    Archive contains: {contents}")
        print("  ✅ Archive context working!")


def demo_direct_operations():
    """Demonstrate direct operations without context managers."""
    print("\n=== Direct Operations Demo ===")
    
    print("\n1. Direct directory operations:")
    Directory.create_directory("direct_test")
    Directory.create_directory("direct_test/subdir")
    files = Directory.list_contents("direct_test")
    print(f"  - Created directory with contents: {files}")
    
    print("\n2. Direct file operations:")
    File.write_content("direct_test/direct_file.txt", "Direct operations content")
    File.append_line("direct_test/direct_file.txt", "Additional line")
    content = File.read_content("direct_test/direct_file.txt")
    print(f"  - File content: {repr(content[:50])}...")
    
    print("\n3. Direct archive operations:")
    Archive.create_zip_archive("direct_archive.zip", "direct_test")
    contents = Archive.list_archive_contents("direct_archive.zip")
    print(f"  - Archive contents: {contents}")
    print("  ✅ Direct operations working!")


def demo_nested_contexts():
    """Demonstrate nested contexts with the new architecture."""
    print("\n=== Nested Contexts Demo ===")
    
    with DirectoryContext("nested_test", create=True) as dir_ctx:
        print("In directory context...")
        dir_ctx.list_contents()
        
        with FileContext("outer_file.txt", create=True) as file_ctx:
            print("In file context (nested)...")
            file_ctx.append_line("Outer file content")
            
        # Back to directory context
        print("Back in directory context...")
        dir_ctx.create_directory("nested_dir")
        
        with ArchiveContext(target="nested.zip") as archive_ctx:
            print("In archive context (nested)...")
            archive_ctx.add_file("outer_file.txt", "outer.txt")
            contents = archive_ctx.list_contents()
            print(f"    Archive contents: {contents}")
            
        print("Back in directory context...")
        final_contents = dir_ctx.list_contents()
        print(f"  Final directory contents: {final_contents}")
        print("  ✅ Nested contexts working!")


def demo_dry_run_mode():
    """Demonstrate dry-run mode with the new architecture."""
    print("\n=== Dry-Run Mode Demo ===")
    
    print("\n1. Dry-run directory operations:")
    with DirectoryContext("dry_run_test", create=True, dry_run=True) as dir_ctx:
        print("  - Creating subdirectory in dry-run mode...")
        dir_ctx.create_directory("would_create")
        print("  - Listing contents in dry-run mode...")
        dir_ctx.list_contents()
    
    print("\n2. Dry-run file operations:")
    with FileContext("dry_run_file.txt", create=True, dry_run=True) as file_ctx:
        print("  - Writing content in dry-run mode...")
        file_ctx.write_content("This would be written in dry-run mode")
        print("  - Adding heading in dry-run mode...")
        file_ctx.add_heading("Dry Run Heading")
        
    print("  ✅ Dry-run mode working!")


def demo_method_chaining():
    """Demonstrate method chaining with the new architecture."""
    print("\n=== Method Chaining Demo ===")
    
    with DirectoryContext("chaining_test", create=True) as dir_ctx:
        # Method chaining with file operations
        with FileContext("chained_file.txt", create=True) as file_ctx:
            file_ctx.write_content("Starting content")\
                    .append_line("Chained line 1")\
                    .append_line("Chained line 2")\
                    .add_heading("Chained Heading")\
                    .append_line("After heading")
            
            content = file_ctx.read_content()
            lines = len(content.split('\n'))
            print(f"  - Created file with {lines} lines using method chaining")
        
        dir_contents = dir_ctx.list_contents()
        print(f"  - Directory contents: {dir_contents}")
        print("  ✅ Method chaining working!")


if __name__ == "__main__":
    print("Context Manager Demonstration (Separated Architecture)")
    print("====================================================")
    
    try:
        demo_context_managers()
        demo_direct_operations()
        demo_nested_contexts()
        demo_dry_run_mode()
        demo_method_chaining()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Context managers with separated architecture")
        print("✅ Direct operations without context overhead")
        print("✅ Nested contexts with proper scope management")
        print("✅ Dry-run mode for testing operations")
        print("✅ Method chaining for fluent interfaces")
        print("\nNote: The separated architecture provides both context managers")
        print("and direct operations for maximum flexibility.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test files
        import shutil
        test_paths = ["test_dir", "test_archive.zip", "direct_test", 
                     "direct_archive.zip", "nested_test", "nested.zip", 
                     "chaining_test"]
        for path in test_paths:
            path_obj = Path(path)
            if path_obj.exists():
                if path_obj.is_dir():
                    shutil.rmtree(path_obj)
                else:
                    path_obj.unlink()
        print("\n🧹 Cleanup completed.")