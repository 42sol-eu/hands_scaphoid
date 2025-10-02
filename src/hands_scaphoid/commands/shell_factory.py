"""
Shell factory functions module.
---yaml
File:
    name: shell_factory.py
    uuid: b2c8d4e0-1f6g-7h3i-cd4e-6b7c8d9e0f1g
    date: 2025-09-30

Description:
    Factory functions for creating shell instances

Project:
    name: hands_scraphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Local imports]
from ..objects.shells.PowerShell import PowerShell
from ..objects.shells.WslShell import WslShell
from ..objects.shells.SshShell import SshShell



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

def create_ssh_shell(host: str, **kwargs) -> SshShell:
    """
    Create an SSH shell instance.

    Args:
        distribution: WSL distribution to use (default: "wsl")

    Returns:
        WslShell instance
    """
    return SshShell(host=host, **kwargs)

#TODO: type from call def create_shell(prompt):

