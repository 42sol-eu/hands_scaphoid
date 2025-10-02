"""
PowerShell class module.
---yaml
File:
    name: PowerShell.py
    uuid: 4i7h1g6d-9f5e-6g9h-ea0b-6g7h8a9i0j1k
    date: 2025-09-30

Description:
    PowerShell-compatible shell executor that translates Unix commands to PowerShell equivalents

Project:
    name: hands_scraphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import platform
import subprocess
from typing import Dict, List

#%% [Local imports]
from ..ShellExecutable import ShellExecutable as Shell
from ...__base__ import PathLike


class PowerShell(Shell):
    """
    A PowerShell-compatible shell executor that translates Unix commands to PowerShell.

    This class automatically translates common Unix commands to their PowerShell
    equivalents when running on Windows systems.
    """

    # Command translation mapping from Unix to PowerShell
    COMMAND_TRANSLATIONS = {
        "ls": "Get-ChildItem",
        "dir": "Get-ChildItem",
        "cat": "Get-Content",
        "cp": "Copy-Item",
        "copy": "Copy-Item",
        "mv": "Move-Item",
        "move": "Move-Item",
        "rm": "Remove-Item",
        "del": "Remove-Item",
        "mkdir": "New-Item -ItemType Directory",
        "rmdir": "Remove-Item -Recurse",
        "pwd": "Get-Location",
        "cd": "Set-Location",
        "echo": "Write-Output",
        "grep": "Select-String",
        "find": "Get-ChildItem -Recurse | Where-Object",
        "ps": "Get-Process",
        "kill": "Stop-Process",
        "which": "Get-Command",
        "whereis": "Get-Command",
        "curl": "Invoke-WebRequest",
        "wget": "Invoke-WebRequest",
        "head": "Get-Content | Select-Object -First",
        "tail": "Get-Content | Select-Object -Last",
        "wc": "Measure-Object",
        "sort": "Sort-Object",
        "uniq": "Sort-Object -Unique",
        "cut": "Select-Object",
        "awk": "ForEach-Object",
        "sed": "ForEach-Object",
        "env": "Get-ChildItem Env:",
        "export": "Set-Variable",
        "chmod": "Set-ItemProperty",
        "chown": "Set-Acl",
        "df": "Get-WmiObject -Class Win32_LogicalDisk",
        "du": "Get-ChildItem -Recurse | Measure-Object -Property Length -Sum",
        "mount": "Get-WmiObject -Class Win32_LogicalDisk",
        "umount": 'Write-Warning "umount not available in PowerShell"',
        "top": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
        "htop": "Get-Process | Sort-Object CPU -Descending | Select-Object -First 10",
        "free": "Get-WmiObject -Class Win32_OperatingSystem | Select-Object TotalVisibleMemorySize, FreePhysicalMemory",
        "uptime": "Get-WmiObject -Class Win32_OperatingSystem | Select-Object LastBootUpTime",
        "whoami": "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name",
        "id": "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name",
        "hostname": "$env:COMPUTERNAME",
        "uname": "Get-ComputerInfo | Select-Object WindowsProductName, WindowsVersion",
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
            if command == "ls" and args:
                # ls -la -> Get-ChildItem -Force -Name
                ps_args = []
                for arg in args:
                    if arg.startswith("-"):
                        if "a" in arg:
                            ps_args.append("-Force")
                        if "l" in arg:
                            ps_args.append("-Detailed")
                        if "h" in arg:
                            ps_args.append("-Humanized")
                    else:
                        ps_args.append(f'"{arg}"')
                return f"{translated_cmd} {' '.join(ps_args)}"

            elif command == "cp" and len(args) >= 2:
                # cp source dest -> Copy-Item source dest
                source = f'"{args[0]}"' if not args[0].startswith('"') else args[0]
                dest = f'"{args[1]}"' if not args[1].startswith('"') else args[1]
                extra_args = args[2:] if len(args) > 2 else []
                ps_args = [source, dest]
                if "-r" in " ".join(args) or "-R" in " ".join(args):
                    ps_args.append("-Recurse")
                if "-f" in " ".join(args):
                    ps_args.append("-Force")
                ps_args.extend(extra_args)
                return f"{translated_cmd} {' '.join(ps_args)}"

            elif command == "rm" and args:
                # rm -rf file -> Remove-Item file -Recurse -Force
                ps_args = []
                files = []
                for arg in args:
                    if arg.startswith("-"):
                        if "r" in arg or "R" in arg:
                            ps_args.append("-Recurse")
                        if "f" in arg:
                            ps_args.append("-Force")
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

    def run(
        self, command_with_args: str, **kwargs: Dict
    ) -> subprocess.CompletedProcess:
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