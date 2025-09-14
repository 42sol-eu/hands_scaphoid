#!/bin/bash
# Activate the virtual environment for hands_scaphoid project
set -e 

# Get the directory of the script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
echo "Script directory: $SCRIPT_DIR"

# echo "Python: venv setup"
# uv venv .venv

source "$SCRIPT_DIR/../.venv/bin/activate"
echo "Virtual environment activated for hands_scaphoid"

echo "Python: python $(which python3)"
echo "Python: uv     $(which uv)"
echo "Available packages:"

uv pip list | grep -E "scaphoid" || echo "No hands_scaphoid packages found"

echo "DONE:--activate_venv.sh"