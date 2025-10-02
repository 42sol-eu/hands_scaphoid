# Examples

This page provides practical examples of using Hands Scaphoid in real-world scenarios.

## Deployment Scripts

!!! note

    Deployment scripts 


### Simple Web App Deployment

```python
#!/usr/bin/env python3
"""
Deploy a web application using Hands Scaphoid.
"""

from hands_scaphoid import ShellContext
import sys

def deploy_web_app(branch="main", environment="production"):
    """Deploy web application."""
    
    print(f"🚀 Deploying from branch '{branch}' to '{environment}'...")
    
    with ShellContext(cwd="/app") as shell:
        # Allow required commands
        required_commands = ["git", "docker", "docker-compose", "echo"]
        for cmd in required_commands:
            if not shell.allow(cmd):
                print(f"❌ Required command '{cmd}' not found")
                return False
        
        try:
            # Pull latest code
            print("📥 Pulling latest code...")
            shell.run(f"git pull origin {branch}")
            
            # Build new Docker image
            print("🔨 Building Docker image...")
            shell.run("docker build -t myapp:latest .")
            
            # Stop old containers
            print("🛑 Stopping old containers...")
            shell.run("docker-compose down")
            
            # Start new containers
            print("▶️ Starting new containers...")
            shell.run("docker-compose up -d")
            
            # Verify deployment
            print("✅ Verifying deployment...")
            result = shell.run("docker-compose ps")
            if "Up" in result.stdout:
                print("✅ Deployment successful!")
                return True
            else:
                print("❌ Deployment verification failed")
                return False
                
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Deploy web application")
    parser.add_argument("--branch", default="main", help="Git branch to deploy")
    parser.add_argument("--env", default="production", help="Environment")
    
    args = parser.parse_args()
    
    if not deploy_web_app(args.branch, args.env):
        sys.exit(1)
```

### Database Migration Script

```python
#!/usr/bin/env python3
"""
Database migration script with backup.
"""

from hands_scaphoid import ShellContext
from datetime import datetime
import sys

def migrate_database():
    """Run database migrations with backup."""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.sql"
    
    with ShellContext() as shell:
        # Allow database commands
        for cmd in ["pg_dump", "psql", "echo"]:
            if not shell.allow(cmd):
                print(f"❌ Database command '{cmd}' not available")
                return False
        
        try:
            # Create backup
            print("💾 Creating database backup...")
            shell.run(f"pg_dump myapp_prod > {backup_file}")
            
            # Run migrations
            print("🔄 Running migrations...")
            shell.run("psql myapp_prod < migrations/latest.sql")
            
            # Verify migration
            print("✅ Migration completed successfully!")
            print(f"💾 Backup saved as: {backup_file}")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print(f"🔄 Restoring from backup: {backup_file}")
            try:
                shell.run(f"psql myapp_prod < {backup_file}")
                print("✅ Database restored from backup")
            except Exception as restore_error:
                print(f"❌ Backup restoration failed: {restore_error}")
            return False

if __name__ == "__main__":
    if not migrate_database():
        sys.exit(1)
```

## Development Workflows

### Project Setup Automation

```python
#!/usr/bin/env python3
"""
Automated project setup script.
"""

from hands_scaphoid import ShellContext
import sys
import os

def setup_project(project_name: str, template: str = "python"):
    """Set up a new project from template."""
    
    project_dir = f"/workspace/{project_name}"
    
    with ShellContext() as shell:
        # Allow development tools
        dev_tools = ["git", "python", "pip", "npm", "mkdir", "cp", "echo"]
        for tool in dev_tools:
            shell.allow(tool)
        
        try:
            # Create project directory
            print(f"📁 Creating project directory: {project_dir}")
            shell.run(f"mkdir -p {project_dir}")
            shell.cd(project_dir)
            
            # Initialize git repository
            print("🔧 Initializing Git repository...")
            shell.run("git init")
            
            if template == "python":
                setup_python_project(shell, project_name)
            elif template == "node":
                setup_node_project(shell, project_name)
            else:
                print(f"❌ Unknown template: {template}")
                return False
            
            # Create initial commit
            print("💾 Creating initial commit...")
            shell.run("git add .")
            shell.run(f"git commit -m 'Initial commit for {project_name}'")
            
            print(f"✅ Project '{project_name}' set up successfully!")
            print(f"📁 Location: {project_dir}")
            return True
            
        except Exception as e:
            print(f"❌ Project setup failed: {e}")
            return False

def setup_python_project(shell, project_name):
    """Set up Python project structure."""
    print("🐍 Setting up Python project...")
    
    # Create Python project structure
    shell.run(f"mkdir -p {project_name}")
    shell.run(f"mkdir -p tests")
    shell.run(f"mkdir -p docs")
    
    # Create basic files
    pyproject_content = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = ""
requires-python = ">=3.11"
dependencies = []
'''
    
    with open("pyproject.toml", "w") as f:
        f.write(pyproject_content)
    
    # Create virtual environment
    shell.run("python -m venv .venv")
    
    print("✅ Python project structure created")

def setup_node_project(shell, project_name):
    """Set up Node.js project structure."""
    print("📦 Setting up Node.js project...")
    
    # Initialize npm project
    shell.run("npm init -y")
    
    # Create basic structure
    shell.run("mkdir -p src")
    shell.run("mkdir -p tests")
    shell.run("mkdir -p docs")
    
    print("✅ Node.js project structure created")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: setup_project.py <project_name> [template]")
        sys.exit(1)
    
    project_name = sys.argv[1]
    template = sys.argv[2] if len(sys.argv) > 2 else "python"
    
    if not setup_project(project_name, template):
        sys.exit(1)
```

