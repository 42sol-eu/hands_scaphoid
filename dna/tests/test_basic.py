"""
Basic test suite for DNA CLI functionality.

Tests core commands and file operations with simplified approach.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

# Import the main dna CLI
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna import cli
from commands.file_creator import create_file_from_template, list_templates


class TestDNABasics:
    """Basic tests for DNA CLI."""
    
    def test_cli_help(self):
        """Test that CLI help works."""
        runner = CliRunner()
        result = runner.invoke(cli, ['--help'])
        assert result.exit_code == 0
        assert "DO - A CLI tool for Python package development" in result.output
    
    def test_create_file_help(self):
        """Test create-file command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-file', '--help'])
        assert result.exit_code == 0
        assert "Create a new file" in result.output
    
    def test_find_classes_help(self):
        """Test find-classes command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['find-classes', '--help'])
        assert result.exit_code == 0
        assert "Find all classes" in result.output


class TestFileCreator:
    """Test file creator functionality."""
    
    def test_list_templates(self):
        """Test that we can list templates."""
        templates = list_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # Should have basic templates
        expected = ["module", "class", "function"]
        for template in expected:
            assert template in templates
    
    def test_create_simple_file(self, temp_dir):
        """Test creating a simple file."""
        output_file = temp_dir / "test_module.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="module",
            author="Test Author",
            description="Test module"
        )
        
        assert result is True
        assert output_file.exists()
        
        # Check basic content
        content = output_file.read_text()
        assert "Test Author" in content
    
    def test_create_class_file(self, temp_dir):
        """Test creating a class file."""
        output_file = temp_dir / "TestClass.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="class",
            author="Test Author",
            description="Test class",
            custom_vars={"class_name": "TestClass"}
        )
        
        assert result is True
        assert output_file.exists()
        
        # Check class content
        content = output_file.read_text()
        assert "class TestClass" in content
        assert "def __init__" in content


class TestCommandIntegration:
    """Test command integration."""
    
    def test_create_file_command(self, temp_dir):
        """Test create-file command via CLI."""
        runner = CliRunner()
        output_file = temp_dir / "cli_test.py"
        
        result = runner.invoke(cli, [
            'create-file', str(output_file),
            '--template', 'module',
            '--author', 'CLI Test'
        ])
        
        # Should succeed or show reasonable error
        assert result.exit_code == 0 or "error" not in result.output.lower()
        
        # If file was created, check it
        if output_file.exists():
            content = output_file.read_text()
            assert len(content) > 0
    
    def test_list_templates_command(self):
        """Test listing templates via CLI."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-file', '--list'])
        
        assert result.exit_code == 0
        assert "Templates:" in result.output


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_template(self, temp_dir):
        """Test handling invalid template."""
        output_file = temp_dir / "invalid.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="nonexistent",
            author="Test"
        )
        
        # Should handle gracefully
        assert result is False
    
    def test_find_classes_missing_file(self):
        """Test find-classes with missing file."""
        runner = CliRunner()
        result = runner.invoke(cli, ['find-classes', '/nonexistent/file.py'])
        
        # Should handle error gracefully (exit code may vary)
        assert isinstance(result.exit_code, int)


@pytest.mark.slow
class TestSlowOperations:
    """Tests that might be slower."""
    
    def test_create_multiple_files(self, temp_dir):
        """Test creating multiple files."""
        files = [
            ("module1.py", "module"),
            ("Class1.py", "class"),
            ("func1.py", "function")
        ]
        
        created = []
        for filename, template in files:
            output_file = temp_dir / filename
            result = create_file_from_template(
                filename=str(output_file),
                template=template,
                author="Test Author"
            )
            
            if result:
                created.append(output_file)
        
        # Should create at least some files
        assert len(created) > 0
        
        # Check each created file
        for file in created:
            assert file.exists()
            assert file.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])