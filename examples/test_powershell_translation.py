#!/usr/bin/env python3
"""
Simple test of PowerShell command translation.
"""

from hands_scaphoid import PowerShellShell

def test_powershell_translation():
    """Test PowerShell command translation."""
    shell = PowerShellShell()
    
    print("=== PowerShell Command Translation Test ===")
    print()
    
    test_commands = [
        "ls",
        "ls -la", 
        "cp file1.txt file2.txt",
        "cp -r folder dest",
        "rm file.txt",
        "rm -rf folder",
        "cat file.txt",
        "pwd",
        "echo hello",
        "ps",
        "whoami",
        "hostname",
        "grep pattern file.txt",
        "mkdir newfolder"
    ]
    
    for cmd in test_commands:
        translated = shell._translate_command(cmd)
        print(f"{cmd:25} -> {translated}")
    
    print()
    print("=== PowerShell Shell Info ===")
    print(f"Shell executable: {shell.shell_executable}")

if __name__ == "__main__":
    test_powershell_translation()
