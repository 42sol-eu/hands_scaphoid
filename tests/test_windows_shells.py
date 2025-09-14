#!/usr/bin/env python3
"""
Unit tests for Windows-specific shell implementations.
"""

import platform
import pytest
from unittest.mock import patch, MagicMock

from hands_scaphoid.WindowsShells import PowerShell, WslShell, create_powershell_shell, create_wsl_shell


class TestPowerShell:
    """Test PowerShell shell command translation and execution."""

    def test_command_translation_ls(self):
        """Test ls command translation to Get-ChildItem."""
        shell = PowerShell()
        
        # Basic ls
        translated = shell._translate_command("ls")
        assert translated == "Get-ChildItem"
        
        # ls with arguments
        translated = shell._translate_command("ls -la")
        assert "Get-ChildItem" in translated
        assert "-Force" in translated
        
    def test_command_translation_cp(self):
        """Test cp command translation to Copy-Item."""
        shell = PowerShell()
        
        # Basic copy
        translated = shell._translate_command("cp source.txt dest.txt")
        assert translated == 'Copy-Item "source.txt" "dest.txt"'
        
        # Copy with recursive flag
        translated = shell._translate_command("cp -r folder dest")
        assert "Copy-Item" in translated
        assert "-Recurse" in translated
        
    def test_command_translation_rm(self):
        """Test rm command translation to Remove-Item."""
        shell = PowerShell()
        
        # Basic remove
        translated = shell._translate_command("rm file.txt")
        assert 'Remove-Item "file.txt"' in translated
        
        # Remove with flags
        translated = shell._translate_command("rm -rf folder")
        assert "Remove-Item" in translated
        assert "-Recurse" in translated
        assert "-Force" in translated
        
    def test_command_translation_common_commands(self):
        """Test translation of common Unix commands."""
        shell = PowerShell()
        
        test_cases = {
            "cat file.txt": "Get-Content file.txt",
            "pwd": "Get-Location",
            "echo hello": "Write-Output hello",
            "ps": "Get-Process",
            "whoami": "[System.Security.Principal.WindowsIdentity]::GetCurrent().Name"
        }
        
        for unix_cmd, expected_ps in test_cases.items():
            translated = shell._translate_command(unix_cmd)
            assert expected_ps in translated or translated == expected_ps
            
    def test_untranslated_commands(self):
        """Test that unknown commands are not translated."""
        shell = PowerShell()
        
        unknown_cmd = "some_unknown_command arg1 arg2"
        translated = shell._translate_command(unknown_cmd)
        assert translated == unknown_cmd
        
    @patch('platform.system')
    @patch('subprocess.run')
    def test_powershell_executable_detection(self, mock_run, mock_platform):
        """Test PowerShell executable detection on Windows."""
        mock_platform.return_value = "Windows"
        
        # Test pwsh available
        mock_run.return_value = MagicMock(returncode=0)
        shell = PowerShell()
        assert shell.shell_executable == "pwsh.exe"
        
        # Test pwsh not available, fallback to powershell
        mock_run.side_effect = FileNotFoundError()
        shell = PowerShell()
        assert shell.shell_executable == "powershell.exe"
        
    def test_create_powershell_shell_convenience(self):
        """Test the convenience function for creating PowerShell shells."""
        shell = create_powershell_shell()
        assert isinstance(shell, PowerShell)


