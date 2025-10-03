"""
Shell implementations module.
---yaml
File:
    name: __init__.py
    date: 2025-09-30

Description:
    Exports shell implementation classes for different platforms.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Shell implementations]
from .PowerShell import PowerShell
from .WslShell import WslShell

# [Exports]
__all__ = [
    "PowerShell",
    "WslShell",
]
