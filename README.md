# Hands Scaphoid - shell commands and Pythonic handling of interactions with data 

[![PyPI version](https://badge.fury.io/py/hands-scaphoid.svg)](https://badge.fury.io/py/hands-scaphoid)
[![Python Support](https://img.shields.io/pypi/pyversions/hands-scaphoid.svg)](https://pypi.org/project/hands-scaphoid/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/42sol-eu/hands_scaphoid/workflows/Tests/badge.svg)](https://github.com/42sol-eu/hands_scaphoid/actions)
[![Documentation Status](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://42sol-eu.github.io/hands_scaphoid/)

A secure shell execution context manager for Python that provides controlled command execution with environment management, command allowlisting

## 🚀 Features

- **🔒 Secure Command Execution**: Allowlist-based command execution for enhanced security
- **🌍 Environment Management**: Load and manage environment variables from files
- **🎯 Context Management**: Clean global function injection for script-like usage
- **✨ Rich Output**: Beautiful console output using Rich library
- **🔍 Type Safety**: Full type hints for better development experience
- **⚡ Easy to Use**: Both object-oriented and functional interfaces
- **🐳 Docker Integration**: - via `hands-traphezium`

## 📦 Installation

```bash
pip install hands-scaphoid
```

## 🏃‍♂️ Quick Start

### Basic Usage

```python
from hands_scaphoid import ShellContext

# Basic usage with context manager
with ShellContext() as shell:
    # Allow specific commands for security
    shell.allow(["echo", "ls"])
    
    # Execute commands securely
    result = shell.run("echo 'Hello, World!'")
    print(result.stdout)  # Output: Hello, World!
    
    # Change directory
    shell.cd("/tmp")
    
    # List files
    result = shell.run("ls -la")
    print(result.stdout)
```

### Script-style usage

```python
from hands_scaphoid import ShellContext

# Use global functions for script-like experience
with ShellContext():
    # Functions are available globally within the context
    allow(["git", "echo"])

    cd("/path/to/project")
    run("git status")
    run("echo 'Build complete'")
```

### Docker integration

> [!Note]
> Docker integration has moved to `hands_trapezium`.

```python
from hands_scaphoid import ShellContext

with ShellContext() as shell:
    allow("docker")
    
    # Execute commands in containers
    result = run_in("mycontainer", "ls /app")
    
    # Check if containers are running
    depends_on(["web", "database"])
```

### Environment management

```python
from hands_scaphoid import ShellContext

# Load environment from file
with ShellContext(env_file=".env") as shell:
    db_url = shell.get_env_var("DATABASE_URL")
    
    # Set additional variables
    set_env_var("DEPLOYMENT", "production")
```

## Security model

Hands scaphoid uses an allowlist-based security model:

1. **No commands are allowed by default** 🚫
2. **Commands must be explicitly allowed** using `allow()` ✅
3. **Only the command name is checked**, not arguments
4. **Commands are validated** to exist on the system

```python
with ShellContext() as shell:
    # This will fail - command not allowed
    try:   
        run("rm -rf /")
    except PermissionError:
        print("Security working! 🛡️")
    
    # Allow the command first
    allow("echo")
    run("echo 'This works!'")  # ✅ This succeeds
```

## 📚 Documentation

For comprehensive documentation, visit: **[https://42sol-eu.github.io/hands_scaphoid](https://42sol-eu.github.io/hands_scaphoid)**

## 🎯 Use Cases

- **Deployment scripts**: Secure automation scripts with command validation
- **CI/CD pipelines**: Controlled command execution in build processes
- **System administration**: Safe system management scripts
- **Docker workflows**: Seamless container command execution
- **Development tools**: Build tools and development automation

## Example: Deployment Script

```python
#!/usr/bin/env python3
"""
Simple deployment script using Hands/Scaphoid
"""
from hands_scaphoid import ShellContext

def deploy_application():
    with ShellContext(cwd="/app") as shell:
        commands = ["git", "docker", "echo"]
        allow(commands)
        # Allow required commands
        
        try:
            # Deploy workflow
            run("git pull origin main")
            run("docker build -t eden:latest .")
            depends_on(["database", "redis"])  # Check dependencies
            run("docker run -d --name eden eden:latest")
            
            print("✅ Deployment successful!")
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    deploy_application()
```

## 🔧 Requirements

- Python 3.11+
- Rich library for console output
- Click for CLI interface

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

```bash
git clone https://github.com/42sol-eu/hands_scaphoid.git
cd hands_scaphoid
pip install -e ".[dev]"
```

### Running Tests

```bash
pytest
```

### Building Documentation

```bash
mkdocs serve
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**Andreas Häberle** - [42sol-eu](https://github.com/42sol-eu)

## 🌟 Support

If you find this project helpful, please consider giving it a star on GitHub! ⭐

## 📝 Changelog

See [CHANGELOG.md](CHANGELOG.md) for a list of changes and version history.