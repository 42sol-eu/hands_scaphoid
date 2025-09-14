# Installation

## Requirements

Hands Trapezium requires Python 3.11 or higher.

## Install from PyPI

The easiest way to install Hands Trapezium is from PyPI using pip:

```bash
pip install hands-trapezium
```

## Install from Source

You can also install directly from the GitHub repository:

```bash
pip install git+https://github.com/42sol-eu/hands_trapezium.git
```

Or clone the repository and install in development mode:

```bash
git clone https://github.com/42sol-eu/hands_trapezium.git
cd hands_trapezium
pip install -e .
```

## Development Installation

If you want to contribute to Hands Trapezium, install it in development mode with testing dependencies:

```bash
git clone https://github.com/42sol-eu/hands_trapezium.git
cd hands_trapezium
pip install -e ".[dev]"
```

This will install additional dependencies for testing and development:

- pytest for testing
- pytest-cov for coverage
- mkdocs for documentation
- black for code formatting
- mypy for type checking

## Virtual Environment

It's recommended to install Hands Trapezium in a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows)
venv\Scripts\activate

# Install Hands Trapezium
pip install hands-trapezium
```

## Using UV (Recommended)

If you're using [UV](https://github.com/astral-sh/uv) for package management:

```bash
uv add hands-trapezium
```

## Verify Installation

After installation, verify that Hands Trapezium is installed correctly:

```python
import hands_trapezium
print(hands_trapezium.__version__)
```

Or use the command-line interface:

```bash
python -m hands_trapezium --version
```

## Dependencies

Hands Trapezium has minimal dependencies:

- **rich**: For beautiful console output
- **click**: For the command-line interface

These will be automatically installed when you install Hands Trapezium.

## Platform Support

Hands Trapezium is tested on:

- Linux (Ubuntu, Debian, CentOS, etc.)
- macOS
- Windows

The library works anywhere Python runs, but some features (like command validation) may behave differently on different platforms.

## Docker

You can also use Hands Trapezium in Docker containers. Here's a simple Dockerfile:

```dockerfile
FROM python:3.11-slim

# Install Hands Trapezium
RUN pip install hands-trapezium

# Copy your script
COPY script.py /app/script.py

WORKDIR /app
CMD ["python", "script.py"]
```

## Troubleshooting

### Permission Errors

If you encounter permission errors during installation, try:

```bash
pip install --user hands-trapezium
```

### Python Version Issues

Ensure you're using Python 3.11 or higher:

```bash
python --version
```

If you have multiple Python versions, you might need to use `python3.11` or `python3` instead of `python`.

### Import Errors

If you get import errors after installation, make sure you're in the correct virtual environment and that the installation completed successfully:

```bash
pip list | grep hands-trapezium
```
