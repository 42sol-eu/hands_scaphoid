"""
file commands for package.

This module contains file command functions used throughout the package.
----
file:
    name:        file_commands.py  
    uuid:        9e8b266d-8e07-42cf-a0ee-f9633493c789
description:     file_commands init
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from ..__base__ import (
    console, 
    # yes, no, true, false, 
    # DEBUG_MODE,
    logger,
    PathLike, Path
)
from .core_commands import is_file, ensure_path
from typing import Optional, Any

logger.debug("Importing file_commands module")


def read(file_path: PathLike, head: Optional[int] = None, tail: Optional[int] = None, line_separator: str = '\n', do_print: bool = False) -> str:
    """
    Read and optionally display the defined lines of a file.
    Combines `cat`, `head` and `tail`

    Args:
        file_path: The path to the file.
        head: The number of lines to display from the start (default is None).
        tail: The number of lines to display from the end (default is None).

    Returns:
        str
    """
    data = ""
    file_lines = []
    try:
        path = ensure_path(file_path).expanduser().resolve()
        if not is_file(path):
            logger.error(f"[red]File does not exist:[/red] {path}")
            return data


        with path.open("r", encoding="utf-8") as file:
            file_lines = file.readlines()
            
        # cat()
        if head is not None and tail is not None:
            for line in file_lines:
                data += line + line_separator
                if do_print:
                    console.print(line.rstrip())
        else:
            if head is not None:
                file_lines += file_lines[:head]
            if tail is not None:
                file_lines += file_lines[-tail:]
            data = line_separator.join(line for line in file_lines)
            if do_print:
                console.print(data)
        return data

    except Exception as e:
        logger.error(f"[red]Error reading file:[/red] {e}")
    
    return data

# TODO: implement more functions in file_command like
# - TODO: filter(name: PathLike, pattern: str) -> list[str]:
# - TODO: write(name: PathLike, data: Any) -> bool:
# - TODO: append(name: PathLike, data: Any)
# - TODO: create(name: PathLike, data: Any) -> bool:
# - TODO: cli for show_content(), cat() and show_head() show_tail()
