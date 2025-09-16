#!/usr/bin/env python3
"""
Windows-specific shell implementations for hands_scaphoid.

This module provides Windows PowerShell and WSL shell execution classes
that extend the base Shell functionality with platform-specific features.

Classes:
    PowerShell: Translates Unix commands to PowerShell equivalents
    WslShell: Executes commands in Windows Subsystem for Linux
"""

from __future__ import annotations

import platform
import subprocess
from typing import Dict, List, Optional, Union

from .Shell import Shell
from .__base__ import console


class PowerShell(Shell):
    """
    A PowerShell-compatible shell executor that translates Unix commands to PowerShell.
    
    This class automatically translates common Unix commands to their PowerShell
    equivalents when running on Windows systems.
    """

    # Command translation mapping from Unix to PowerShell
    COMMAND_TRANSLATIONS = {
        'ls': 'Get-ChildItem',
        'dir': 'Get-ChildItem', 
        'cat': 'Get-Content',
        'cp': 'Copy-Item',
        'copy': 'Copy-Item',
        'mv': 'Move-Item',
        'move': 'Move-Item',
        'rm': 'Remove-Item',
        'del': 'Remove-Item',
        'mkdir': 'New-Item -ItemType Directory',
        'rmdir': 'Remove-Item -Recurse',
        'pwd': 'Get-Location',
        'cd': 'Set-Location',
        'echo': 'Write-Output',
        'grep': 'Select-String',
        'find': 'Get-ChildItem -Recurse | Where-Object',
        'ps': 'Get-Process',
        'kill': 'Stop-Process',
        'which': 'Get-Command',
        'whereis': 'Get-Command',
        'curl': 'Invoke-WebRequest',
        'wget': 'Invoke-WebRequest',
        'head': 'Get-Content | Select-Object -First',
        'tail': 'Get-Content | Select-Object -Last',
        'wc': 'Measure-Object',
        'sort': 'Sort-Object',
        'uniq': 'Sort-Object -Unique',
        'cut': 'Select-Object',
        'awk': 'ForEach-Object',
        'sed': 'ForEach-Object',
        'env': 'Get-ChildItem Env:',
        'export': 'Set-Variable',
        'chmod': 'Set-ItemProperty',
        'chown': 'Set-Acl',
        'df': 'Get-WmiObject -Class Win32_LogicalDisk',
        'du': 'Get-ChildItem -Recurse | Measure-Object -Property Length -Sum',
        'mount': 'Get-WmiObject -Class Win32_LogicalDisk',
        'umount': 'Write-Warning "umount not available in PowerShell"',
        'top': 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10',
        'htop': 'Get-Process | Sort-Object CPU -Descending | Select-Object -First 10',
        'free': 'Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory',
        'uptime': 'Get-WmiObject -Class Win32_OperatingSystem | Select-Object LastBootUpTime',
        'whoami': '[System.Security.Principal.WindowsIdentity]::GetCurrent().Name',
        'id': '[System.Security.Principal.WindowsIdentity]::GetCurrent().Name',
        'hostname': '$env:COMPUTERNAME',
        'uname': 'Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion'
    }

    def __init__(self, *args, **kwargs):
        """Initialize PowerShell with PowerShell as the default shell."""
        super().__init__(*args, **kwargs)
        self.shell_executable = "powershell.exe"
        if platform.system() == "Windows":
            # Try to use PowerShell Core (pwsh) if available, fallback to Windows PowerShell
            try:
                subprocess.run(["pwsh", "-Version"], capture_output=True, check=True)
                self.shell_executable = "pwsh.exe"
            except (subprocess.CalledProcessError, FileNotFoundError):
                self.shell_executable = "powershell.exe"

    def _translate_command(self, command_with_args: str) -> str:
        """
        Translate Unix commands to PowerShell equivalents.
        
        Args:
            command_with_args: The original command with arguments
            
        Returns:
            Translated PowerShell command
        """
        if isinstance(command_with_args, str):
            parts = command_with_args.strip().split()
        else:
            parts = command_with_args
            
        if not parts:
            return command_with_args
            
        command = parts[0]
        args = parts[1:] if len(parts) > 1 else []
        
        # Check if we have a translation for this command
        if command in self.COMMAND_TRANSLATIONS:
            translated_cmd = self.COMMAND_TRANSLATIONS[command]
            
            # Handle special cases for argument translation
            if command == 'ls' and args:
                # ls -la -> Get-ChildItem -Force -Name
                ps_args = []
                for arg in args:
                    if arg.startswith('-'):
                        if 'a' in arg:
                            ps_args.append('-Force')
                        if 'l' in arg:
                            ps_args.append('-Detailed') 
                        if 'h' in arg:
                            ps_args.append('-Humanized')
                    else:
                        ps_args.append(f'"{arg}"')
                return f"{translated_cmd} {' '.join(ps_args)}"
                
            elif command == 'cp' and len(args) >= 2:
                # cp source dest -> Copy-Item source dest
                source = f'"{args[0]}"' if not args[0].startswith('"') else args[0]
                dest = f'"{args[1]}"' if not args[1].startswith('"') else args[1]
                extra_args = args[2:] if len(args) > 2 else []
                ps_args = [source, dest]
                if '-r' in ' '.join(args) or '-R' in ' '.join(args):
                    ps_args.append('-Recurse')
                if '-f' in ' '.join(args):
                    ps_args.append('-Force')
                ps_args.extend(extra_args)
                return f"{translated_cmd} {' '.join(ps_args)}"
                
            elif command == 'rm' and args:
                # rm -rf file -> Remove-Item file -Recurse -Force
                ps_args = []
                files = []
                for arg in args:
                    if arg.startswith('-'):
                        if 'r' in arg or 'R' in arg:
                            ps_args.append('-Recurse')
                        if 'f' in arg:
                            ps_args.append('-Force')
                    else:
                        files.append(f'"{arg}"' if not arg.startswith('"') else arg)
                return f"{translated_cmd} {' '.join(files)} {' '.join(ps_args)}"
                
            else:
                # Default: just append arguments
                if args:
                    return f"{translated_cmd} {' '.join(args)}"
                else:
                    return translated_cmd
        
        # No translation available, return original command
        return command_with_args

    def run(self, command_with_args: str, **kwargs) -> subprocess.CompletedProcess:
        """
        Execute a command, translating Unix commands to PowerShell if needed.
        
        Args:
            command_with_args: The command to execute
            **kwargs: Additional arguments passed to parent run method
            
        Returns:
            CompletedProcess object with execution results
        """
        if platform.system() == "Windows":
            # Translate the command for Windows PowerShell
            translated_command = self._translate_command(command_with_args)
            
            # If the command was translated, we need to run it through PowerShell
            if translated_command != command_with_args:
                # Run the translated command through PowerShell
                ps_command = f'{self.shell_executable} -Command "{translated_command}"'
                return super().run(ps_command, **kwargs)
        
        # Run the original command
        return super().run(command_with_args, **kwargs)