### Automated Testing Pipeline

```python
#!/usr/bin/env python3
"""
Comprehensive testing pipeline.
"""

from hands_scaphoid import ShellContext
import sys

def run_test_pipeline():
    """Run complete testing pipeline."""
    
    with ShellContext() as shell:
        # Allow testing tools
        test_tools = ["python", "pytest", "flake8", "mypy", "black", "echo"]
        for tool in test_tools:
            if not shell.allow(tool):
                print(f"⚠️ Testing tool '{tool}' not available")
        
        tests_passed = True
        
        # Code formatting check
        print("🎨 Checking code formatting...")
        try:
            shell.run("black --check src tests")
            print("✅ Code formatting OK")
        except Exception:
            print("❌ Code formatting issues found")
            tests_passed = False
        
        # Linting
        print("🔍 Running linter...")
        try:
            shell.run("flake8 src tests")
            print("✅ Linting passed")
        except Exception:
            print("❌ Linting issues found")
            tests_passed = False
        
        # Type checking
        print("🔬 Type checking...")
        try:
            shell.run("mypy src")
            print("✅ Type checking passed")
        except Exception:
            print("❌ Type checking issues found")
            tests_passed = False
        
        # Unit tests
        print("🧪 Running unit tests...")
        try:
            result = shell.run("pytest tests/ -v --cov")
            print("✅ Unit tests passed")
            
            # Extract coverage percentage
            coverage_line = [line for line in result.stdout.split('\n') 
                           if 'TOTAL' in line and '%' in line]
            if coverage_line:
                print(f"📊 {coverage_line[0]}")
                
        except Exception:
            print("❌ Unit tests failed")
            tests_passed = False
        
        if tests_passed:
            print("\n🎉 All tests passed! Ready for deployment.")
            return True
        else:
            print("\n❌ Some tests failed. Please fix issues before deployment.")
            return False

if __name__ == "__main__":
    if not run_test_pipeline():
        sys.exit(1)
```

## DevOps Automation

### Container Management

```python
#!/usr/bin/env python3
"""
Docker container management utilities.
"""

from hands_scaphoid import ShellContext
import json
import sys

def manage_containers(action: str, service: str = None):
    """Manage Docker containers."""
    
    with ShellContext() as shell:
        shell.allow("docker")
        shell.allow("docker-compose")
        
        try:
            if action == "status":
                show_container_status(shell)
            elif action == "logs":
                show_container_logs(shell, service)
            elif action == "restart":
                restart_service(shell, service)
            elif action == "health":
                check_health(shell)
            else:
                print(f"❌ Unknown action: {action}")
                return False
                
            return True
            
        except Exception as e:
            print(f"❌ Container management failed: {e}")
            return False

def show_container_status(shell):
    """Show status of all containers."""
    print("📊 Container Status:")
    print("-" * 50)
    
    result = shell.run("docker-compose ps")
    print(result.stdout)

def show_container_logs(shell, service):
    """Show logs for a specific service."""
    if not service:
        print("❌ Service name required for logs")
        return
    
    print(f"📝 Logs for {service}:")
    print("-" * 50)
    
    result = shell.run(f"docker-compose logs --tail=50 {service}")
    print(result.stdout)

def restart_service(shell, service):
    """Restart a specific service."""
    if not service:
        print("❌ Service name required for restart")
        return
    
    print(f"🔄 Restarting {service}...")
    shell.run(f"docker-compose restart {service}")
    print(f"✅ {service} restarted")

def check_health(shell):
    """Check health of all services."""
    print("🏥 Health Check:")
    print("-" * 50)
    
    # Get container info
    result = shell.run("docker ps --format '{{.Names}}\t{{.Status}}'")
    
    for line in result.stdout.strip().split('\n'):
        if line:
            name, status = line.split('\t', 1)
            if 'healthy' in status.lower():
                print(f"✅ {name}: {status}")
            elif 'unhealthy' in status.lower():
                print(f"❌ {name}: {status}")
            else:
                print(f"⚠️ {name}: {status}")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Container management")
    parser.add_argument("action", choices=["status", "logs", "restart", "health"])
    parser.add_argument("--service", help="Service name")
    
    args = parser.parse_args()
    
    if not manage_containers(args.action, args.service):
        sys.exit(1)
```

