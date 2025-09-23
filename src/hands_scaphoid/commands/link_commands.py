"""
Generic link commands.
----
file:
    name:        link_commands.py
    uuid:        da25ddca-80aa-4286-a9a9-a9d4fad1083c
description:     link commands
authors:         felix@42sol.eu
project:
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from ..__base__ import logger, PathLike, Path
from typing import List, Optional, Any
from .core_commands import (
    exists,
    ensure_path,
    does_not_exists,
    get_file_extension, 
    is_directory,
    is_file,
    is_instance,
    which,
)

# TODO: link imports
# TODO: implement link commands
# TODO: implement windows lnk
# TODO: implement url files
# - TODO: cli for ln link, unlink
# - TODO: evaluate softlinks and hardlinks