# Windows Shell Support

Hands Scaphoid provides specialized shell classes for Windows environments that make cross-platform development easier.

## PowerShellShell

The `PowerShellShell` class automatically translates common Unix commands to their PowerShell equivalents, allowing you to write cross-platform scripts using familiar Unix command syntax.

### Basic Usage

```python
from hands_scaphoid import PowerShellShell

# Create a PowerShell shell
shell = PowerShellShell()

# Allow commands (both Unix and PowerShell versions work)
shell.allow("ls")         # Automatically translated to Get-ChildItem
shell.allow("cp")         # Automatically translated to Copy-Item
shell.allow("echo")       # Automatically translated to Write-Output

# Run Unix commands - they get translated automatically
result = shell.run("ls -la")           # Becomes: Get-ChildItem -Force -Detailed
result = shell.run("cp file1 file2")   # Becomes: Copy-Item "file1" "file2"
result = shell.run("echo 'Hello'")     # Becomes: Write-Output 'Hello'
```

### Command Translation Examples

| Unix Command | PowerShell Translation |
|-------------|----------------------|
| `ls` | `Get-ChildItem` |
| `ls -la` | `Get-ChildItem -Force -Detailed` |
| `cp source dest` | `Copy-Item "source" "dest"` |
| `cp -r folder dest` | `Copy-Item "folder" "dest" -Recurse` |
| `rm file` | `Remove-Item "file"` |
| `rm -rf folder` | `Remove-Item "folder" -Recurse -Force` |
| `cat file` | `Get-Content file` |
| `pwd` | `Get-Location` |
| `echo text` | `Write-Output text` |
| `ps` | `Get-Process` |
| `whoami` | `[System.Security.Principal.WindowsIdentity]::GetCurrent().Name` |
| `hostname` | `$env:COMPUTERNAME` |

### PowerShell Executable Detection

The class automatically detects the best PowerShell executable:
- Tries `pwsh.exe` (PowerShell Core) first
- Falls back to `powershell.exe` (Windows PowerShell) if Core is not available

## WslShell

The `WslShell` class allows you to execute Linux commands through Windows Subsystem for Linux (WSL), giving you access to a full Linux environment from your Python scripts.

### Basic Usage

```python
from hands_scaphoid import WslShell

# Create a WSL shell (uses default WSL distribution)
shell = WslShell()

# Or specify a specific distribution
shell = WslShell(distribution="Ubuntu")

# Allow Linux commands
shell.allow("ls")
shell.allow("grep")
shell.allow("awk")

# Run Linux commands
result = shell.run("ls -la")
result = shell.run("grep 'pattern' file.txt")
result = shell.run("uname -a")
```

### WSL Distribution Management

```python
# List available WSL distributions
distributions = shell.list_distributions()
print("Available distributions:", distributions)

# Switch to a different distribution
success = shell.set_distribution("Debian")
if success:
    print("Switched to Debian")
else:
    print("Failed to switch distribution")
```

### Command Wrapping

WSL commands are automatically wrapped for execution:
```python
# When you run: shell.run("ls -la")
# It actually executes: ["wsl.exe", "--", "sh", "-c", "ls -la"]
```

## Convenience Functions

```python
from hands_scaphoid import create_powershell_shell, create_wsl_shell

# Create shells using convenience functions
ps_shell = create_powershell_shell()
wsl_shell = create_wsl_shell("Ubuntu")

# Get available WSL distributions
from hands_scaphoid.WindowsShells import get_available_wsl_distributions
distributions = get_available_wsl_distributions()
```

## Cross-Platform Script Example

```python
import platform
from hands_scaphoid import Shell, PowerShellShell, WslShell

def cross_platform_example():
    # Choose shell based on platform and requirements
    if platform.system() == "Windows":
        # Option 1: Use PowerShell for Windows compatibility
        shell = PowerShellShell()
        
        # Option 2: Use WSL for Linux compatibility
        # shell = WslShell()
    else:
        # Use regular shell on Unix systems
        shell = Shell()
    
    # Allow commands (works for all shell types)
    shell.allow("ls")
    shell.allow("echo")
    
    # Run commands using Unix syntax
    result = shell.run("ls")
    result = shell.run("echo 'Cross-platform hello'")
    
    print("Directory listing succeeded:", result.returncode == 0)
```

## Error Handling

```python
from hands_scaphoid import WslShell

try:
    # This will raise RuntimeError if WSL is not available
    shell = WslShell()
    shell.allow("ls")
    result = shell.run("ls")
except RuntimeError as e:
    print(f"WSL not available: {e}")
    # Fallback to PowerShell or regular shell
    shell = PowerShellShell()
    shell.allow("ls")
    result = shell.run("ls")
```

## Security

Both Windows shell classes inherit the same security model as the base `Shell` class:
- Commands must be explicitly allowed using `allow()`
- Only the command name is checked, not arguments
- Commands are validated to exist on the system when possible

## Requirements

- **PowerShellShell**: Works on any Windows system with PowerShell installed
- **WslShell**: Requires Windows Subsystem for Linux (WSL) to be installed and configured

## Platform Behavior

- **Windows**: Both classes work as described above
- **Non-Windows**: Both classes fall back to regular shell behavior for cross-platform compatibility
