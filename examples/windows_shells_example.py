#!/usr/bin/env python3
"""
Example usage of Windows-specific shell classes.

This example demonstrates how to use PowerShellShell and WslShell
for cross-platform command execution on Windows systems.
"""

import platform
from hands_scaphoid import Shell, PowerShellShell, WslShell, create_powershell_shell, create_wsl_shell


def demo_regular_shell():
    """Demonstrate regular shell usage."""
    print("=== Regular Shell Demo ===")
    
    with Shell() as shell:
        shell.allow("echo")
        if platform.system() == "Windows":
            shell.allow("cmd")
        
        result = shell.run("echo 'Hello from regular shell'")
        print(f"Output: {result.stdout.strip()}")
        print(f"Return code: {result.returncode}")


def demo_powershell():
    """Demonstrate PowerShell shell with command translation."""
    print("\n=== PowerShell Demo ===")
    
    if platform.system() != "Windows":
        print("PowerShell demo skipped (not on Windows)")
        return
        
    try:
        # Create PowerShell shell
        ps_shell = create_powershell_shell()
        
        # Allow commands (both Unix and PowerShell versions)
        ps_shell.allow("ls")
        ps_shell.allow("Get-ChildItem")
        ps_shell.allow("cp")
        ps_shell.allow("Copy-Item")
        ps_shell.allow("echo")
        ps_shell.allow("Write-Output")
        ps_shell.allow("powershell.exe")
        ps_shell.allow("pwsh.exe")
        
        print("1. Using Unix 'ls' command (auto-translated to Get-ChildItem):")
        result = ps_shell.run("ls")
        print(f"Command succeeded: {result.returncode == 0}")
        
        print("2. Using Unix 'echo' command (auto-translated to Write-Output):")
        result = ps_shell.run("echo 'Hello from PowerShell'")
        print(f"Output: {result.stdout.strip()}")
        
        print("3. Command translation examples:")
        translations = [
            "ls -la",
            "cp file1.txt file2.txt", 
            "rm -rf folder",
            "cat file.txt",
            "pwd",
            "whoami"
        ]
        
        for cmd in translations:
            translated = ps_shell._translate_command(cmd)
            print(f"  {cmd} -> {translated}")
            
    except Exception as e:
        print(f"PowerShell demo failed: {e}")


def demo_wsl_shell():
    """Demonstrate WSL shell usage."""
    print("\n=== WSL Shell Demo ===")
    
    if platform.system() != "Windows":
        print("WSL demo skipped (not on Windows)")
        return
        
    try:
        # Create WSL shell
        wsl_shell = create_wsl_shell()
        
        # Allow Linux commands
        wsl_shell.allow("echo")
        wsl_shell.allow("ls")
        wsl_shell.allow("pwd")
        wsl_shell.allow("uname")
        
        print("1. List available WSL distributions:")
        distributions = wsl_shell.list_distributions()
        print(f"Available distributions: {distributions}")
        
        print("2. Running Linux commands in WSL:")
        
        # Test echo command
        result = wsl_shell.run("echo 'Hello from WSL'")
        print(f"Echo output: {result.stdout.strip()}")
        
        # Test pwd command
        result = wsl_shell.run("pwd")
        print(f"Current directory in WSL: {result.stdout.strip()}")
        
        # Test uname command
        result = wsl_shell.run("uname -a")
        print(f"System info: {result.stdout.strip()}")
        
        print("3. Switching WSL distributions:")
        if "Ubuntu" in distributions:
            success = wsl_shell.set_distribution("Ubuntu")
            print(f"Switched to Ubuntu: {success}")
            if success:
                result = wsl_shell.run("echo 'Hello from Ubuntu'")
                print(f"Ubuntu output: {result.stdout.strip()}")
        
    except RuntimeError as e:
        print(f"WSL not available: {e}")
    except Exception as e:
        print(f"WSL demo failed: {e}")


def demo_cross_platform_script():
    """Demonstrate a cross-platform script that adapts to the environment."""
    print("\n=== Cross-Platform Script Demo ===")
    
    # Choose the appropriate shell based on the platform
    if platform.system() == "Windows":
        print("Windows detected - using PowerShell for better compatibility")
        shell = create_powershell_shell()
        
        # Allow both Unix and PowerShell commands
        commands_to_allow = ["ls", "Get-ChildItem", "echo", "Write-Output", 
                           "powershell.exe", "pwsh.exe"]
    else:
        print(f"{platform.system()} detected - using regular shell")
        shell = Shell()
        commands_to_allow = ["ls", "echo", "pwd"]
    
    # Allow all necessary commands
    for cmd in commands_to_allow:
        shell.allow(cmd)
    
    try:
        # Run cross-platform commands
        print("1. Listing current directory:")
        result = shell.run("ls")
        print(f"Directory listing succeeded: {result.returncode == 0}")
        
        print("2. Echo test:")
        result = shell.run("echo 'Cross-platform hello'")
        print(f"Output: {result.stdout.strip()}")
        
        # Platform-specific commands
        if platform.system() == "Windows":
            print("3. Windows-specific: Getting computer name")
            shell.allow("hostname")
            result = shell.run("hostname")
            print(f"Computer name: {result.stdout.strip()}")
        else:
            print("3. Unix-specific: Getting current user")
            shell.allow("whoami")
            result = shell.run("whoami")
            print(f"Current user: {result.stdout.strip()}")
            
    except Exception as e:
        print(f"Cross-platform demo failed: {e}")


def demo_wsl_vs_powershell():
    """Compare WSL and PowerShell execution."""
    print("\n=== WSL vs PowerShell Comparison ===")
    
    if platform.system() != "Windows":
        print("Comparison demo skipped (not on Windows)")
        return
    
    commands = ["echo 'Hello World'", "pwd"]
    
    # Test with PowerShell
    print("PowerShell Results:")
    try:
        ps_shell = create_powershell_shell()
        for cmd in ["echo", "Write-Output", "pwd", "Get-Location", "powershell.exe", "pwsh.exe"]:
            ps_shell.allow(cmd)
            
        for cmd in commands:
            try:
                result = ps_shell.run(cmd)
                print(f"  {cmd}: {result.stdout.strip()}")
            except Exception as e:
                print(f"  {cmd}: Failed - {e}")
    except Exception as e:
        print(f"PowerShell test failed: {e}")
    
    # Test with WSL
    print("\nWSL Results:")
    try:
        wsl_shell = create_wsl_shell()
        for cmd in ["echo", "pwd"]:
            wsl_shell.allow(cmd)
            
        for cmd in commands:
            try:
                result = wsl_shell.run(cmd)
                print(f"  {cmd}: {result.stdout.strip()}")
            except Exception as e:
                print(f"  {cmd}: Failed - {e}")
    except Exception as e:
        print(f"WSL test failed: {e}")


if __name__ == "__main__":
    print("Hands Scaphoid Windows Shell Examples")
    print("====================================")
    print(f"Platform: {platform.system()}")
    print(f"Python: {platform.python_version()}")
    
    # Run all demos
    demo_regular_shell()
    demo_powershell()
    demo_wsl_shell()
    demo_cross_platform_script()
    demo_wsl_vs_powershell()
    
    print("\n=== Demo Complete ===")
    print("Try running individual functions for specific examples!")
