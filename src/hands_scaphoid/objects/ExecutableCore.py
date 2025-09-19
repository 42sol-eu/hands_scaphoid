
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
        print(f"Executing {self.name} at {self.path} with args: {args} and kwargs: {kwargs}")
        # Here you would add the actual execution logic, e.g., using subprocess
        # For demonstration, we'll just return a success message
        return f"{self.name} executed successfully."