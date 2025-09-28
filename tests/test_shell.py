#!/usr/bin/env python3
"""
Unit tests for the Shell class.

File:
    name: test_shell.py
    uuid: 1234abcd-5678-90ef-1234-567890abcdef
    date: 2025-09-28

Description:
    Comprehensive tests for Shell class functionality including command execution,
    environment management, working directory handling, and security features.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# Standard library imports
import os
import subprocess
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# Third-party imports
import pytest

# Project imports
from hands_scaphoid import Shell


class TestShellInitialization:
    """Test Shell class initialization."""

    def test_init_default_values(self):
        """Test Shell initialization with default values."""
        shell = Shell()
        assert shell.cwd == os.getcwd()
        assert isinstance(shell.env, dict)  # env is a copy, not the same object
        assert shell.allow_commands == []
        assert shell.last_result is None

    def test_init_with_custom_cwd(self, temp_dir):
        """Test Shell initialization with custom working directory."""
        shell = Shell(cwd=str(temp_dir))
        assert shell.cwd == str(temp_dir)

    def test_init_with_custom_env(self, mock_env_vars):
        """Test Shell initialization with custom environment."""
        shell = Shell(env=mock_env_vars)
        assert shell.env == mock_env_vars

    def test_init_with_invalid_cwd(self):
        """Test Shell initialization with invalid working directory."""
        with pytest.raises(FileNotFoundError):
            Shell(cwd="/nonexistent/directory")

    def test_init_loads_env_file(self, temp_env_file):
        """Test that environment file is loaded correctly."""
        shell = Shell(env_file=temp_env_file)
        assert shell.env.get("TEST_VAR") == "test_value"
        assert shell.env.get("ANOTHER_VAR") == "another_value"

    def test_init_handles_missing_env_file(self):
        """Test that missing environment file is handled gracefully."""
        shell = Shell(env_file="/nonexistent/.env")
        # Should not raise an exception
        assert isinstance(shell.env, dict)


class TestShellAllowMethod:
    """Test Shell.allow() method."""

    @patch("subprocess.run")
    def test_allow_valid_command(self, mock_run, shell_with_temp_dir):
        """Test allowing a valid command."""
        mock_run.return_value = MagicMock()

        result = shell_with_temp_dir.allow("echo")

        assert result is True
        assert "echo" in shell_with_temp_dir.allow_commands
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_allow_invalid_command(self, mock_run, shell_with_temp_dir):
        """Test allowing an invalid command."""
        mock_run.side_effect = subprocess.CalledProcessError(1, "which")

        result = shell_with_temp_dir.allow("nonexistent_command")

        assert result is False
        assert "nonexistent_command" not in shell_with_temp_dir.allow_commands

    def test_allow_already_allowed_command(self, shell_with_temp_dir):
        """Test allowing a command that's already allowed."""
        shell_with_temp_dir.allow_commands = ["echo"]

        result = shell_with_temp_dir.allow("echo")

        assert result is True
        assert shell_with_temp_dir.allow_commands.count("echo") == 1

    def test_allow_empty_command(self, shell_with_temp_dir):
        """Test allowing an empty command."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            shell_with_temp_dir.allow("")

    def test_allow_whitespace_command(self, shell_with_temp_dir):
        """Test allowing a whitespace-only command."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            shell_with_temp_dir.allow("   ")