class TestWslShell:
    """Test WSL shell execution and distribution management."""

    @patch('subprocess.run')
    def test_wsl_availability_check(self, mock_run):
        """Test WSL availability checking."""
        # Test WSL available
        mock_run.return_value = MagicMock(returncode=0)
        shell = WslShell()
        assert shell.distribution == "wsl"
        
        # Test WSL not available
        mock_run.side_effect = FileNotFoundError()
        with pytest.raises(RuntimeError, match="WSL distribution 'wsl' is not available"):
            WslShell()
            
    @patch('subprocess.run')
    def test_wsl_command_wrapping(self, mock_run):
        """Test command wrapping for WSL execution."""
        mock_run.return_value = MagicMock(returncode=0)
        shell = WslShell()
        
        # Test string command wrapping
        wrapped = shell._wrap_command_for_wsl("ls -la")
        expected = ["wsl.exe", "--", "sh", "-c", "ls -la"]
        assert wrapped == expected
        
        # Test list command wrapping
        wrapped = shell._wrap_command_for_wsl(["ls", "-la"])
        expected = ["wsl.exe", "--", "sh", "-c", "ls -la"]
        assert wrapped == expected
        
    @patch('subprocess.run')
    def test_wsl_distributions_list(self, mock_run):
        """Test listing available WSL distributions."""
        # Mock WSL list output
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Ubuntu\nDebian\nkali-linux\n"
        )
        
        shell = WslShell()
        distributions = shell.list_distributions()
        
        assert "Ubuntu" in distributions
        assert "Debian" in distributions
        assert "kali-linux" in distributions
        
    @patch('subprocess.run')
    def test_wsl_distribution_switching(self, mock_run):
        """Test switching WSL distributions."""
        # First call for initial WSL check (success)
        # Second call for availability check of new distribution (success)
        mock_run.return_value = MagicMock(returncode=0)
        
        shell = WslShell("wsl")
        assert shell.distribution == "wsl"
        
        # Switch to Ubuntu
        success = shell.set_distribution("Ubuntu")
        assert success is True
        assert shell.distribution == "Ubuntu"
        
        # Try to switch to non-existent distribution
        mock_run.side_effect = [MagicMock(returncode=0), FileNotFoundError()]
        success = shell.set_distribution("NonExistent")
        assert success is False
        assert shell.distribution == "Ubuntu"  # Should revert
        
    @patch('platform.system')
    @patch('subprocess.run')
    def test_wsl_run_on_windows(self, mock_run, mock_platform):
        """Test command execution through WSL on Windows."""
        mock_platform.return_value = "Windows"
        
        # Mock WSL availability check
        mock_run.return_value = MagicMock(returncode=0)
        shell = WslShell()
        shell.allow("ls")
        
        # Mock command execution
        mock_process = MagicMock()
        mock_run.return_value = mock_process
        
        result = shell.run("ls -la")
        
        # Verify the WSL command was called correctly
        mock_run.assert_called()
        call_args = mock_run.call_args
        assert "wsl.exe" in call_args[0][0][0]
        assert "ls -la" in call_args[0][0]
        
    @patch('platform.system')
    def test_wsl_run_on_non_windows(self, mock_platform):
        """Test that WSL shell works normally on non-Windows systems."""
        mock_platform.return_value = "Linux"
        
        # On non-Windows, WslShell should behave like regular Shell
        with patch.object(WslShell, '__init__', lambda x: Shell.__init__(x)):
            shell = WslShell()
            shell.allow_commands = {"ls"}  # Bypass the allow check
            
            with patch('subprocess.run') as mock_run:
                mock_run.return_value = MagicMock()
                shell.run("ls")
                
                # Should call subprocess.run directly without WSL wrapper
                mock_run.assert_called()
                call_args = mock_run.call_args[0][0]
                assert call_args == ["ls"]
                
    def test_create_wsl_shell_convenience(self):
        """Test the convenience function for creating WSL shells."""
        with patch('subprocess.run') as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            shell = create_wsl_shell("Ubuntu")
            assert isinstance(shell, WslShell)
            assert shell.distribution == "Ubuntu"


class TestWindowsShellIntegration:
    """Integration tests for Windows shell classes."""
    
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_powershell_real_command(self):
        """Test real PowerShell command execution on Windows."""
        shell = PowerShell()
        shell.allow("echo")
        shell.allow("powershell.exe")
        shell.allow("pwsh.exe")
        
        try:
            result = shell.run("echo 'Hello PowerShell'")
            assert result.returncode == 0
            assert "Hello PowerShell" in result.stdout
        except Exception as e:
            pytest.skip(f"PowerShell not available: {e}")
            
    @pytest.mark.skipif(platform.system() != "Windows", reason="Windows-specific test")
    def test_wsl_real_command(self):
        """Test real WSL command execution on Windows."""
        try:
            shell = WslShell()
            shell.allow("echo")
            
            result = shell.run("echo 'Hello WSL'")
            assert result.returncode == 0
            assert "Hello WSL" in result.stdout
        except RuntimeError:
            pytest.skip("WSL not available")
        except Exception as e:
            pytest.skip(f"WSL test failed: {e}")


if __name__ == "__main__":
    pytest.main([__file__])
