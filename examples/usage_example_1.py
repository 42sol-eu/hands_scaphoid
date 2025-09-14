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