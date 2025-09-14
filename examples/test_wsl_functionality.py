#!/usr/bin/env python3
"""
Simple test of WSL functionality.
"""

import platform
from hands_scaphoid import WslShell

def test_wsl_functionality():
    """Test WSL command wrapping."""
    print("=== WSL Functionality Test ===")
    print(f"Platform: {platform.system()}")
    print()
    
    if platform.system() != "Windows":
        print("WSL tests are only relevant on Windows")
        return
    
    try:
        # Create WSL shell
        wsl_shell = WslShell()
        print(f"WSL Distribution: {wsl_shell.distribution}")
        print()
        
        # Test command wrapping
        test_commands = [
            "ls -la",
            "pwd", 
            "echo 'Hello WSL'",
            "uname -a"
        ]
        
        print("Command wrapping examples:")
        for cmd in test_commands:
            wrapped = wsl_shell._wrap_command_for_wsl(cmd)
            print(f"{cmd:20} -> {' '.join(wrapped)}")
        
        print()
        
        # List available distributions
        print("Available WSL distributions:")
        distributions = wsl_shell.list_distributions()
        if distributions:
            for dist in distributions:
                print(f"  - {dist}")
        else:
            print("  No distributions found")
            
    except RuntimeError as e:
        print(f"WSL not available: {e}")
    except Exception as e:
        print(f"WSL test failed: {e}")

if __name__ == "__main__":
    test_wsl_functionality()
