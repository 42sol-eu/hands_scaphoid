"""
WslShell class module.
---yaml
File:
    name: WslShell.py
    uuid: 3j8i2h7e-0g6f-7h0i-fb1c-7h8i9a0j1k2l
    date: 2025-09-30

Description:
    Shell executor that runs commands in Windows Subsystem for Linux

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
from ...__base__ import console


class WslShell(Shell):
    """
    A shell executor that runs commands in Windows Subsystem for Linux.

    This class prefixes commands with wsl.exe or a specific distribution
    executable (like debian.exe) to execute Linux commands on Windows.
    """

    def __init__(
        self, distribution: str = "wsl", *args: List[str], **kwargs: Dict[str, str]
    ):
        """
        Initialize WslShell with a specific WSL distribution.

        Args:
            distribution: WSL distribution command (e.g., 'wsl', 'debian', 'ubuntu')
            *args:
            **kwargs: Arguments passed to parent Shell class
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
                [f"{self.distribution}.exe", "--help"], capture_output=True, timeout=5
            )
            return result.returncode == 0
        except (
            subprocess.CalledProcessError,
            FileNotFoundError,
            subprocess.TimeoutExpired,
        ):
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

    def run(
        self, command_with_args: str, **kwargs: Dict[str, str]
    ) -> subprocess.CompletedProcess:
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
                raise PermissionError(
                    f"Command '{base_command}' is not allowed. Use allow() first."
                )

            console.print(f"[bold]$ (WSL) {command_with_args}[/bold]")

            # Execute the wrapped command
            return subprocess.run(wsl_command, cwd=self.cwd, env=self.env, **kwargs)
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
                check=True,
            )
            # Parse the output to get distribution names
            distributions = []
            for line in result.stdout.strip().split("\n"):
                if line.strip():
                    # Remove any special characters and whitespace
                    dist_name = (
                        line.strip().replace("\x00", "").replace("*", "").strip()
                    )
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