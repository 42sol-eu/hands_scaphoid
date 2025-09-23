"""
Windows shells (PowerShell and WslShell)
----
file:
    name:        WindowsShells.py  
    uuid:        1b38546a-16d2-4be6-b807-4d0bbe4f9815
description:     implementing ShellExecutables for Windows
authors:         felix@42sol.eu
project:
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from .ObjectCore import ObjectCore


class ExecutableCore(ObjectCore):
    """
    Core class for executable objects.
    """

    def __init__(self, name: str, path: str):
        super().__init__(name, path)
        self.name = name
        self.path = path

    def execute(self, *args, **kwargs):
        """
        Execute the core executable with given arguments.
        """
        print(
            f"Executing {self.name} at {self.path} with args: {args} and kwargs: {kwargs}"
        )
        # Here you would add the actual execution logic, e.g., using subprocess
        # For demonstration, we'll just return a success message
        return f"{self.name} executed successfully."
