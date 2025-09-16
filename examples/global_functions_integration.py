#!/usr/bin/env python3
"""
Example demonstrating integration between file system contexts and shell operations.

This example shows how to use the DirectoryContext, FileContext, and ArchiveContext
with shell operations using the new separated architecture.
"""

import sys
from pathlib import Path

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import Directory, File, Archive
from hands_scaphoid.ShellContext import ShellContext


def demo_filesystem_shell_integration():
    """Demonstrate integration between file system operations and shell commands."""
    print("\n=== File System and Shell Integration Demo ===")
    
    # Directory context with shell integration
    print("\n1. Directory operations with shell commands:")
    with DirectoryContext("test_dir", create=True) as dir_ctx:
        # File system operations
        dir_ctx.create_directory("subdir")
        dir_ctx.list_contents()
        
        # Create files using file context
        with FileContext("example.txt", create=True) as file_ctx:
            file_ctx.append_line("Hello from integrated operations!")
            file_ctx.append_line("This combines file system and shell operations.")
            file_ctx.add_heading("Integration Example")
            file_ctx.write_content("Content added via context manager.")
        
        # Create archive using archive context
        with ArchiveContext(target="../test_archive.zip") as archive_ctx:
            archive_ctx.add_file("example.txt", "example.txt")
            archive_ctx.add_directory("subdir", "test_subdirectory")
            contents = archive_ctx.list_contents()
            print(f"Archive contents: {contents}")
        
        print("  ✅ File system operations completed!")


def demo_shell_with_filesystem():
    """Demonstrate shell operations combined with file system contexts."""
    print("\n2. Shell operations with file system context:")
    
    # Shell context with file system operations
    with ShellContext() as shell:
        shell.allow("ls")
        shell.allow("cat") 
        shell.allow("mkdir")
        shell.allow("echo")
        shell.allow("pwd")
        
        # Create directory using shell, then operate on it with context manager
        shell.run("mkdir -p shell_test")
        
        with DirectoryContext("shell_test") as dir_ctx:
            # Mix shell commands and context operations
            print("    Current directory contents (shell):")
            shell.run("ls -la")
            
            # File operations via context manager
            dir_ctx.create_directory("context_created")
            
            with FileContext("mixed_file.txt", create=True) as file_ctx:
                file_ctx.append_line("Created with mixed shell and context operations")
                
            # Show results with shell command
            print("    File content (shell):")
            shell.run("cat mixed_file.txt")
            
            print("  ✅ Mixed shell and context operations completed!")


def demo_nested_integration():
    """Demonstrate nested contexts with both file system and shell operations."""
    print("\n3. Nested contexts with integrated operations:")
    
    with DirectoryContext("integration_test", create=True) as outer_dir:
        outer_contents = outer_dir.list_contents()
        print(f"  Outer directory contents: {outer_contents}")
        
        with FileContext("outer_file.txt", create=True) as outer_file:
            outer_file.append_line("Outer file content")
            
        # Nested directory context
        with DirectoryContext("nested_context") as nested_dir:
            nested_dir.create_directory("deep_nested")
            
            # Shell operations within nested context
            with ShellContext() as shell:
                shell.allow("ls")
                shell.allow("pwd")
                shell.allow("echo")
                
                print("    Shell operations within nested context:")
                shell.run("pwd")
                shell.run("ls -la")
                
                # Archive within nested shell context
                with ArchiveContext(target="nested_archive.zip") as archive:
                    archive.add_file("../outer_file.txt", "outer.txt")
                    nested_contents = archive.list_contents()
                    print(f"    Nested archive contents: {nested_contents}")
                    
        final_contents = outer_dir.list_contents()
        print(f"  Final outer directory contents: {final_contents}")
        print("  ✅ Nested integration completed!")


