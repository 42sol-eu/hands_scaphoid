"""
Unit tests for the ShellContext context manager.
"""

import builtins
from unittest.mock import patch, MagicMock

import pytest

from hands_scaphoid import ShellContext, Shell


class TestShellContext:
    """Test ShellContext context manager."""

    def test_shell_context_basic_usage(self, temp_dir):
        """Test basic usage of ShellContext."""
        with ShellContext(cwd=str(temp_dir)) as shell:
            assert isinstance(shell, Shell)
            assert shell.cwd == str(temp_dir)

            # Test that global functions are available
            assert hasattr(builtins, "cd")
            assert hasattr(builtins, "run")
            assert hasattr(builtins, "run_in")
            assert hasattr(builtins, "sleep")
            assert hasattr(builtins, "allow")
            assert hasattr(builtins, "depends_on")

    def test_shell_context_cleanup(self, temp_dir):
        """Test that ShellContext cleans up global functions."""
        # Store original state
        original_functions = {}
        function_names = ["cd", "run", "run_in", "sleep", "allow", "depends_on"]

        for func_name in function_names:
            if hasattr(builtins, func_name):
                original_functions[func_name] = getattr(builtins, func_name)

        with ShellContext(cwd=str(temp_dir)):
            # Functions should be available during context
            for func_name in function_names:
                assert hasattr(builtins, func_name)

        # Functions should be cleaned up after context
        for func_name in function_names:
            if func_name in original_functions:
                assert getattr(builtins, func_name) == original_functions[func_name]
            else:
                assert not hasattr(builtins, func_name)

    def test_shell_context_with_env_file(self, temp_env_file):
        """Test ShellContext with custom environment file."""
        with ShellContext(env_file=temp_env_file) as shell:
            assert shell.get_env_var("TEST_VAR") == "test_value"

    def test_shell_context_global_functions_work(self, temp_dir):
        """Test that global functions work correctly."""
        with ShellContext(cwd=str(temp_dir)) as shell:
            # Test cd function
            subdir = temp_dir / "test_subdir"
            subdir.mkdir()

            cd("test_subdir")  # noqa: F821
            assert shell.cwd.endswith("test_subdir")

            # Test allow function
            with patch("subprocess.run") as mock_run:
                mock_run.return_value = MagicMock()
                result = allow("echo")  # noqa: F821
                assert result is True

    def test_shell_context_exception_handling(self, temp_dir):
        """Test that ShellContext handles exceptions properly."""
        function_names = ["cd", "run", "run_in", "sleep", "allow", "depends_on"]

        try:
            with ShellContext(cwd=str(temp_dir)):
                # Functions should be available
                for func_name in function_names:
                    assert hasattr(builtins, func_name)

                # Raise an exception
                raise ValueError("Test exception")

        except ValueError:
            # Functions should still be cleaned up
            for func_name in function_names:
                assert not hasattr(builtins, func_name)

    def test_shell_context_preserves_existing_functions(self):
        """Test that ShellContext preserves existing global functions."""
        # Set up existing functions
        original_cd = lambda x: None  # noqa: E731
        original_run = lambda x: None  # noqa: E731

        builtins.cd = original_cd
        builtins.run = original_run

        try:
            with ShellContext():
                # Functions should be overridden during context
                assert builtins.cd != original_cd
                assert builtins.run != original_run

            # Original functions should be restored
            assert builtins.cd == original_cd
            assert builtins.run == original_run

        finally:
            # Clean up
            if hasattr(builtins, "cd"):
                delattr(builtins, "cd")
            if hasattr(builtins, "run"):
                delattr(builtins, "run")

    def test_shell_context_with_custom_env(self, mock_env_vars):
        """Test ShellContext with custom environment variables."""
        with ShellContext(env=mock_env_vars) as shell:
            assert shell.get_env_var("TEST_VAR") == "test_value"
            assert shell.get_env_var("HOME") == "/home/test"


class TestShellContextIntegration:
    """Integration tests for ShellContext."""

    def test_shell_context_real_commands(self, temp_dir):
        """Test ShellContext with real command execution."""
        with ShellContext(cwd=str(temp_dir)) as shell:
            # Allow echo command
            if shell.allow("echo"):
                result = run("echo 'Hello World'")  # noqa: F821
                assert "Hello World" in result.stdout

    def test_shell_context_directory_operations(self, temp_dir):
        """Test directory operations through ShellContext."""
        with ShellContext(cwd=str(temp_dir)):
            # Create a subdirectory
            subdir = temp_dir / "testdir"
            subdir.mkdir()

            # Change to subdirectory
            cd("testdir")  # noqa: F821

            # Change back to parent
            cd("..")  # noqa: F821

    def test_shell_context_environment_operations(self, temp_dir):
        """Test environment variable operations through ShellContext."""
        with ShellContext(cwd=str(temp_dir)) as shell:
            # Set an environment variable
            shell.set_env_var("TEST_NEW_VAR", "test_value")

            # Get the environment variable
            value = shell.get_env_var("TEST_NEW_VAR")
            assert value == "test_value"

    @patch("time.sleep")
    def test_shell_context_sleep_function(self, mock_sleep, temp_dir):
        """Test sleep function through ShellContext."""
        with ShellContext(cwd=str(temp_dir)):
            sleep(2)  # noqa: F821
            mock_sleep.assert_called_once_with(2)
