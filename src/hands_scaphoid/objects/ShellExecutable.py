"""
Shell execution module with security and environment management.

File:
    name: Shell.py
    uuid: 52319d84-4784-4df7-8752-64967f3716f8
    date: 2025-09-12

Description:
    Provides secure shell command execution with allowlisting, environment
    management, and Docker integration capabilities.

Project:
    name: hands/palm/trapezium
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4

Authors: ["Andreas Häberle"]
Projects: ["hands/palm/trapezium"]
"""

#%% [Standard library imports]
from __future__ import annotations
import os
import platform
import subprocess
import sys
import time
from typing import Dict, List, Optional, Union

#%% [Local imports]
from ..__base__ import *
from .files.ExecutableFile import ExecutableFile
# from ..commands.shell_factory import create_powershell_shell, create_wsl_shell

#%% [Class code]
class ShellExecutable(ExecutableFile):
    """
    A secure shell command executor with environment management.

    This class provides a secure way to execute shell commands with features like:
    - Command allowlisting for security
    - Environment variable management
    - Docker container command execution
    - Working directory management
    """

    def __init__(
        self,
        cwd: Optional[Union[str, PathLike]] = None,
        env: Optional[Dict[str, str]] = None,
        env_file: str = "~/.env",
    ) -> None:
        """
        Initialize the Shell instance.

        Args:
            cwd: Working directory for command execution. Defaults to current directory.
            env: Environment variables dictionary. Defaults to copy of os.environ.
            env_file: Path to environment file to load variables from.

        Raises:
            FileNotFoundError: If the specified working directory doesn't exist.
        """
        super().__init__(name="shell", path=str(cwd or os.getcwd()))

        self.cwd = str(Path(cwd or os.getcwd()).resolve())
        if not os.path.isdir(self.cwd):
            raise FileNotFoundError(f"Working directory does not exist: {self.cwd}")

        self.env = env or os.environ.copy()
        self.env_file = os.path.expanduser(env_file)
        self._load_env_file()
        self.allow_commands: List[str] = []
        self.last_result: Optional[subprocess.CompletedProcess] = None

        # define basic commands
        self.allow_commands.append("which")

    def _load_env_file(self) -> None:
        """Load environment variables from the specified env file."""
        if os.path.exists(self.env_file):
            try:
                with open(self.env_file, "r", encoding="utf-8") as f:
                    for line_num, line in enumerate(f, 1):
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            try:
                                key, value = line.split("=", 1)
                                self.env[key.strip()] = value.strip()
                            except ValueError:
                                console.print(
                                    f"[yellow]Warning: Invalid line {line_num} in {self.env_file}: {line}[/yellow]"
                                )
            except IOError as e:
                console.print(
                    f"[yellow]Warning: Could not read env file {self.env_file}: {e}[/yellow]"
                )

    def allow(self, command: Union[str, List[str]]) -> bool:
        """
        Allow a command to be executed.

        Args:
            command: The command or lost of commands to allow (first word will be extracted).

        Returns:
            True if command was successfully allowed, False if command doesn't exist.

        Raises:
            ValueError: If command is empty or invalid.
        """
        do_check: bool = True

        if isinstance(command, str):
            command = [command]

        for cmd in command:
            if not cmd or not cmd.split(" ")[0].strip():
                raise ValueError("Command cannot be empty")

            # check if available
            if do_check:
                # Use a different approach for checking command availability
                # to avoid recursive call to run()
                try:
                    if platform.system() == "Windows":
                        # On Windows, try 'where' command instead of 'which'
                        check_result = subprocess.run(
                            ["where", cmd], capture_output=True, timeout=2, env=self.env
                        )
                    else:
                        # On Unix systems, use 'which'
                        check_result = subprocess.run(
                            ["which", cmd], capture_output=True, timeout=2, env=self.env
                        )
                    add = check_result.returncode == 0
                except (
                    subprocess.CalledProcessError,
                    subprocess.TimeoutExpired,
                    FileNotFoundError,
                ):
                    add = True  # If we can't check, assume it's available
                    console.print(f"⚠️ Could not verify availability of command: {cmd}")
            else:
                add = True
                console.print(f"⚠️ Skipping availability check for command: {cmd}")

            if add:
                # command is available
                if cmd not in self.allow_commands:
                    self.allow_commands.append(cmd)
                else:
                    pass
                result = True
            else:
                console.print(
                    f"❌ Command not found: {cmd} in {self.env.get('PATH', '')}"
                )
                result = False

        return result

    def run(
        self,
        command_with_args: str,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        text: bool = True,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute a shell command with security checks.

        Args:
            command_with_args: The shell command to execute including arguments.
            timeout: Maximum seconds to wait for command completion.
            capture_output: Whether to capture stdout and stderr.
            text: Whether to return output as text (str) or bytes.
            check: Whether to raise exception on non-zero exit codes.

        Returns:
            CompletedProcess object with execution results.

        Raises:
            PermissionError: If the command is not in the allow list.
            subprocess.CalledProcessError: If check=True and command fails.
            subprocess.TimeoutExpired: If command times out.
            ValueError: If command is empty or invalid.
        """

        if isinstance(command_with_args, str):
            command_parts = command_with_args.strip().split()
        else:
            command_parts = command_with_args

        command_name = command_parts[0]

        console.print(f"[bold]$ {command_with_args}[/bold]")

        if command_name not in self.allow_commands:
            raise PermissionError(
                f"Command '{command_name}' is not allowed. Use allow() first."
            )

        try:
            result = subprocess.run(
                command_parts,
                cwd=self.cwd,
                env=self.env,
                timeout=timeout,
                capture_output=capture_output,
                text=text,
                check=check,
            )

            if result.stderr and capture_output:
                console.print(f"[red]Error: {result.stderr}[/red]")

            self.last_result = result
            return result

        except subprocess.CalledProcessError as e:
            self.last_result = e
            raise
        except subprocess.TimeoutExpired as e:
            console.print(
                f"[red]Command timed out after {timeout} seconds: {command_with_args}[/red]"
            )
            raise

    def run_in(
        self,
        container_name: str,
        command_with_args: list[str] | str,
        timeout: Optional[int] = None,
        capture_output: bool = True,
        text: bool = True,
        check: bool = True,
    ) -> subprocess.CompletedProcess:
        """
        Execute a command inside a Docker container.

        Args:
            container_name: Name of the Docker container.
            command_with_args: Command to execute inside the container.
            timeout: Maximum seconds to wait for command completion.
            capture_output: Whether to capture stdout and stderr.
            text: Whether to return output as text (str) or bytes.
            check: Whether to raise exception on non-zero exit codes.

        Returns:
            CompletedProcess object with execution results.

        Raises:
            PermissionError: If docker command is not allowed.
            subprocess.CalledProcessError: If check=True and command fails.
            ValueError: If container_name or command is empty.
        """

        command_with_args.insert(0, container_name)
        command_with_args.insert(0, "exec")
        command_with_args.insert(0, "docker")

        return self.run(command_with_args, timeout, capture_output, text, check)

    def cd(self, path: str) -> None:
        """
        Change the current working directory.

        Args:
            path: Path to change to (relative or absolute).

        Raises:
            NotADirectoryError: If the path is not a valid directory.
            ValueError: If path is empty.
        """
        if not path or not path.strip():
            raise ValueError("Path cannot be empty")

        if os.name == "nt":
            new_path = Path("C:") / os.path.abspath(
                os.path.join(self.cwd, path.replace("/", "\\"))
            )

        new_path = os.path.abspath(os.path.join(self.cwd, path))

        if not os.path.isdir(new_path):
            raise NotADirectoryError(f"{new_path} is not a valid directory.")

        self.cwd = new_path

    def get_env_var(self, var_name: str) -> Optional[str]:
        """
        Get the value of an environment variable.

        Args:
            var_name: Name of the environment variable.

        Returns:
            Value of the environment variable or None if not found.

        Raises:
            ValueError: If var_name is empty.
        """
        if not var_name or not var_name.strip():
            raise ValueError("Variable name cannot be empty")

        return self.env.get(var_name)

    def set_env_var(self, var_name: str, value: str) -> None:
        """
        Set an environment variable.

        Args:
            var_name: Name of the environment variable.
            value: Value to set.

        Raises:
            ValueError: If var_name is empty.
        """
        if not var_name or not var_name.strip():
            raise ValueError("Variable name cannot be empty")

        self.env[var_name] = value

    def sleep(self, seconds: Union[int, float]) -> None:
        """
        Sleep for the specified number of seconds.

        Args:
            seconds: Number of seconds to sleep.

        Raises:
            ValueError: If seconds is negative.
        """
        if seconds < 0:
            raise ValueError("Sleep duration cannot be negative")

        time.sleep(seconds)

    def depends_on(self, names: Union[str, List[str]]) -> bool:
        """
        Check if Docker containers are running.

        Args:
            names: Container name(s) to check.

        Returns:
            True if all containers are running.

        Raises:
            SystemExit: If any container is not running.
            RuntimeError: If docker command fails.
        """
        if isinstance(names, str):
            names = [names]

        if not names:
            raise ValueError("Container names cannot be empty")

        try:
            # Ensure docker is allowed
            if "docker" not in self.allow_commands:
                if not self.allow("docker"):
                    raise RuntimeError("Docker command is not available")

            result = self.run("docker ps --format '{{.Names}}'", check=True)
            running_containers = [
                line.strip().replace("'", "") for line in result.stdout.splitlines()
            ]

            for name in names:
                if name not in running_containers:
                    console.print(f"[red]Container {name} is not running![/red]")
                    sys.exit(2)

            return True

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to check Docker containers: {e}")

    def get_allowed_commands(self) -> List[str]:
        """
        Get the list of currently allowed commands.

        Returns:
            List of allowed command names.
        """
        return self.allow_commands.copy()

    def is_command_allowed(self, command: str) -> bool:
        """
        Check if a command is in the allow list.

        Args:
            command: Command name to check.

        Returns:
            True if command is allowed, False otherwise.
        """
        if not command or not command.strip():
            return False

        command_name = command.strip().split()[0]
        return command_name in self.allow_commands