def demo_error_handling_integration():
    """Demonstrate error handling with integrated operations."""
    print("\n4. Error handling with integrated operations:")
    
    try:
        with DirectoryContext("error_test", create=True) as dir_ctx:
            # Try shell operation that might fail
            with ShellContext() as shell:
                shell.allow("ls")
                try:
                    shell.run("ls nonexistent_file")
                except Exception as e:
                    print(f"    Shell error handled: {e}")
                
                # Continue with file operations despite shell error
                with FileContext("recovery_file.txt", create=True) as file_ctx:
                    file_ctx.write_content("Recovered from shell error")
                    content = file_ctx.read_content()
                    print(f"    Recovery file content: {repr(content[:30])}...")
                    
            print("  ✅ Error handling integration completed!")
                    
    except Exception as e:
        print(f"  ❌ Unexpected error: {e}")


def demo_performance_comparison():
    """Compare performance of different integration approaches."""
    print("\n5. Performance comparison of integration approaches:")
    
    import time
    
    # Direct operations approach
    start_time = time.time()
    for i in range(5):
        Directory.create_directory(f"perf_direct_{i}")
        File.write_content(f"perf_direct_{i}/file.txt", f"Content {i}")
        Archive.create_zip_archive(f"perf_direct_{i}.zip", f"perf_direct_{i}")
    direct_time = time.time() - start_time
    
    # Context manager approach
    start_time = time.time()
    for i in range(5):
        with DirectoryContext(f"perf_context_{i}", create=True) as dir_ctx:
            with FileContext("file.txt", create=True) as file_ctx:
                file_ctx.write_content(f"Content {i}")
            with ArchiveContext(target=f"../perf_context_{i}.zip", source=".") as archive:
                pass  # Archive is created automatically
    context_time = time.time() - start_time
    
    # Shell integration approach
    start_time = time.time()
    with ShellContext() as shell:
        shell.allow("mkdir")
        shell.allow("echo")
        shell.allow("zip")
        for i in range(5):
            shell.run(f"mkdir -p perf_shell_{i}")
            with FileContext(f"perf_shell_{i}/file.txt", create=True) as file_ctx:
                file_ctx.write_content(f"Content {i}")
            shell.run(f"cd perf_shell_{i} && zip ../perf_shell_{i}.zip file.txt")
    shell_time = time.time() - start_time
    
    print(f"  Direct operations: {direct_time:.4f}s")
    print(f"  Context managers: {context_time:.4f}s")
    print(f"  Shell integration: {shell_time:.4f}s")
    print("  ✅ Performance comparison completed!")


if __name__ == "__main__":
    print("File System and Shell Integration Demonstration")
    print("==============================================")
    
    try:
        demo_filesystem_shell_integration()
        demo_shell_with_filesystem()
        demo_nested_integration()
        demo_error_handling_integration()
        demo_performance_comparison()
        
        print("\n🎉 All integration demonstrations completed successfully!")
        print("\nKey Features Demonstrated:")
        print("✅ File system context managers with shell operations")
        print("✅ Mixed shell and context manager operations")
        print("✅ Nested contexts with integrated functionality")
        print("✅ Error handling across different operation types")
        print("✅ Performance comparison of integration approaches")
        print("\nNote: The separated architecture allows flexible")
        print("integration between different operation types.")
        
    except Exception as e:
        print(f"\n❌ Error during demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test files
        import shutil
        cleanup_patterns = [
            "test_dir", "test_archive.zip", "shell_test", "integration_test",
            "error_test", "perf_direct_*", "perf_context_*", "perf_shell_*"
        ]
        
        for pattern in cleanup_patterns:
            if '*' in pattern:
                # Handle wildcard patterns
                import glob
                for path in glob.glob(pattern):
                    path_obj = Path(path)
                    if path_obj.exists():
                        if path_obj.is_dir():
                            shutil.rmtree(path_obj)
                        else:
                            path_obj.unlink()
            else:
                path_obj = Path(pattern)
                if path_obj.exists():
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj)
                    else:
                        path_obj.unlink()
        
        print("\n🧹 Integration cleanup completed.")