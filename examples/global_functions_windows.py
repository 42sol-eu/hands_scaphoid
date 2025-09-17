#!/usr/bin/env python3
"""
Example demonstrating file system and Windows shell integration.

This example shows how to use the DirectoryContext, FileContext, and ArchiveContext
with Windows shell operations using the new separated architecture.
"""

import sys
from pathlib import Path
import platform

# Add the src directory to the path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext
from hands_scaphoid import Directory, File, Archive
from hands_scaphoid.contexts.ShellContext import ShellContext


def demo_windows_filesystem_integration():
    """Demonstrate Windows-specific file system operations."""
    print("\n=== Windows File System Integration Demo ===")
    print(f"Platform: {platform.system()}")
    
    # Directory context with Windows paths
    print("\n1. Windows directory operations:")
    with DirectoryContext("test_dir", create=True) as dir_ctx:
        # File system operations
        dir_ctx.create_directory("subdir")
        dir_ctx.list_contents()
        
        # Create files with Windows line endings
        with FileContext("windows_example.txt", create=True) as file_ctx:
            file_ctx.append_line("Hello from Windows integration!")
            file_ctx.append_line("This handles Windows paths and line endings.")
            file_ctx.add_heading("Windows Integration")
            file_ctx.write_content("Content with proper Windows formatting.")
        
        # Create archive
        with ArchiveContext(target="../windows_archive.zip") as archive_ctx:
            archive_ctx.add_file("windows_example.txt", "windows_example.txt")
            archive_ctx.add_directory("subdir", "windows_subdirectory")
            contents = archive_ctx.list_contents()
            print(f"Archive contents: {contents}")
        
        print("  ✅ Windows file system operations completed!")


def demo_powershell_integration():
    """Demonstrate PowerShell integration with file system contexts."""
    print("\n2. PowerShell integration:")
    
    if platform.system() != "Windows":
        print("  ⚠️ Skipping PowerShell demo - not on Windows")
        return
    
    # PowerShell context with file system operations
    with ShellContext() as shell:
        # Allow PowerShell commands
        shell.allow("Get-ChildItem")
        shell.allow("New-Item")
        shell.allow("Set-Content")
        shell.allow("Get-Content")
        shell.allow("Test-Path")
        
        # Create directory using PowerShell
        shell.run("New-Item -ItemType Directory -Path 'powershell_test' -Force")
        
        with DirectoryContext("powershell_test") as dir_ctx:
            # Mix PowerShell commands and context operations
            print("    Current directory contents (PowerShell):")
            shell.run("Get-ChildItem")
            
            # File operations via context manager
            dir_ctx.create_directory("ps_context_created")
            
            with FileContext("powershell_file.txt", create=True) as file_ctx:
                file_ctx.append_line("Created with PowerShell and context integration")
                file_ctx.append_line("Handles Windows paths properly")
                
            # Show results with PowerShell
            print("    File content (PowerShell):")
            shell.run("Get-Content powershell_file.txt")
            
            print("  ✅ PowerShell integration completed!")


def demo_cmd_integration():
    """Demonstrate Command Prompt integration with file system contexts.""" 
    print("\n3. Command Prompt integration:")
    
    if platform.system() != "Windows":
        print("  ⚠️ Skipping CMD demo - not on Windows")
        return
    
    with ShellContext() as shell:
        # Allow CMD commands
        shell.allow("dir")
        shell.allow("mkdir")
        shell.allow("echo")
        shell.allow("type")
        shell.allow("cd")
        
        # Create directory using CMD
        shell.run("mkdir cmd_test 2>nul")
        
        with DirectoryContext("cmd_test") as dir_ctx:
            # Mix CMD commands and context operations
            print("    Current directory contents (CMD):")
            shell.run("dir")
            
            # File operations via context manager
            dir_ctx.create_directory("cmd_context_created")
            
            with FileContext("cmd_file.txt", create=True) as file_ctx:
                file_ctx.append_line("Created with CMD and context integration")
                file_ctx.append_line("Works with Windows Command Prompt")
                
            # Show results with CMD
            print("    File content (CMD):")
            shell.run("type cmd_file.txt")
            
            print("  ✅ Command Prompt integration completed!")


def demo_windows_paths():
    """Demonstrate Windows path handling with contexts."""
    print("\n4. Windows path handling:")
    
    # Test various Windows path formats
    test_paths = [
        "windows_paths\\backslash_path",
        "windows_paths/forward_slash_path", 
        "windows_paths\\mixed\\forward/slash\\path"
    ]
    
    with DirectoryContext("windows_paths", create=True) as base_dir:
        for test_path in test_paths:
            try:
                # Extract just the subdirectory name
                subdir = Path(test_path).name
                base_dir.create_directory(subdir)
                
                with FileContext(f"{subdir}\\test_file.txt", create=True) as file_ctx:
                    file_ctx.write_content(f"Content for {subdir}")
                    file_ctx.append_line(f"Path: {test_path}")
                    
                print(f"    ✅ Created: {subdir}")
                
            except Exception as e:
                print(f"    ❌ Failed to create {test_path}: {e}")
        
        final_contents = base_dir.list_contents()
        print(f"  Final contents: {final_contents}")
        print("  ✅ Windows path handling completed!")