### System Monitoring

```python
#!/usr/bin/env python3
"""
System monitoring and alerts.
"""

from hands_scaphoid import ShellContext
import time
import sys

def monitor_system(duration_minutes: int = 5):
    """Monitor system resources and services."""
    
    end_time = time.time() + (duration_minutes * 60)
    
    with ShellContext() as shell:
        # Allow monitoring commands
        monitor_commands = ["ps", "df", "free", "top", "docker", "curl"]
        for cmd in monitor_commands:
            shell.allow(cmd)
        
        print(f"🔍 Starting system monitoring for {duration_minutes} minutes...")
        
        while time.time() < end_time:
            print(f"\n📊 System Check - {time.strftime('%H:%M:%S')}")
            print("-" * 50)
            
            # Check disk usage
            check_disk_usage(shell)
            
            # Check memory usage
            check_memory_usage(shell)
            
            # Check running services
            check_services(shell)
            
            # Check application health
            check_application_health(shell)
            
            # Wait before next check
            time.sleep(30)
        
        print("\n✅ Monitoring completed")

def check_disk_usage(shell):
    """Check disk usage."""
    result = shell.run("df -h /")
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        usage_line = lines[1].split()
        usage_percent = usage_line[4].rstrip('%')
        
        if int(usage_percent) > 90:
            print(f"🔴 Disk usage: {usage_percent}% (CRITICAL)")
        elif int(usage_percent) > 80:
            print(f"🟡 Disk usage: {usage_percent}% (WARNING)")
        else:
            print(f"🟢 Disk usage: {usage_percent}% (OK)")

def check_memory_usage(shell):
    """Check memory usage."""
    result = shell.run("free -m")
    lines = result.stdout.strip().split('\n')
    if len(lines) > 1:
        mem_line = lines[1].split()
        total = int(mem_line[1])
        used = int(mem_line[2])
        usage_percent = (used / total) * 100
        
        if usage_percent > 90:
            print(f"🔴 Memory usage: {usage_percent:.1f}% (CRITICAL)")
        elif usage_percent > 80:
            print(f"🟡 Memory usage: {usage_percent:.1f}% (WARNING)")
        else:
            print(f"🟢 Memory usage: {usage_percent:.1f}% (OK)")

def check_services(shell):
    """Check running services."""
    try:
        result = shell.run("docker-compose ps", check=False)
        if result.returncode == 0:
            # Count running containers
            running = result.stdout.count("Up")
            total = len([line for line in result.stdout.split('\n') 
                        if line and not line.startswith('Name')])
            
            if running == total:
                print(f"🟢 Services: {running}/{total} running (OK)")
            else:
                print(f"🔴 Services: {running}/{total} running (ISSUES)")
        else:
            print("⚠️ Could not check services")
    except Exception:
        print("⚠️ Service check failed")

def check_application_health(shell):
    """Check application health endpoints."""
    try:
        result = shell.run("curl -s -o /dev/null -w '%{http_code}' http://localhost:8080/health", 
                          check=False)
        status_code = result.stdout.strip()
        
        if status_code == "200":
            print("🟢 Application health: OK")
        else:
            print(f"🔴 Application health: HTTP {status_code}")
    except Exception:
        print("🔴 Application health: UNREACHABLE")

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="System monitoring")
    parser.add_argument("--duration", type=int, default=5, 
                       help="Monitoring duration in minutes")
    
    args = parser.parse_args()
    
    try:
        monitor_system(args.duration)
    except KeyboardInterrupt:
        print("\n⏹️ Monitoring stopped by user")
```

## File Processing

### Batch Image Processing

