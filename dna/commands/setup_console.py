

try:
    from rich.console import Console
    console = Console()
except ImportError:
    # Fallback console for when rich is not available
    class SimpleConsole:
        def print(self, text, **kwargs):
            print(text)
    console = SimpleConsole()
