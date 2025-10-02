# Plugin Features Test

This page demonstrates the mkdocs-material plugins: admonitions, tabs, and API includes.

## Admonitions (Callouts)

Admonitions provide visually distinct callout boxes for different types of information.

!!! note "Information Note"
    This is a note admonition. Use it to provide helpful information to users.

!!! tip "Pro Tip"
    This is a tip admonition. Perfect for sharing best practices and helpful hints.

!!! warning "Important Warning"
    This is a warning admonition. Use it to highlight potential issues or important considerations.

!!! danger "Critical Alert"
    This is a danger admonition. Use it for critical information that users must be aware of.

!!! example "Code Example"
    This is an example admonition with code:
    
    ```python
    from hands_scaphoid import Shell
    
    with Shell() as shell:
        result = shell.run("echo 'Hello World'")
        print(result.stdout)
    ```

!!! abstract "Summary"
    This is an abstract admonition for summarizing key points.

!!! info "Additional Information"
    You can also use collapsible admonitions:

??? note "Click to expand"
    This content is hidden by default and can be expanded by clicking.

??? question "Frequently Asked Question"
    **Q: How do I use the Shell context manager?**
    
    A: Simply import it and use it in a `with` statement as shown in the examples above.

## Tabs

Tabs allow you to organize related content in a compact, navigable interface.

=== "Python Example"

    ```python
    from hands_scaphoid import Shell
    
    # Basic usage
    with Shell() as shell:
        result = shell.run("ls -la")
        print(result.stdout)
    ```

=== "Windows PowerShell"

    ```python
    from hands_scaphoid import Shell
    
    # Windows PowerShell example
    with Shell(shell="powershell") as shell:
        result = shell.run("Get-ChildItem")
        print(result.stdout)
    ```

=== "Command Prompt"

    ```python
    from hands_scaphoid import Shell
    
    # Windows Command Prompt example
    with Shell(shell="cmd") as shell:
        result = shell.run("dir")
        print(result.stdout)
    ```

=== "Bash/WSL"

    ```python
    from hands_scaphoid import Shell
    
    # WSL/Bash example
    with Shell(shell="bash") as shell:
        result = shell.run("find . -name '*.py'")
        print(result.stdout)
    ```

### Configuration Tabs

=== "Basic Configuration"

    ```python
    from hands_scaphoid import Shell
    
    # Simple configuration
    shell = Shell(
        shell="bash",
        timeout=30
    )
    ```

=== "Advanced Configuration"

    ```python
    from hands_scaphoid import Shell
    
    # Advanced configuration with custom environment
    shell = Shell(
        shell="bash",
        timeout=60,
        env={"PATH": "/custom/path"},
        cwd="/custom/working/directory"
    )
    ```

=== "Windows Specific"

    ```python
    from hands_scaphoid import Shell
    
    # Windows-specific configuration
    shell = Shell(
        shell="powershell",
        timeout=45,
        execution_policy="RemoteSigned"
    )
    ```

## API Documentation Includes

The mkdocstrings plugin automatically generates API documentation from docstrings.

### Shell Class Example

::: hands_scaphoid.ShellExecutable
    options:
      show_root_heading: false
      show_source: false
      members_order: alphabetical
      show_bases: false

### ShellContext Class

::: hands_scaphoid.ShellContext
    options:
      show_root_heading: true
      show_source: true
      members_order: source

### File Operations

TODO: add file operations example

## Combined Example

Here's an example that combines all three features:

!!! example "Complete Workflow Example"

    === "Setup"
    
        First, install and import the necessary components:
        
        ```python
        from hands_scaphoid import Shell, ShellContext
        import os
        ```
    
    === "Basic Usage"
    
        ```python
        # Create a shell context
        with Shell() as shell:
            # Run a simple command
            result = shell.run("echo 'Hello from shell!'")
            
            if result.success:
                print(f"Output: {result.stdout}")
            else:
                print(f"Error: {result.stderr}")
        ```
    
    === "Advanced Usage"
    
        ```python
        # Advanced usage with error handling
        try:
            with Shell(timeout=30) as shell:
                # Multiple commands
                commands = [
                    "pwd",
                    "ls -la",
                    "echo 'Processing complete'"
                ]
                
                for cmd in commands:
                    result = shell.run(cmd)
                    if not result.success:
                        raise RuntimeError(f"Command failed: {cmd}")
                        
        except TimeoutError:
            print("Operation timed out")
        except RuntimeError as e:
            print(f"Command execution failed: {e}")
        ```

    !!! warning "Error Handling"
        Always implement proper error handling when working with shell commands, especially in production environments.

    !!! tip "Performance"
        For multiple related commands, consider using a single shell context to avoid the overhead of creating multiple shell instances.

## Testing the Plugins

To verify that all plugins are working correctly:

1. **Admonitions**: Check that the callout boxes above render with proper styling and icons
2. **Tabs**: Verify that the tabbed content switches properly when clicking different tabs
3. **API Includes**: Confirm that the API documentation is automatically generated and displayed with proper formatting

!!! success "All Features Working"
    If you can see properly formatted admonitions, functional tabs, and auto-generated API documentation, then all mkdocs-material plugins are configured correctly!