```python
#!/usr/bin/env python3
"""
Batch image processing with ImageMagick.
"""

from hands_scaphoid import ShellContext
import os
import sys

def process_images(input_dir: str, output_dir: str, 
                  width: int = 800, height: int = 600, quality: int = 85):
    """Process images in batch."""
    
    with ShellContext(cwd=input_dir) as shell:
        # Allow image processing commands
        shell.allow("find")
        shell.allow("convert")  # ImageMagick
        shell.allow("mkdir")
        shell.allow("identify")
        
        try:
            # Create output directory
            shell.run(f"mkdir -p {output_dir}")
            
            # Find image files
            result = shell.run("find . -type f \\( -iname '*.jpg' -o -iname '*.jpeg' -o -iname '*.png' -o -iname '*.gif' \\)")
            
            image_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
            
            if not image_files:
                print("❌ No image files found")
                return False
            
            print(f"📷 Found {len(image_files)} images to process")
            
            processed = 0
            for image_file in image_files:
                try:
                    # Get original image info
                    info_result = shell.run(f"identify -format '%wx%h' '{image_file}'")
                    original_size = info_result.stdout.strip()
                    
                    # Generate output filename
                    output_file = os.path.join(output_dir, 
                                             os.path.basename(image_file))
                    
                    # Process image
                    convert_cmd = (f"convert '{image_file}' "
                                 f"-resize {width}x{height}> "
                                 f"-quality {quality} "
                                 f"'{output_file}'")
                    
                    shell.run(convert_cmd)
                    
                    # Get new image info
                    new_info_result = shell.run(f"identify -format '%wx%h' '{output_file}'")
                    new_size = new_info_result.stdout.strip()
                    
                    print(f"✅ {image_file}: {original_size} → {new_size}")
                    processed += 1
                    
                except Exception as e:
                    print(f"❌ Failed to process {image_file}: {e}")
            
            print(f"\n🎉 Processed {processed}/{len(image_files)} images")
            return processed > 0
            
        except Exception as e:
            print(f"❌ Image processing failed: {e}")
            return False

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Batch image processing")
    parser.add_argument("input_dir", help="Input directory")
    parser.add_argument("output_dir", help="Output directory")
    parser.add_argument("--width", type=int, default=800, help="Max width")
    parser.add_argument("--height", type=int, default=600, help="Max height")
    parser.add_argument("--quality", type=int, default=85, help="JPEG quality")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.input_dir):
        print(f"❌ Input directory does not exist: {args.input_dir}")
        sys.exit(1)
    
    if not process_images(args.input_dir, args.output_dir, 
                         args.width, args.height, args.quality):
        sys.exit(1)
```

These examples demonstrate the flexibility and power of Hands Scaphoid for various automation tasks while maintaining security through command allowlisting.
# Getting Started

Welcome to Hands Scaphoid! This guide will help you get up and running quickly with secure shell command execution in Python.

## What is Hands Scaphoid?

Hands Scaphoid is a Python library that provides a secure and convenient way to execute shell commands with:

- **Security**: Command allowlisting prevents execution of unauthorized commands
- **Environment Management**: Load environment variables from files
- **Docker Integration**: Execute commands in Docker containers
- **Clean API**: Both object-oriented and script-like interfaces

## Basic Concepts

### Shell Class

The `Shell` class is the core of Hands Scaphoid. It provides secure command execution with environment management.

```python
from hands_scaphoid import Shell

# Create a shell instance
shell = Shell(cwd="/path/to/working/dir")

# Allow commands before executing them
shell.allow("echo")
shell.allow("ls")

# Execute commands
result = shell.run("echo 'Hello, World!'")
print(result.stdout)  # Output: Hello, World!
```

### ShellContext Manager

The `ShellContext` provides a more convenient way to use Shell functionality with automatic cleanup.

```python
from hands_scaphoid import ShellContext

with ShellContext(cwd="/tmp") as shell:
    shell.allow("pwd")
    result = shell.run("pwd")
    print(result.stdout)  # Output: /tmp
```

### Global Functions

For script-like usage, ShellContext can inject functions globally:

```python
from hands_scaphoid import ShellContext

with ShellContext():
    # These functions are now available globally
    allow("echo")
    allow("git")
    
    cd("/path/to/project")
    run("git status")
    run("echo 'Done!'")
```

## Your First Script

Let's create a simple script that demonstrates the key features:

