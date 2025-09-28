#!/usr/bin/env python3
"""
Base module for hands-trapezium package.

This module provides common constants and imports used throughout the package.

File:
    name: __base__.py
    uuid: e9f42686-b123-4b3f-bf33-59e1b86396f3
    date: 2025-09-12

Description:
    Shell context runner base module

Project:
    name: hands/scapohoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4

Authors: ["Andreas Häberle"]
Projects: ["hands/palm/trapezium"]
"""

#%% [ Typing imports]
from typing import (
    Any, 
    Callable,
    Dict,
    Generator,
    IO,
    List,
    Optional, 
    Union,
)

PathLike = Union[str, Path]

from contextlib import contextmanager as context_manager

#%% [Standard library imports]
from abc import ABC as AbstractBaseClass
from abc import abstractmethod as abstract_method
import logging
import os
from pathlib import Path
import subprocess
import sys
import time

#%% [Third party imports]
from rich import print
from rich.console import Console
from rich.logging import RichHandler

#%% [Constants]
DEBUG_MODE = False
ENABLE_TRACEBACK = DEBUG_MODE

if ENABLE_TRACEBACK:
    from rich import traceback

    traceback.install()

# Convenience constants
no = False
yes = True
false = False
true = True
G_debug = DEBUG_MODE

#%% [Local setup] 
# Create console instance for rich output
console = Console()

logging.basicConfig(
    level=logging.DEBUG if DEBUG_MODE else logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(console=console, rich_tracebacks=True)],
)

#%% [Exports]
__all__ = [
    "os",
    "subprocess",
    "sys",
    "time",
    "print",
    "console",
    "no",
    "yes",
    "G_debug",
    "DEBUG_MODE",
    "ENABLE_TRACEBACK",
]

logger = logging.getLogger("hands_scaphoid")