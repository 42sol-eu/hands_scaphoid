# Shell Executable API Reference

The `Shell` class is the core component of hands-scaphoid, providing a secure context manager for shell command execution.

!!! info "Context Manager"
    The Shell class implements the context manager protocol, ensuring proper cleanup of resources.

=== "Basic Usage"

    ```python
    from hands_scaphoid import Shell
    
    with Shell() as shell:
        result = shell.run("echo 'Hello World'")
        print(result.stdout)
    ```

=== "With Configuration"

    ```python
    from hands_scaphoid import Shell
    
    with Shell(shell="bash", timeout=30) as shell:
        result = shell.run("ls -la")
        if result.success:
            print(result.stdout)
        else:
            print(f"Error: {result.stderr}")
    ```

!!! warning "Platform Compatibility"
    Different shell types have varying levels of support across platforms. See the Windows Shells documentation for platform-specific details.

## API documentation

::: hands_scaphoid.objects.ShellExecutable
    options:
      show_root_heading: true
      show_source: true
      members_order: source
      group_by_category: true
      show_category_heading: true
      docstring_style: google
