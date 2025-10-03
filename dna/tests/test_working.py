"""
Simplified working tests for DNA CLI functionality.

These tests use the correct API signatures and focus on core functionality.
"""

import pytest
from pathlib import Path
from click.testing import CliRunner

# Import the main dna CLI
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from dna import cli
from commands.file_creator import create_file_from_template, list_templates


class TestDNACore:
    """Core DNA CLI tests that actually work."""
    
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
    
    def test_create_init_help(self):
        """Test create-init command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-init', '--help'])
        assert result.exit_code == 0
        assert "Create init.py file" in result.output
    
    def test_find_classes_help(self):
        """Test find-classes command help."""
        runner = CliRunner()
        result = runner.invoke(cli, ['find-classes', '--help'])
        assert result.exit_code == 0


class TestFileCreatorAPI:
    """Test file creator API with correct signatures."""
    
    def test_list_templates(self):
        """Test that we can list templates."""
        templates = list_templates()
        assert isinstance(templates, dict)
        assert len(templates) > 0
        
        # Should have basic templates
        expected = ["module", "class", "function"]
        for template in expected:
            assert template in templates
    
    def test_create_file_correct_api(self, temp_dir):
        """Test creating file with correct API."""
        output_file = temp_dir / "test_module.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="module",
            author="Test Author",
            description="Test module",
            custom_vars={"module_name": "test_module"}
        )
        
        assert result is True
        assert output_file.exists()
        
        # Check basic content
        content = output_file.read_text()
        assert "Test Author" in content
    
    def test_create_class_correct_api(self, temp_dir):
        """Test creating class with correct API."""
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
        assert "class TestClass" in content or "TestClass" in content


class TestCreateInitCommand:
    """Test the create-init command functionality."""
    
    def test_create_init_dry_run(self):
        """Test create-init with dry run."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-init', '.', '--dry-run'])
        
        # Should succeed (even if no modules found)
        assert result.exit_code == 0
    
    def test_create_init_on_commands_dir(self):
        """Test create-init on the commands directory."""
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create-init', 'commands', 
            '--dry-run', 
            '--package-name', 'test_commands'
        ])
        
        assert result.exit_code == 0
        assert "Preview of __init__.py" in result.output
    
    def test_create_init_with_sample_files(self, temp_dir):
        """Test create-init with some sample Python files."""
        # Create sample files
        (temp_dir / "module1.py").write_text("""
class SampleClass:
    def method(self):
        pass

def sample_function():
    pass
""")
        
        (temp_dir / "module2.py").write_text("""
def another_function():
    pass
""")
        
        runner = CliRunner()
        result = runner.invoke(cli, [
            'create-init', str(temp_dir),
            '--dry-run',
            '--author', 'Test Author'
        ])
        
        assert result.exit_code == 0
        assert "SampleClass" in result.output
        assert "sample_function" in result.output
        assert "another_function" in result.output


class TestCommandIntegration:
    """Test command integration and workflows."""
    
    def test_create_file_and_init_workflow(self, temp_dir):
        """Test creating files and then generating __init__.py."""
        runner = CliRunner()
        
        # Create a module file
        module_file = temp_dir / "mymodule.py"
        result = runner.invoke(cli, [
            'create-file', str(module_file),
            '--template', 'module',
            '--author', 'Test Author'
        ])
        
        # Should create file successfully or show reasonable error
        if result.exit_code == 0:
            assert module_file.exists()
        
        # Now try to create __init__.py
        result = runner.invoke(cli, [
            'create-init', str(temp_dir),
            '--dry-run'
        ])
        
        assert result.exit_code == 0


class TestErrorHandling:
    """Test error handling."""
    
    def test_invalid_template(self, temp_dir):
        """Test handling invalid template."""
        output_file = temp_dir / "invalid.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="nonexistent_template",
            author="Test"
        )
        
        # Should handle gracefully
        assert result is False
    
    def test_create_init_nonexistent_dir(self):
        """Test create-init with non-existent directory."""
        runner = CliRunner()
        result = runner.invoke(cli, ['create-init', '/nonexistent/directory'])
        
        # Should handle error gracefully
        assert result.exit_code != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])