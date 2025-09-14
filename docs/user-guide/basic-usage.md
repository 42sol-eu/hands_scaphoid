# Basic Usage

This guide covers the basic usage patterns of Hands Trapezium.

## Shell Class

The `Shell` class is the core of Hands Trapezium, providing secure command execution.

### Creating a Shell Instance

```python
from hands_scaphoid import Shell

# Basic shell with current directory
shell = Shell()

# Shell with custom working directory
shell = Shell(cwd="/path/to/working/dir")

# Shell with custom environment
shell = Shell(env={"PATH": "/usr/bin:/bin"})

# Shell with environment file
shell = Shell(env_file="/path/to/.env")
```

### Allowing Commands

Before executing any command, you must explicitly allow it:

```python
# Allow single commands
shell.allow("echo")
shell.allow("ls")
shell.allow("git")

# Check if command exists and allow it
if shell.allow("docker"):
    print("Docker is available")
else:
    print("Docker not found on system")
```

### Executing Commands

```python
# Basic command execution
result = shell.run("echo 'Hello World'")
print(result.stdout)  # Output: Hello World

# Command with timeout
result = shell.run("sleep 1", timeout=5)

# Command without error checking
result = shell.run("ls /nonexistent", check=False)
if result.returncode != 0:
    print("Command failed")

# Capture output as bytes instead of text
result = shell.run("cat binary_file", text=False)
```

### Working with Directories

```python
# Change directory
shell.cd("/tmp")
print(shell.cwd)  # Output: /tmp

# Use relative paths
shell.cd("../")
shell.cd("subdir")

# Go to absolute path
shell.cd("/home/user/project")
```

### Environment Variables

```python
# Get environment variable
db_url = shell.get_env_var("DATABASE_URL")

# Set environment variable
shell.set_env_var("NODE_ENV", "production")

# Check if variable exists
if shell.get_env_var("API_KEY"):
    print("API key is set")
```

## ShellContext Manager

The `ShellContext` provides a cleaner way to use Shell functionality.

### Basic Context Usage

```python
from hands_scaphoid import ShellContext

with ShellContext() as shell:
    shell.allow("echo")
    shell.allow("ls")
    
    result = shell.run("echo 'Hello from context'")
    print(result.stdout)
    
    shell.cd("/tmp")
    result = shell.run("ls")
    print(result.stdout)
```

### Global Functions Style

```python
with ShellContext():
    # These functions are now available globally
    allow("git")
    allow("echo")
    allow("npm")
    
    # Change to project directory
    cd("/path/to/project")
    
    # Run build commands
    run("git pull origin main")
    run("npm install")
    run("npm run build")
    
    # Show completion message
    run("echo 'Build complete!'")
```

### Custom Configuration

```python
# Custom working directory and environment
with ShellContext(cwd="/app", env_file=".env.production") as shell:
    shell.allow("docker")
    shell.allow("docker-compose")
    
    # Deploy application
    shell.run("docker-compose down")
    shell.run("docker-compose up -d")
```

## Error Handling

### Security Errors

```python
with ShellContext() as shell:
    # This will raise PermissionError
    try:
        shell.run("rm important_file")
    except PermissionError as e:
        print(f"Security prevented: {e}")
    
    # Allow the command first
    shell.allow("rm")
    shell.run("rm temporary_file")  # Now works
```

### Command Execution Errors

```python
import subprocess

with ShellContext() as shell:
    shell.allow("ls")
    
    try:
        shell.run("ls /nonexistent/directory")
    except subprocess.CalledProcessError as e:
        print(f"Command failed with exit code {e.returncode}")
        print(f"Error output: {e.stderr}")
```

### Timeout Handling

```python
try:
    with ShellContext() as shell:
        shell.allow("sleep")
        shell.run("sleep 10", timeout=5)
except subprocess.TimeoutExpired:
    print("Command timed out")
```

## Practical Examples

### Simple Script Runner

```python
from hands_scaphoid import ShellContext

def run_tests():
    """Run project tests."""
    with ShellContext() as shell:
        # Allow required commands
        shell.allow("python")
        shell.allow("pytest")
        
        # Change to project directory
        shell.cd("/path/to/project")
        
        # Run tests
        try:
            result = shell.run("pytest tests/")
            if result.returncode == 0:
                print("✅ All tests passed!")
            else:
                print("❌ Tests failed!")
                return False
        except Exception as e:
            print(f"❌ Test execution failed: {e}")
            return False
    
    return True
```

### Environment Setup Script

```python
def setup_development_environment():
    """Set up development environment."""
    with ShellContext(cwd="/app") as shell:
        # Allow necessary commands
        commands = ["git", "python", "pip", "npm"]
        for cmd in commands:
            if not shell.allow(cmd):
                print(f"❌ {cmd} not found")
                return False
        
        # Clone repository
        shell.run("git clone https://github.com/user/repo.git .")
        
        # Install Python dependencies
        shell.run("pip install -r requirements.txt")
        
        # Install Node.js dependencies
        shell.run("npm install")
        
        # Set up environment file
        shell.set_env_var("ENVIRONMENT", "development")
        
        print("✅ Development environment ready!")
    
    return True
```

### File Processing Pipeline

```python
def process_files(input_dir: str, output_dir: str):
    """Process files in a directory."""
    with ShellContext(cwd=input_dir) as shell:
        # Allow file processing commands
        shell.allow("find")
        shell.allow("convert")  # ImageMagick
        shell.allow("mkdir")
        
        # Create output directory
        shell.run(f"mkdir -p {output_dir}")
        
        # Find and process image files
        result = shell.run("find . -name '*.jpg' -o -name '*.png'")
        
        for file_path in result.stdout.strip().split('\n'):
            if file_path:
                output_file = f"{output_dir}/{file_path}"
                shell.run(f"convert {file_path} -resize 800x600 {output_file}")
                print(f"Processed: {file_path}")
```

## Tips and Best Practices

### Security Best Practices

1. **Allowlist Only Required Commands**: Only allow commands you actually need
2. **Validate Input**: Validate any user input before using in commands
3. **Use Specific Commands**: Prefer specific commands over generic ones
4. **Review Command Lists**: Regularly review what commands your scripts allow

### Performance Tips

1. **Reuse Shell Instances**: Create once and reuse for multiple commands
2. **Batch Operations**: Group related commands in the same context
3. **Avoid Unnecessary Captures**: Set `capture_output=False` when you don't need output

### Error Handling

1. **Use try/except**: Always handle potential errors
2. **Check Return Codes**: Check command success before proceeding
3. **Provide Meaningful Messages**: Give users clear error messages
4. **Graceful Degradation**: Have fallback options when commands fail

### Code Organization

1. **Separate Concerns**: Keep command logic separate from business logic
2. **Use Functions**: Wrap command sequences in functions
3. **Document Commands**: Comment what each command does
4. **Version Control**: Track changes to command sequences
