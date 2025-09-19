#!/usr/bin/env python3
"""
Main entry point for hands-scaphoid CLI.

This module provides a simple command-line interface for the hands-scaphoid
package, demonstrating basic usage and serving as an entry point.
"""

import sys
from typing import List, Optional

import click
from rich.console import Console

from . import __version__
from .objects.ShellExecutable import Shell
from .contexts.ShellContext import ShellContext

console = Console()


@click.group(invoke_without_command=True)
@click.option('--version', is_flag=True, help='Show version and exit')
@click.pass_context
def main(ctx: click.Context, version: bool) -> None:
    """
    Hands Scaphoid - Secure shell execution context manager.
    
    A Python library for secure shell command execution with environment
    management, command allowlisting, and Docker integration.
    """
    if version:
        console.print(f"hands-scaphoid version {__version__}")
        sys.exit(0)
    
    if ctx.invoked_subcommand is None:
        console.print("Hello from hands-scaphoid!")
        console.print("\nUse --help to see available commands.")


@main.command()
@click.option('--cwd', default=None, help='Working directory')
@click.option('--env-file', default='~/.env', help='Environment file path')
@click.argument('commands', nargs=-1, required=True)
def exec(cwd: Optional[str], env_file: str, commands: List[str]) -> None:
    """
    Execute shell commands in a secure context.
    
    Example:
        hands-trapezium exec "ls -la" "echo hello"
    """
    try:
        with ShellContext(cwd=cwd, env_file=env_file) as shell:
            for command in commands:
                # Extract command name for allowlisting
                cmd_name = command.split()[0] if command.strip() else ""
                if cmd_name:
                    if not shell.allow(cmd_name):
                        console.print(f"[red]Error: Command '{cmd_name}' not found[/red]")
                        sys.exit(1)
                    
                    try:
                        result = shell.run(command)
                        if result.stdout:
                            console.print(result.stdout, end='')
                    except Exception as e:
                        console.print(f"[red]Error executing '{command}': {e}[/red]")
                        sys.exit(1)
                        
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@main.command()
def demo() -> None:
    """Run a demonstration of hands-trapezium capabilities."""
    console.print("[bold]Hands Trapezium Demo[/bold]")
    console.print("\nDemonstrating secure shell execution...")
    
    try:
        with ShellContext() as shell:
            # Allow safe commands
            commands_to_demo = ["echo", "pwd", "whoami"]
            
            for cmd in commands_to_demo:
                if shell.allow(cmd):
                    console.print(f"\n[green]Executing: {cmd}[/green]")
                    try:
                        result = shell.run(cmd)
                        if result.stdout:
                            console.print(f"Output: {result.stdout.strip()}")
                    except Exception as e:
                        console.print(f"[red]Error: {e}[/red]")
                else:
                    console.print(f"[yellow]Command '{cmd}' not available on this system[/yellow]")
                    
            # Demonstrate security - try to run a non-allowed command
            console.print("\n[yellow]Demonstrating security - trying to run 'cat' without allowing it:[/yellow]")
            try:
                shell.run("cat /etc/passwd")
            except PermissionError as e:
                console.print(f"[green]Security working: {e}[/green]")
                
    except Exception as e:
        console.print(f"[red]Demo error: {e}[/red]")
        sys.exit(1)


if __name__ == "__main__":
    main()
