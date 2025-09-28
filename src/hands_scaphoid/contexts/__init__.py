"""
Contexts module for hands_scaphoid package.
----
file:
    name:        __init__.py
    uuid:        2e15cf32-d93a-4cfa-968c-d20109749955
description:     init contexts
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

#%% [Local imports]
from .ContextCore import ContextCore
from .ShellContext import ShellContext

#%% [Exports]
__all__ = [
    "ContextCore",
    "ShellContext",
]
