"""
Unit tests for the main module and CLI interface.
"""

from unittest.mock import patch, MagicMock
from click.testing import CliRunner

import pytest

from hands_scaphoid.main import main, exec, demo
from hands_scaphoid import __version__


class TestMainCommand:
    """Test the main CLI command."""

    def test_main_version_flag(self):
        """Test the --version flag."""
        runner = CliRunner()
        result = runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert __version__ in result.output

    def test_main_without_command(self):
        """Test main command without subcommand."""
        runner = CliRunner()
        result = runner.invoke(main, [])

        assert result.exit_code == 0
        assert "Hello from hands-trapezium!" in result.output
        assert "Use --help to see available commands." in result.output

    def test_main_help(self):
        """Test main command help."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Hands Trapezium" in result.output
        assert "shell command execution" in result.output


class TestExecCommand:
    """Test the exec CLI command."""

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_single_command(self, mock_shell_context):
        """Test executing a single command."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "Hello World\n"
        mock_shell.run.return_value = mock_result
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["echo Hello World"])

        assert result.exit_code == 0
        mock_shell.allow.assert_called_once_with("echo")
        mock_shell.run.assert_called_once_with("echo Hello World")

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_multiple_commands(self, mock_shell_context):
        """Test executing multiple commands."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "output\n"
        mock_shell.run.return_value = mock_result
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["echo hello", "pwd"])

        assert result.exit_code == 0
        assert mock_shell.allow.call_count == 2
        assert mock_shell.run.call_count == 2

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_command_not_found(self, mock_shell_context):
        """Test executing a command that's not found."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = False
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["nonexistent_command"])

        assert result.exit_code == 1
        assert "Command 'nonexistent_command' not found" in result.output

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_command_execution_error(self, mock_shell_context):
        """Test handling command execution errors."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_shell.run.side_effect = Exception("Command failed")
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["failing_command"])

        assert result.exit_code == 1
        assert "Error executing" in result.output

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_with_custom_cwd(self, mock_shell_context):
        """Test executing with custom working directory."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_shell.run.return_value = mock_result
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["--cwd", "/tmp", "pwd"])

        assert result.exit_code == 0
        mock_shell_context.assert_called_once_with(cwd="/tmp", env_file="~/.env")

    @patch("hands_scaphoid.main.ShellContext")
    def test_exec_with_custom_env_file(self, mock_shell_context):
        """Test executing with custom environment file."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = ""
        mock_shell.run.return_value = mock_result
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(exec, ["--env-file", "/custom/.env", "echo test"])

        assert result.exit_code == 0
        mock_shell_context.assert_called_once_with(cwd=None, env_file="/custom/.env")

    def test_exec_no_commands(self):
        """Test exec command without any commands."""
        runner = CliRunner()
        result = runner.invoke(exec, [])

        assert result.exit_code == 2  # Click error for missing required argument


class TestDemoCommand:
    """Test the demo CLI command."""

    @patch("hands_scaphoid.main.ShellContext")
    def test_demo_successful_execution(self, mock_shell_context):
        """Test successful demo execution."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "demo output\n"
        mock_shell.run.return_value = mock_result
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(demo, [])

        assert result.exit_code == 0
        assert "Hands Trapezium Demo" in result.output
        assert "Demonstrating secure shell execution" in result.output

    @patch("hands_scaphoid.main.ShellContext")
    def test_demo_command_not_available(self, mock_shell_context):
        """Test demo when commands are not available."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = False
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(demo, [])

        assert result.exit_code == 0
        assert "not available on this system" in result.output

    @patch("hands_scaphoid.main.ShellContext")
    def test_demo_security_demonstration(self, mock_shell_context):
        """Test demo security feature demonstration."""
        # Setup mock
        mock_shell = MagicMock()
        mock_shell.allow.return_value = True
        mock_result = MagicMock()
        mock_result.stdout = "output\n"
        mock_shell.run.side_effect = [
            mock_result,  # First few commands succeed
            mock_result,
            mock_result,
            PermissionError("Command 'cat' is not allowed"),  # Security demo
        ]
        mock_shell_context.return_value.__enter__.return_value = mock_shell

        runner = CliRunner()
        result = runner.invoke(demo, [])

        assert result.exit_code == 0
        assert "Security working" in result.output

    @patch("hands_scaphoid.main.ShellContext")
    def test_demo_exception_handling(self, mock_shell_context):
        """Test demo exception handling."""
        # Setup mock to raise an exception
        mock_shell_context.side_effect = Exception("Demo error")

        runner = CliRunner()
        result = runner.invoke(demo, [])

        assert result.exit_code == 1
        assert "Demo error" in result.output


class TestMainModuleIntegration:
    """Integration tests for the main module."""

    def test_main_entry_point(self):
        """Test that main can be called as entry point."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "Usage:" in result.output

    def test_command_discovery(self):
        """Test that all commands are discoverable."""
        runner = CliRunner()
        result = runner.invoke(main, ["--help"])

        assert result.exit_code == 0
        assert "exec" in result.output
        assert "demo" in result.output