```python
#!/usr/bin/env python3
"""
Simple deployment script using Hands Scaphoid
"""

from hands_scaphoid import ShellContext

def deploy_app():
    with ShellContext(cwd="/app") as shell:
        # Allow the commands we need
        shell.allow("git")
        shell.allow("docker")
        shell.allow("echo")
        
        try:
            # Pull latest code
            print("Pulling latest code...")
            shell.run("git pull origin main")
            
            # Build Docker image
            print("Building Docker image...")
            shell.run("docker build -t myapp:latest .")
            
            # Check if container is running
            print("Checking dependencies...")
            shell.depends_on(["database", "redis"])
            
            # Deploy new version
            print("Deploying new version...")
            shell.run("docker run -d --name myapp myapp:latest")
            
            print("Deployment complete!")
            
        except Exception as e:
            print(f"Deployment failed: {e}")
            return False
    
    return True

if __name__ == "__main__":
    deploy_app()
```

## Security Model

Hands Scaphoid uses an allowlist-based security model:

1. **No commands are allowed by default**
2. **Commands must be explicitly allowed** using `allow()`
3. **Only the command name is checked**, not arguments
4. **Commands are validated** to exist on the system

```python
with ShellContext() as shell:
    # This will fail - command not allowed
    try:
        shell.run("rm -rf /")
    except PermissionError:
        print("Security working!")
    
    # Allow the command first
    shell.allow("echo")
    shell.run("echo 'This works!'")  # This succeeds
```

## Environment Management

Load environment variables from files:

```python
# Create an .env file
with open(".env", "w") as f:
    f.write("DATABASE_URL=postgresql://localhost/mydb\n")
    f.write("API_KEY=secret123\n")

# Use the environment file
with ShellContext(env_file=".env") as shell:
    db_url = shell.get_env_var("DATABASE_URL")
    print(f"Database URL: {db_url}")
    
    # Set additional variables
    shell.set_env_var("DEPLOYMENT", "production")
```

## Error Handling

Hands Scaphoid provides detailed error handling:

```python
from hands_scaphoid import ShellContext
import subprocess

with ShellContext() as shell:
    shell.allow("ls")
    
    try:
        # This will fail if directory doesn't exist
        result = shell.run("ls /nonexistent", check=True)
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
    except PermissionError as e:
        print(f"Security error: {e}")
```

## Next Steps

Now that you understand the basics, explore these advanced topics:

- [Basic Usage](user-guide/basic-usage.md) - Detailed usage examples
- [PowerShell](api/objects/power-shell.md) - Windows PowerShell and WSL support
- [SshShell](api/objects/ssh-shell.md) - Windows PowerShell and WSL support
- [WslShell](api/objects/wsl-shell.md) - Windows PowerShell and WSL support
- [API Reference](api/objects/shell-executable.md) - Complete API documentation
# Hands Scaphoid

[![PyPI version](https://badge.fury.io/py/hands-trapezium.svg)](https://badge.fury.io/py/hands-trapezium)
[![Python Support](https://img.shields.io/pypi/pyversions/hands-trapezium.svg)](https://pypi.org/project/hands-trapezium/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/42sol-eu/hands_scaphoid/workflows/Tests/badge.svg)](https://github.com/42sol-eu/hands_scaphoid/actions)

A secure shell execution context manager for Python that provides controlled command execution with environment management, command allowlisting, and Docker integration.

## Features

- **Secure Command Execution**: Allowlist-based command execution for enhanced security
- **Environment Management**: Load and manage environment variables from files
- **Docker Integration**: Execute commands inside Docker containers
- **Context Management**: Clean global function injection for script-like usage
- **Rich Output**: Beautiful console output using Rich library
- **Type Safety**: Full type hints for better development experience

## Quick Start

```python
from hands_scaphoid import ShellContext

# Basic usage with context manager
with ShellContext() as shell:
    # Allow specific commands
    shell.allow("echo")
    shell.allow("ls")
    
    # Execute commands securely
    result = shell.run("echo 'Hello, World!'")
    print(result.stdout)
    
    # Change directory
    shell.cd("/tmp")
    
    # List files
    result = shell.run("ls -la")
    print(result.stdout)
```

## Global Function Style

```python
from hands_scaphoid import ShellContext

# Use global functions for script-like experience
with ShellContext():
    allow("git")
    allow("echo")
    
    # Functions are available globally within the context
    cd("/path/to/project")
    run("git status")
    run("echo 'Build complete'")
```

## Docker Integration

```python
from hands_scaphoid import ShellContext

with ShellContext() as shell:
    shell.allow("docker")
    
    # Execute commands in containers
    result = shell.run_in("mycontainer", "ls /app")
    
    # Check if containers are running
    shell.depends_on(["web", "database"])
```

## Installation

```bash
pip install hands-trapezium
```

## Requirements

- Python 3.11+
- Rich library for console output
- Click for CLI interface

## Documentation

For comprehensive documentation, visit: [https://42sol-eu.github.io/hands_scaphoid](https://42sol-eu.github.io/hands_scaphoid)

