#!/usr/bin/env python3
"""
Example demonstrating global function access and ShellContext integration for Windows.

This example shows how to use the File, Directory, and Archive contexts
with global function access and integration with ShellContext on Windows.
"""

import sys
from pathlib import Path

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from hands_scaphoid.Directory import Directory
from hands_scaphoid.File import File
from hands_scaphoid.Archive import Archive
from hands_scaphoid.ShellContext import ShellContext


def demo_global_functions():
    """Demonstrate global function access without object prefixes."""
    print("\n=== Global Function Access Demo ===")
    
    # Directory context with global functions
    print("\n1. Directory context with global functions:")
    with Directory("test_dir", create=True, enable_globals=True):
        # These functions are now available globally without the object prefix
        list_contents()  # Instead of dir_context.list_contents()
        create_subdirectory("subdir")
        list_contents()
        print("✅ Directory global functions working!")
    
    # File context with global functions
    print("\n2. File context with global functions:")
    with File("test_dir/example.txt", create=True, enable_globals=True):
        write_line("Hello from global functions!")
        write_line("This is written using global access.")
        add_heading("Global Functions")
        write_content("Content added via global function access.")
        print("✅ File global functions working!")
    
    # Archive context with global functions
    print("\n3. Archive context with global functions:")
    with Archive("test_archive.zip", create=True, enable_globals=True):
        add_file("test_dir/example.txt", "example.txt")
        add_directory("test_dir", "test_directory")
        list_contents()
        print("✅ Archive global functions working!")


def demo_shellcontext_integration():
    """Demonstrate integration with ShellContext (Windows compatible)."""
    print("\n=== ShellContext Integration Demo ===")
    
    # Using ShellContext alongside File/Directory contexts
    print("\n1. Combined usage with ShellContext (Windows commands):")
    with ShellContext() as shell:
        # Shell functions are available globally
        allow("dir")
        allow("type")
        allow("echo")
        
        # Use shell commands alongside file context
        with Directory("shell_test", create=True, enable_globals=True):
            # Both shell and directory functions available
            run("dir")  # Windows directory listing
            create_subdirectory("shell_created")  # Directory function
            
            with File("shell_file.txt", create=True, enable_globals=True):
                write_line("Created with mixed shell and file context")
                
            # Use shell to display the file (Windows type command)
            run("type shell_file.txt")
            print("✅ ShellContext integration working!")


def demo_nested_contexts():
    """Demonstrate nested contexts with global functions."""
    print("\n=== Nested Contexts Demo ===")
    
    with Directory("nested_test", create=True, enable_globals=True):
        print("In directory context...")
        list_contents()
        
        with File("outer_file.txt", create=True, enable_globals=True):
            print("In file context...")
            write_line("Outer file content")
            
            # Note: When contexts are nested, the inner context's globals take precedence
            # Directory functions are temporarily overridden by File functions
            
        # Back to directory context - directory functions available again
        print("Back in directory context...")
        create_subdirectory("nested_dir")
        
        with Archive("nested.zip", create=True, enable_globals=True):
            print("In archive context...")
            add_file("outer_file.txt", "outer.txt")
            list_contents()
            
        print("✅ Nested contexts working!")


def demo_dry_run_with_globals():
    """Demonstrate dry-run mode with global functions."""
    print("\n=== Dry-Run with Global Functions Demo ===")
    
    print("\n1. Dry-run directory operations:")
    with Directory("dry_run_test", create=True, dry_run=True, enable_globals=True):
        create_subdirectory("would_create")
        list_contents()  # Shows what would be listed
    
    print("\n2. Dry-run file operations:")
    with File("dry_run_file.txt", create=True, dry_run=True, enable_globals=True):
        write_line("This would be written in dry-run mode")
        add_heading("Dry Run Heading")
        
    print("✅ Dry-run with global functions working!")


def demo_standalone_vs_global():
    """Demonstrate the difference between standalone and global function usage."""
    print("\n=== Standalone vs Global Functions Demo ===")
    
    print("\n1. Standalone usage (without context):")
    # Create directory using standalone method
    Directory.create_directory("standalone_test")
    # Add file using standalone method
    File.write_file("standalone_test/standalone_file.txt", "Standalone content")
    # Create archive using standalone method
    Archive.create_archive("standalone.zip", "standalone_test")
    print("✅ Standalone methods working!")
    
    print("\n2. Global functions usage (within context):")
    with Directory("global_test", create=True, enable_globals=True):
        # Using global functions (no object prefix needed)
        create_subdirectory("global_subdir")
        list_contents()
        
        with File("global_file.txt", create=True, enable_globals=True):
            write_line("Global function content")
            add_heading("Global Functions")
            
        with Archive("global.zip", create=True, enable_globals=True):
            add_file("global_file.txt")
            list_contents()
            
    print("✅ Global functions working!")


if __name__ == "__main__":
    print("Global Functions and ShellContext Integration Example (Windows)")
    print("===============================================================")
    
    try:
        demo_global_functions()
        demo_shellcontext_integration()
        demo_nested_contexts()
        demo_dry_run_with_globals()
        demo_standalone_vs_global()
        
        print("\n🎉 All demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ Global function access (no object prefix needed)")
        print("✅ ShellContext integration with Windows commands")
        print("✅ Nested contexts with proper function scope")
        print("✅ Dry-run mode with global functions")
        print("✅ Standalone vs context-managed operations")
        print("\nNote: Global functions are automatically cleaned up when exiting contexts.")
        print("This prevents namespace pollution and ensures proper isolation.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test files
        import shutil
        test_paths = ["test_dir", "test_archive.zip", "shell_test", "nested_test", 
                     "nested.zip", "standalone_test", "standalone.zip", "global_test", "global.zip"]
        for path in test_paths:
            path_obj = Path(path)
            if path_obj.exists():
                if path_obj.is_dir():
                    shutil.rmtree(path_obj)
                else:
                    path_obj.unlink()
        print("\n🧹 Cleanup completed.")