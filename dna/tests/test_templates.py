"""
Test suite for template generation functionality.

Tests the copier template system, Jinja2 templates, and
template discovery mechanisms.
"""

import pytest
from pathlib import Path
import tempfile
import yaml
from unittest.mock import patch, MagicMock

# Import template functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.file_creator import (
    get_available_copier_templates,
    create_file_from_copier_template,
    create_file_from_template,
    list_templates
)


class TestTemplateDiscovery:
    """Test template discovery functionality."""
    
    def test_get_available_copier_templates(self):
        """Test discovering copier templates in subfolders."""
        templates = get_available_copier_templates()
        assert isinstance(templates, dict)
        
        # Should include basic template types
        expected_types = ["itemcore", "data-class", "cli-tool", "readme-project"]
        for template_type in expected_types:
            assert template_type in templates, f"Missing template type: {template_type}"
    
    def test_get_template_list(self):
        """Test getting complete template list."""
        jinja_templates = list_templates()
        copier_templates = get_available_copier_templates()
        
        # Should have some templates
        assert len(jinja_templates) > 0 or len(copier_templates) > 0
        
        # Copier templates should be organized by category
        if copier_templates:
            for category, info in copier_templates.items():
                assert isinstance(info, dict)
                assert "path" in info


class TestCopierTemplateGeneration:
    """Test copier template generation."""
    
    def test_create_itemcore_template(self, temp_dir):
        """Test creating ItemCore template."""
        output_file = temp_dir / "TestItem.py"
        
        # Mock copier.run to avoid actual template generation
        with patch("commands.file_creator.copier.run") as mock_copier:
            mock_copier.return_value = None
            
            result = create_file_from_copier_template(
                template_type="itemcore",
                output_path=str(output_file),
                context={
                    "class_name": "TestItem",
                    "author": "Test Author",
                    "description": "A test item class"
                }
            )
            
            # Should call copier.run
            mock_copier.assert_called_once()
            call_args = mock_copier.call_args
            
            # Verify template path and destination
            template_path = str(call_args[0][0])
            dest_path = str(call_args[0][1])
            
            assert "itemcore" in template_path
            assert str(temp_dir) in dest_path
    
    def test_create_readme_template(self, temp_dir):
        """Test creating README template."""
        output_file = temp_dir / "README.md"
        
        with patch("commands.file_creator.copier.run") as mock_copier:
            mock_copier.return_value = None
            
            result = create_file_from_copier_template(
                template_type="readme-project",
                output_path=str(output_file),
                context={
                    "project_name": "Test Project",
                    "description": "A test project",
                    "author": "Test Author"
                }
            )
            
            mock_copier.assert_called_once()
    
    def test_create_dna_command_template(self, temp_dir):
        """Test creating DNA command template."""
        output_file = temp_dir / "test_command.py"
        
        with patch("commands.file_creator.copier.run") as mock_copier:
            mock_copier.return_value = None
            
            result = create_file_from_copier_template(
                template_type="dna-command",
                output_path=str(output_file),
                context={
                    "command_name": "test-command",
                    "function_name": "test_command",
                    "description": "A test command",
                    "author": "Test Author"
                }
            )
            
            mock_copier.assert_called_once()


class TestJinja2Templates:
    """Test Jinja2 template functionality."""
    
    def test_create_module_template(self, temp_dir):
        """Test creating a module with Jinja2 template."""
        output_file = temp_dir / "test_module.py"
        
        result = create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={
                "module_name": "test_module",
                "author": "Test Author",
                "description": "A test module"
            }
        )
        
        assert result is True
        assert output_file.exists()
        
        # Check content
        content = output_file.read_text()
        assert "test_module" in content
        assert "Test Author" in content
    
    def test_create_class_template(self, temp_dir):
        """Test creating a class with Jinja2 template."""
        output_file = temp_dir / "TestClass.py"
        
        result = create_file_from_template(
            template_name="class",
            output_path=str(output_file),
            context={
                "class_name": "TestClass",
                "author": "Test Author",
                "description": "A test class"
            }
        )
        
        assert result is True
        assert output_file.exists()
        
        # Check content
        content = output_file.read_text()
        assert "class TestClass" in content
        assert "Test Author" in content


class TestTemplateValidation:
    """Test template validation and error handling."""
    
    def test_invalid_template_type(self, temp_dir):
        """Test handling invalid template type."""
        output_file = temp_dir / "test.py"
        
        with patch("commands.file_creator.copier.run") as mock_copier:
            result = create_file_from_copier_template(
                template_type="nonexistent-template",
                output_path=str(output_file),
                context={}
            )
            
            # Should not call copier for invalid template
            mock_copier.assert_not_called()
    
    def test_missing_context_variables(self, temp_dir):
        """Test handling missing required context variables."""
        output_file = temp_dir / "test.py"
        
        # This should still work but might use defaults
        result = create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={}  # Empty context
        )
        
        # Should create file even with missing context
        assert result is True
        assert output_file.exists()


class TestTemplateContent:
    """Test generated template content quality."""
    
    def test_module_template_structure(self, temp_dir):
        """Test that module template has proper structure."""
        output_file = temp_dir / "example_module.py"
        
        create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={
                "module_name": "example_module",
                "author": "Test Author",
                "description": "Example module for testing"
            }
        )
        
        content = output_file.read_text()
        
        # Should have docstring
        assert '"""' in content
        
        # Should have imports section
        assert "import" in content or "from" in content
        
        # Should have main guard
        assert 'if __name__ == "__main__"' in content
    
    def test_class_template_structure(self, temp_dir):
        """Test that class template has proper structure."""
        output_file = temp_dir / "ExampleClass.py"
        
        create_file_from_template(
            template_name="class",
            output_path=str(output_file),
            context={
                "class_name": "ExampleClass",
                "author": "Test Author",
                "description": "Example class for testing"
            }
        )
        
        content = output_file.read_text()
        
        # Should have class definition
        assert "class ExampleClass" in content
        
        # Should have __init__ method
        assert "def __init__" in content
        
        # Should have docstring
        assert '"""' in content


@pytest.mark.integration
class TestTemplateIntegration:
    """Integration tests for template system."""
    
    def test_copier_template_files_exist(self):
        """Test that copier template files exist."""
        templates = get_available_copier_templates()
        
        for template_type, template_info in templates.items():
            template_path = Path(template_info["path"])
            copier_yml = template_path / "copier.yml"
            
            assert template_path.exists(), f"Template directory missing: {template_path}"
            assert copier_yml.exists(), f"copier.yml missing: {copier_yml}"
            
            # Validate copier.yml content
            with open(copier_yml, "r") as f:
                config = yaml.safe_load(f)
                assert isinstance(config, dict), f"Invalid copier.yml: {copier_yml}"
    
    def test_template_directory_structure(self):
        """Test template directory structure."""
        templates_dir = Path(__file__).parent.parent / "commands" / "_templates"
        assert templates_dir.exists()
        
        # Should have subdirectories for different template types
        subdirs = [d for d in templates_dir.iterdir() if d.is_dir()]
        assert len(subdirs) > 0, "No template subdirectories found"
        
        # Each subdirectory should have copier.yml
        for subdir in subdirs:
            copier_yml = subdir / "copier.yml"
            assert copier_yml.exists(), f"Missing copier.yml in {subdir}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])