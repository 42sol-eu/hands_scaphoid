#!/usr/bin/env python3
"""
Final test file for import organizer improvements.
"""

#%% [Standard library imports]
import json
import os
import subprocess
import sys
from collections import defaultdict
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
    Union,
)

#%% [Third party imports]
from rich.console import Console

#%% [Local imports]
from base import (
    logger,
    PathLike,
)
from core_commands import (
    ensure_path,
    exists,
)

def test_function():
    """Test function that uses imports in mixed order."""
    path = Path("test")
    data = {"key": "value"}  
    console = Console()
    items = defaultdict(list)
    return path, data, console, items, logger, exists