def demo_windows_archive_formats():
    """Demonstrate Windows-compatible archive formats."""
    print("\n5. Windows archive format handling:")
    
    # Create content to archive
    with DirectoryContext("archive_source", create=True) as source:
        source.create_directory("windows_subdir")
        
        with FileContext("windows_file.txt", create=True) as file_ctx:
            file_ctx.write_content("Windows-specific content")
            file_ctx.append_line("Line endings: \\r\\n")
            file_ctx.append_line("Character encoding: UTF-8")
        
        with DirectoryContext("windows_subdir") as subdir:
            with FileContext("nested_windows_file.txt", create=True) as nested_file:
                nested_file.write_content("Nested Windows file")
    
    # Create different archive formats
    formats = [
        ("windows_demo.zip", "zip"),
        ("windows_demo.tar", "tar"),
    ]
    
    if platform.system() == "Windows":
        # Add Windows-specific formats
        formats.append(("windows_demo.tar.gz", "tar.gz"))
    
    for archive_name, archive_type in formats:
        try:
            with ArchiveContext(
                source="archive_source",
                target=archive_name,
                archive_type=archive_type
            ) as archive:
                contents = archive.list_contents()
                info = archive.get_archive_info()
                print(f"  ✅ {archive_type}: {archive_name} ({len(contents)} files)")
                
        except Exception as e:
            print(f"  ❌ Failed to create {archive_type}: {e}")
    
    print("  ✅ Windows archive formats completed!")


def demo_windows_error_handling():
    """Demonstrate Windows-specific error handling."""
    print("\n6. Windows error handling:")
    
    try:
        # Test long path handling
        long_path = "windows_error_test\\" + "very_long_directory_name\\" * 10
        
        with DirectoryContext("windows_error_test", create=True) as dir_ctx:
            try:
                # This might fail on older Windows versions
                dir_ctx.create_directory(long_path)
                print("    ✅ Long path creation succeeded")
            except Exception as e:
                print(f"    ⚠️ Long path creation failed (expected): {type(e).__name__}")
            
            # Test invalid characters
            invalid_names = ["con.txt", "aux.txt", "file<>name.txt", "file|name.txt"]
            for invalid_name in invalid_names:
                try:
                    with FileContext(invalid_name, create=True) as file_ctx:
                        file_ctx.write_content("This shouldn't work")
                    print(f"    ⚠️ Created invalid filename: {invalid_name}")
                except Exception as e:
                    print(f"    ✅ Correctly rejected invalid filename: {invalid_name}")
        
        print("  ✅ Windows error handling completed!")
        
    except Exception as e:
        print(f"  ❌ Unexpected error in Windows error handling: {e}")


if __name__ == "__main__":
    print("Windows File System and Shell Integration Demonstration")
    print("=======================================================")
    print(f"Running on: {platform.system()} {platform.release()}")
    
    try:
        demo_windows_filesystem_integration()
        demo_powershell_integration()
        demo_cmd_integration()
        demo_windows_paths()
        demo_windows_archive_formats()
        demo_windows_error_handling()
        
        print("\n🎉 All Windows integration demonstrations completed!")
        print("\nKey Features Demonstrated:")
        print("✅ Windows-specific file system operations")
        print("✅ PowerShell integration with context managers")
        print("✅ Command Prompt integration")
        print("✅ Windows path format handling")
        print("✅ Windows-compatible archive formats")
        print("✅ Windows-specific error handling")
        print("\nNote: Some features may be skipped on non-Windows platforms.")
        
    except Exception as e:
        print(f"\n❌ Error during Windows demonstration: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup test files
        import shutil
        cleanup_paths = [
            "test_dir", "windows_archive.zip", "powershell_test", "cmd_test",
            "windows_paths", "archive_source", "windows_demo.zip", 
            "windows_demo.tar", "windows_demo.tar.gz", "windows_error_test"
        ]
        
        for path in cleanup_paths:
            path_obj = Path(path)
            if path_obj.exists():
                try:
                    if path_obj.is_dir():
                        shutil.rmtree(path_obj)
                    else:
                        path_obj.unlink()
                except Exception as e:
                    print(f"  ⚠️ Could not clean up {path}: {e}")
        
        print("\n🧹 Windows cleanup completed.")