class TestShellRunMethod:
    """Test Shell.run() method."""

    def test_run_allowed_command(self, shell_with_temp_dir):
        """Test running an allowed command."""
        shell_with_temp_dir.allow_commands = ["echo"]

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = "Hello World\n"
            mock_result.stderr = ""
            mock_run.return_value = mock_result

            result = shell_with_temp_dir.run("echo Hello World")

            assert result == mock_result
            assert shell_with_temp_dir.last_result == mock_result

    def test_run_disallowed_command(self, shell_with_temp_dir):
        """Test running a disallowed command."""
        with pytest.raises(PermissionError, match="Command 'echo' is not allowed"):
            shell_with_temp_dir.run("echo Hello")

    def test_run_empty_command(self, shell_with_temp_dir):
        """Test running an empty command."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            shell_with_temp_dir.run("")

    def test_run_with_timeout(self, shell_with_temp_dir):
        """Test running a command with timeout."""
        shell_with_temp_dir.allow_commands = ["sleep"]

        with patch("subprocess.run") as mock_run:
            mock_run.side_effect = subprocess.TimeoutExpired("sleep", 1)

            with pytest.raises(subprocess.TimeoutExpired):
                shell_with_temp_dir.run("sleep 10", timeout=1)

    def test_run_with_error_output(self, shell_with_temp_dir):
        """Test running a command that produces error output."""
        shell_with_temp_dir.allow_commands = ["ls"]

        with patch("subprocess.run") as mock_run:
            mock_result = MagicMock()
            mock_result.stdout = ""
            mock_result.stderr = (
                "ls: cannot access '/nonexistent': No such file or directory"
            )
            mock_run.return_value = mock_result

            # The print function is imported from __base__ in Shell.py
            with patch("hands_scaphoid.Shell.print") as mock_print:
                result = shell_with_temp_dir.run("ls /nonexistent")

                assert result == mock_result
                mock_print.assert_called()


class TestShellRunInMethod:
    """Test Shell.run_in() method."""

    def test_run_in_container(self, shell_with_temp_dir):
        """Test running a command in a Docker container."""
        shell_with_temp_dir.allow_commands = ["docker"]

        with patch.object(shell_with_temp_dir, "run") as mock_run:
            mock_result = MagicMock()
            mock_run.return_value = mock_result

            result = shell_with_temp_dir.run_in("mycontainer", "echo hello")

            expected_command = "docker exec mycontainer echo hello"
            mock_run.assert_called_once_with(expected_command, None, True, True, True)
            assert result == mock_result

    def test_run_in_empty_container_name(self, shell_with_temp_dir):
        """Test running a command with empty container name."""
        with pytest.raises(ValueError, match="Container name cannot be empty"):
            shell_with_temp_dir.run_in("", "echo hello")

    def test_run_in_empty_command(self, shell_with_temp_dir):
        """Test running an empty command in container."""
        with pytest.raises(ValueError, match="Command cannot be empty"):
            shell_with_temp_dir.run_in("mycontainer", "")


class TestShellCdMethod:
    """Test Shell.cd() method."""

    def test_cd_valid_directory(self, temp_dir, shell_with_temp_dir):
        """Test changing to a valid directory."""
        subdir = temp_dir / "subdir"
        subdir.mkdir()

        shell_with_temp_dir.cd("subdir")

        assert shell_with_temp_dir.cwd == str(subdir)

    def test_cd_absolute_path(self, shell_with_temp_dir):
        """Test changing to an absolute path."""
        shell_with_temp_dir.cd("/tmp")
        assert shell_with_temp_dir.cwd == "/tmp"

    def test_cd_invalid_directory(self, shell_with_temp_dir):
        """Test changing to an invalid directory."""
        with pytest.raises(NotADirectoryError):
            shell_with_temp_dir.cd("/nonexistent/directory")

    def test_cd_empty_path(self, shell_with_temp_dir):
        """Test changing to an empty path."""
        with pytest.raises(ValueError, match="Path cannot be empty"):
            shell_with_temp_dir.cd("")


class TestShellEnvironmentMethods:
    """Test Shell environment variable methods."""

    def test_get_env_var_existing(self, shell_with_env):
        """Test getting an existing environment variable."""
        value = shell_with_env.get_env_var("TEST_VAR")
        assert value == "test_value"

    def test_get_env_var_nonexistent(self, shell_with_temp_dir):
        """Test getting a non-existent environment variable."""
        value = shell_with_temp_dir.get_env_var("NONEXISTENT_VAR")
        assert value is None

    def test_get_env_var_empty_name(self, shell_with_temp_dir):
        """Test getting environment variable with empty name."""
        with pytest.raises(ValueError, match="Variable name cannot be empty"):
            shell_with_temp_dir.get_env_var("")

    def test_set_env_var(self, shell_with_temp_dir):
        """Test setting an environment variable."""
        shell_with_temp_dir.set_env_var("NEW_VAR", "new_value")
        assert shell_with_temp_dir.env["NEW_VAR"] == "new_value"

    def test_set_env_var_empty_name(self, shell_with_temp_dir):
        """Test setting environment variable with empty name."""
        with pytest.raises(ValueError, match="Variable name cannot be empty"):
            shell_with_temp_dir.set_env_var("", "value")


class TestShellUtilityMethods:
    """Test Shell utility methods."""

    def test_sleep_positive_duration(self, shell_with_temp_dir):
        """Test sleep with positive duration."""
        with patch("time.sleep") as mock_sleep:
            shell_with_temp_dir.sleep(1.5)
            mock_sleep.assert_called_once_with(1.5)

    def test_sleep_zero_duration(self, shell_with_temp_dir):
        """Test sleep with zero duration."""
        with patch("time.sleep") as mock_sleep:
            shell_with_temp_dir.sleep(0)
            mock_sleep.assert_called_once_with(0)

    def test_sleep_negative_duration(self, shell_with_temp_dir):
        """Test sleep with negative duration."""
        with pytest.raises(ValueError, match="Sleep duration cannot be negative"):
            shell_with_temp_dir.sleep(-1)

    def test_get_allowed_commands(self, shell_with_temp_dir):
        """Test getting list of allowed commands."""
        shell_with_temp_dir.allow_commands = ["echo", "ls"]
        commands = shell_with_temp_dir.get_allowed_commands()

        assert commands == ["echo", "ls"]
        # Ensure it returns a copy
        commands.append("pwd")
        assert "pwd" not in shell_with_temp_dir.allow_commands

    def test_is_command_allowed(self, shell_with_temp_dir):
        """Test checking if command is allowed."""
        shell_with_temp_dir.allow_commands = ["echo"]

        assert shell_with_temp_dir.is_command_allowed("echo") is True
        assert shell_with_temp_dir.is_command_allowed("ls") is False
        assert shell_with_temp_dir.is_command_allowed("") is False


class TestShellDependsOnMethod:
    """Test Shell.depends_on() method."""

    @patch.object(Shell, "allow")
    @patch.object(Shell, "run")
    def test_depends_on_running_containers(
        self, mock_run, mock_allow, shell_with_temp_dir
    ):
        """Test depends_on with running containers."""
        mock_allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "container1\ncontainer2\n"
        mock_run.return_value = mock_result

        result = shell_with_temp_dir.depends_on(["container1", "container2"])

        assert result is True
        mock_run.assert_called_once()

    @patch.object(Shell, "allow")
    @patch.object(Shell, "run")
    def test_depends_on_missing_container(
        self, mock_run, mock_allow, shell_with_temp_dir
    ):
        """Test depends_on with missing container."""
        mock_allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "container1\n"
        mock_run.return_value = mock_result

        with pytest.raises(SystemExit):
            shell_with_temp_dir.depends_on(["container1", "missing_container"])

    def test_depends_on_empty_names(self, shell_with_temp_dir):
        """Test depends_on with empty container names."""
        with pytest.raises(ValueError, match="Container names cannot be empty"):
            shell_with_temp_dir.depends_on([])

    @patch.object(Shell, "allow")
    def test_depends_on_docker_not_available(self, mock_allow, shell_with_temp_dir):
        """Test depends_on when docker is not available."""
        mock_allow.return_value = False

        with pytest.raises(RuntimeError, match="Docker command is not available"):
            shell_with_temp_dir.depends_on(["container1"])
