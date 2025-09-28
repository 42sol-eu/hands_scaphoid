---
applyTo: '**/*.hands.py'
---
# Hands Python scripts settings 

## Package Integration
- Always include the `hands_scaphoid` package
- Use hierarchical context managers for file operations
- Import from base: `from hands_scaphoid import DirectoryContext, FileContext, ArchiveContext`

## CLI Framework
- Use `rich-click` for command-line interfaces
- Leverage Rich console for beautiful output: `from hands_scaphoid import console`
- Use structured logging: `from hands_scaphoid import logger`

## Script Patterns
```python
#!/usr/bin/env python3
"""
Script description with hands_scaphoid integration.
---yaml
File:
    name: {{script_name}}.hands.py
    uuid: {{uuid4-generated-identifier}}
    date: {{modification-date, YYYY-MM-DD}}

Description:
    {{Detailed description of script functionality}}

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid


Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

from hands_scaphoid import DirectoryContext, FileContext, console, logger
import rich_click as click

@click.command()
@click.option('--path', type=click.Path(), help='Target path')
def main(path):
    """Main script function with context managers."""
    with DirectoryContext(path) as dir_ctx:
        # Use hierarchical operations
        pass

if __name__ == "__main__":
    main()
```

## Integration Patterns
- Use context managers for hierarchical path resolution
- Leverage handler patterns for file type detection
- Follow dual interface design (operations + context managers)