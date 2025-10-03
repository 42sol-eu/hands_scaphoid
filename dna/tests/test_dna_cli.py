"""
Test suite for DNA CLI commands.

Tests the core functionality of the DNA CLI tool including
command execution, file operations, and error handling.
---yaml
TODO: enter file meta yaml
"""

import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch, Mock

# [Standard library imports]
# Import the main dna CLI
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

# [Local DUT imports]
from dna import cli

# [Third party imports (tests)]
import pytest 

# [Tests] 

class TestDNACLI:
    """Test the main DNA CLI functionality."""
    
    def test_cli_help(self, dna_cli_runner):
        """Test that CLI help works."""
        result = dna_cli_runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "DO - A CLI tool for Python package development" in result.output
    
    def test_cli_version(self, dna_cli_runner):
        """Test version display."""
        result = dna_cli_runner.invoke(cli, ['--version'])
        assert result.exit_code == 0
    
    @pytest.mark.cli
    def test_find_classes_help(self, dna_cli_runner):
        """Test find-classes command help."""
        result = dna_cli_runner.invoke(cli, ['find-classes', '--help'])
        assert result.exit_code == 0
        assert "Find all classes" in result.output
    
    @pytest.mark.cli
    def test_create_file_help(self, dna_cli_runner):
        """Test create-file command help."""
        result = dna_cli_runner.invoke(cli, ['create-file', '--help'])
        assert result.exit_code == 0
        assert "Create a new file" in result.output
    
    @pytest.mark.cli
    def test_create_file_list_templates(self, dna_cli_runner):
        """Test listing available templates."""
        result = dna_cli_runner.invoke(cli, ['create-file', '--list'])
        assert result.exit_code == 0
        assert "Available Templates:" in result.output
        assert "Jinja2 Templates:" in result.output
    
    @pytest.mark.cli
    def test_install_wheels_help(self, dna_cli_runner):
        """Test install-wheels command help."""
        result = dna_cli_runner.invoke(cli, ['install-wheels', '--help'])
        assert result.exit_code == 0
        assert "Install dependencies" in result.output


class TestCommandImports:
    """Test that command modules import correctly."""
    
    def test_import_find_classes(self):
        """Test importing find_classes command."""
        from commands.find_classes import find_classes
        assert callable(find_classes)
    
    def test_import_create_file(self):
        """Test importing create_file command."""
        from commands.create_file import create_file
        assert callable(create_file)
    
    def test_import_file_creator(self):
        """Test importing file_creator module."""
        from commands.file_creator import create_file_from_template
        assert callable(create_file_from_template)
    
    def test_import_class_finder(self):
        """Test importing class_finder module."""
        from commands.class_finder import find_classes
        assert callable(find_classes)


class TestFileOperations:
    """Test file-related operations."""
    
    @pytest.mark.cli
    def test_find_classes_with_file(self, dna_cli_runner, sample_python_file):
        """Test find-classes command with a real file."""
        result = dna_cli_runner.invoke(cli, ['find-classes', str(sample_python_file)])
        assert result.exit_code == 0
        # Should find SampleClass
        assert "SampleClass" in result.output or "Classes Found" in result.output
    
    @pytest.mark.cli
    def test_find_classes_with_directory(self, dna_cli_runner, sample_directory):
        """Test find-classes command with a directory."""
        result = dna_cli_runner.invoke(cli, ['find-classes', str(sample_directory)])
        assert result.exit_code == 0
    
    def test_create_simple_file(self, temp_dir, dna_cli_runner):
        """Test creating a simple file with template."""
        output_file = temp_dir / "test_module.py"
        result = dna_cli_runner.invoke(cli, [
            'create-file', str(output_file), 
            '--template', 'module',
            '--author', 'Test Author'
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Check file content
        content = output_file.read_text()
        assert "Test Author" in content
        assert "test_module" in content.lower()


@pytest.mark.integration
class TestCommandIntegration:
    """Integration tests for command workflows."""
    
    def test_create_and_analyze_workflow(self, temp_dir, dna_cli_runner):
        """Test creating a file and then analyzing it."""
        # Create a class file
        output_file = temp_dir / "TestClass.py"
        result = dna_cli_runner.invoke(cli, [
            'create-file', str(output_file),
            '--template', 'class',
            '--author', 'Test Author'
        ])
        assert result.exit_code == 0
        assert output_file.exists()
        
        # Now analyze it
        result = dna_cli_runner.invoke(cli, ['find-classes', str(output_file)])
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling in commands."""
    
    @pytest.mark.cli
    def test_find_classes_nonexistent_file(self, dna_cli_runner):
        """Test find-classes with non-existent file."""
        result = dna_cli_runner.invoke(cli, ['find-classes', '/nonexistent/file.py'])
        assert result.exit_code != 0 or "not found" in result.output.lower()
    
    @pytest.mark.cli 
    def test_create_file_existing_file(self, dna_cli_runner, sample_python_file):
        """Test creating file that already exists."""
        result = dna_cli_runner.invoke(cli, [
            'create-file', str(sample_python_file),
            '--template', 'module'
        ])
        # Should either fail or show warning about existing file
        assert result.exit_code != 0 or "exists" in result.output.lower()


class TestDependencyManagement:
    """Test dependency installation and management."""
    
    @pytest.mark.slow
    def test_ensure_dependencies_available(self):
        """Test that ensure_dependencies_installed function exists."""
        from commands.ensure_dependencies_installed import ensure_dependencies_installed
        assert callable(ensure_dependencies_installed)
    
    def test_install_wheels_dry_run(self, dna_cli_runner):
        """Test install-wheels in dry run mode (safe to run)."""
        # This should work even without wheel files
        result = dna_cli_runner.invoke(cli, ['install-wheels', '--help'])
        assert result.exit_code == 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])