class WslShell(Shell):
    """
    A shell executor that runs commands in Windows Subsystem for Linux.
    
    This class prefixes commands with wsl.exe or a specific distribution
    executable (like debian.exe) to execute Linux commands on Windows.
    """

    def __init__(self, distribution: str = "wsl", *args, **kwargs):
        """
        Initialize WslShell with a specific WSL distribution.
        
        Args:
            distribution: WSL distribution command (e.g., 'wsl', 'debian', 'ubuntu')
            *args, **kwargs: Arguments passed to parent Shell class
        """
        super().__init__(*args, **kwargs)
        self.distribution = distribution
        
        # Ensure the distribution executable exists
        if not self._check_wsl_available():
            raise RuntimeError(f"WSL distribution '{distribution}' is not available")

    def _check_wsl_available(self) -> bool:
        """
        Check if the specified WSL distribution is available.
        
        Returns:
            True if WSL distribution is available, False otherwise
        """
        try:
            # Try to run the distribution command with --help
            result = subprocess.run(
                [f"{self.distribution}.exe", "--help"],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False

    def _wrap_command_for_wsl(self, command_with_args: str) -> List[str]:
        """
        Wrap a command to be executed in WSL.
        
        Args:
            command_with_args: The original command with arguments
            
        Returns:
            List of command parts including WSL wrapper
        """
        if isinstance(command_with_args, str):
            # For string commands, pass them to WSL as a single argument
            return [f"{self.distribution}.exe", "--", "sh", "-c", command_with_args]
        else:
            # For list commands, join them and pass to WSL
            command_str = " ".join(command_with_args)
            return [f"{self.distribution}.exe", "--", "sh", "-c", command_str]

    def run(self, command_with_args: str, **kwargs) -> subprocess.CompletedProcess:
        """
        Execute a command in WSL.
        
        Args:
            command_with_args: The command to execute in WSL
            **kwargs: Additional arguments passed to subprocess.run
            
        Returns:
            CompletedProcess object with execution results
        """
        if platform.system() == "Windows":
            # Wrap the command for WSL execution
            wsl_command = self._wrap_command_for_wsl(command_with_args)
            
            # Extract the base command for permission checking
            if isinstance(command_with_args, str):
                base_command = command_with_args.strip().split()[0]
            else:
                base_command = command_with_args[0]
                
            # Check if the base command is allowed
            if base_command not in self.allow_commands:
                raise PermissionError(f"Command '{base_command}' is not allowed. Use allow() first.")
            
            console.print(f"[bold]$ (WSL) {command_with_args}[/bold]")
            
            # Execute the wrapped command
            return subprocess.run(
                wsl_command,
                cwd=self.cwd,
                env=self.env,
                **kwargs
            )
        else:
            # On non-Windows systems, just run the command normally
            return super().run(command_with_args, **kwargs)

    def list_distributions(self) -> List[str]:
        """
        List available WSL distributions.
        
        Returns:
            List of available WSL distribution names
        """
        try:
            result = subprocess.run(
                ["wsl.exe", "--list", "--quiet"],
                capture_output=True,
                text=True,
                check=True
            )
            # Parse the output to get distribution names
            distributions = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    # Remove any special characters and whitespace
                    dist_name = line.strip().replace('\x00', '').replace('*', '').strip()
                    if dist_name:
                        distributions.append(dist_name)
            return distributions
        except (subprocess.CalledProcessError, FileNotFoundError):
            return []

    def set_distribution(self, distribution: str) -> bool:
        """
        Change the WSL distribution used by this shell.
        
        Args:
            distribution: New distribution name to use
            
        Returns:
            True if distribution was successfully set, False otherwise
        """
        old_distribution = self.distribution
        self.distribution = distribution
        
        if self._check_wsl_available():
            return True
        else:
            # Revert to old distribution if new one is not available
            self.distribution = old_distribution
            return False


# Convenience functions for creating shell instances
def create_powershell_shell(**kwargs) -> PowerShell:
    """
    Create a PowerShell shell instance.
    
    Returns:
        PowerShell instance
    """
    return PowerShell(**kwargs)


def create_wsl_shell(distribution: str = "wsl", **kwargs) -> WslShell:
    """
    Create a WSL shell instance.
    
    Args:
        distribution: WSL distribution to use (default: "wsl")
        
    Returns:
        WslShell instance
    """
    return WslShell(distribution=distribution, **kwargs)


def get_available_wsl_distributions() -> List[str]:
    """
    Get list of available WSL distributions.
    
    Returns:
        List of available WSL distribution names
    """
    dummy_shell = WslShell()
    return dummy_shell.list_distributions()
