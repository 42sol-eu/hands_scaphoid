"""
Test suite for file creator functionality.

Tests the core file creation functions including template
selection, file generation, and error handling.
"""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Import file creator functions
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.file_creator import (
    create_file_from_template,
    create_file_from_copier_template,
    list_templates,
    get_available_copier_templates
)


class TestFileCreation:
    """Test basic file creation functionality."""
    
    def test_create_simple_python_file(self, temp_dir):
        """Test creating a simple Python file."""
        output_file = temp_dir / "simple_module.py"
        
        result = create_file_from_template(
            filename=str(output_file),
            template="module",
            author="Test Author",
            description="A simple test module",
            custom_vars={"module_name": "simple_module"}
        )
        
        assert result is True
        assert output_file.exists()
        assert output_file.suffix == ".py"
    
    def test_create_class_file(self, temp_dir):
        """Test creating a class file."""
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
        
        # Verify class content
        content = output_file.read_text()
        assert "class TestClass" in content
        assert "def __init__" in content
    
    def test_create_file_with_empty_context(self, temp_dir):
        """Test creating file with minimal context."""
        output_file = temp_dir / "minimal.py"
        
        result = create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={}
        )
        
        assert result is True
        assert output_file.exists()


class TestCopierIntegration:
    """Test copier template integration."""
    
    @patch('commands.file_creator.copier.run')
    def test_copier_template_call(self, mock_copier, temp_dir):
        """Test that copier is called correctly."""
        mock_copier.return_value = None
        
        output_file = temp_dir / "test_item.py"
        
        result = create_file_from_copier_template(
            template_type="itemcore",
            output_path=str(output_file),
            context={
                "class_name": "TestItem",
                "author": "Test Author"
            }
        )
        
        # Verify copier was called
        mock_copier.assert_called_once()
        
        # Check call arguments
        call_args = mock_copier.call_args
        assert len(call_args[0]) >= 2  # template_path, destination
        
        # Template path should contain 'itemcore'
        template_path = str(call_args[0][0])
        assert "itemcore" in template_path
    
    @patch('commands.file_creator.copier.run')
    def test_copier_with_data_class_template(self, mock_copier, temp_dir):
        """Test copier with data class template."""
        mock_copier.return_value = None
        
        output_file = temp_dir / "DataClass.py"
        
        result = create_file_from_copier_template(
            template_type="data-class",
            output_path=str(output_file),
            context={
                "class_name": "DataClass",
                "fields": ["name", "value"],
                "author": "Test Author"
            }
        )
        
        mock_copier.assert_called_once()
        
        # Verify template type in path
        template_path = str(mock_copier.call_args[0][0])
        assert "data-class" in template_path


class TestTemplateDiscoveryDetailed:
    """Detailed tests for template discovery."""
    
    def test_template_paths_exist(self):
        """Test that template paths actually exist."""
        templates = get_available_copier_templates()
        
        for template_type, info in templates.items():
            template_path = Path(info["path"])
            assert template_path.exists(), f"Template path does not exist: {template_path}"
            assert template_path.is_dir(), f"Template path is not a directory: {template_path}"
    
    def test_template_has_required_files(self):
        """Test that templates have required files."""
        templates = get_available_copier_templates()
        
        for template_type, info in templates.items():
            template_path = Path(info["path"])
            copier_yml = template_path / "copier.yml"
            
            assert copier_yml.exists(), f"Missing copier.yml in {template_type}: {copier_yml}"
    
    def test_jinja_templates_discoverable(self):
        """Test that Jinja2 templates are discoverable."""
        jinja_templates = list_templates()
        
        # Should have basic templates
        expected_templates = ["module", "class", "function"]
        for template in expected_templates:
            assert template in jinja_templates, f"Missing Jinja2 template: {template}"


class TestErrorHandling:
    """Test error handling in file creation."""
    
    def test_invalid_template_name(self, temp_dir):
        """Test handling of invalid template names."""
        output_file = temp_dir / "test.py"
        
        result = create_file_from_template(
            template_name="nonexistent_template",
            output_path=str(output_file),
            context={}
        )
        
        # Should fail gracefully
        assert result is False
        assert not output_file.exists()
    
    def test_invalid_output_path(self):
        """Test handling of invalid output paths."""
        # Try to create file in non-existent directory
        invalid_path = "/nonexistent/directory/file.py"
        
        result = create_file_from_template(
            template_name="module",
            output_path=invalid_path,
            context={}
        )
        
        # Should fail gracefully
        assert result is False
    
    @patch('commands.file_creator.copier.run')
    def test_copier_failure_handling(self, mock_copier, temp_dir):
        """Test handling of copier failures."""
        # Make copier raise an exception
        mock_copier.side_effect = Exception("Copier failed")
        
        output_file = temp_dir / "test.py"
        
        result = create_file_from_copier_template(
            template_type="itemcore",
            output_path=str(output_file),
            context={}
        )
        
        # Should handle the exception gracefully
        assert result is False or result is None


class TestFileContent:
    """Test the content of generated files."""
    
    def test_module_content_structure(self, temp_dir):
        """Test that generated module has proper structure."""
        output_file = temp_dir / "structured_module.py"
        
        create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={
                "module_name": "structured_module",
                "author": "Test Author",
                "description": "A well-structured module"
            }
        )
        
        content = output_file.read_text()
        
        # Should have proper Python structure
        assert content.startswith('"""') or content.startswith("#")  # Header comment
        assert "def " in content or "class " in content  # Some definition
        assert content.strip().endswith('"""') or 'if __name__' in content  # Proper ending
    
    def test_class_content_methods(self, temp_dir):
        """Test that generated class has proper methods."""
        output_file = temp_dir / "MethodClass.py"
        
        create_file_from_template(
            template_name="class",
            output_path=str(output_file),
            context={
                "class_name": "MethodClass",
                "author": "Test Author"
            }
        )
        
        content = output_file.read_text()
        
        # Should have essential class methods
        assert "def __init__" in content
        assert "def __str__" in content or "def __repr__" in content
    
    def test_author_information_included(self, temp_dir):
        """Test that author information is properly included."""
        output_file = temp_dir / "authored_file.py"
        author_name = "John Doe <john@example.com>"
        
        create_file_from_template(
            template_name="module",
            output_path=str(output_file),
            context={
                "module_name": "authored_file",
                "author": author_name
            }
        )
        
        content = output_file.read_text()
        assert author_name in content or "John Doe" in content


@pytest.mark.integration
class TestFileCreatorIntegration:
    """Integration tests for file creator."""
    
    def test_create_multiple_files(self, temp_dir):
        """Test creating multiple files in sequence."""
        files_to_create = [
            ("module1.py", "module", {"module_name": "module1"}),
            ("Class1.py", "class", {"class_name": "Class1"}),
            ("module2.py", "module", {"module_name": "module2"}),
        ]
        
        created_files = []
        for filename, template, context in files_to_create:
            output_file = temp_dir / filename
            context["author"] = "Test Author"
            
            result = create_file_from_template(
                template_name=template,
                output_path=str(output_file),
                context=context
            )
            
            assert result is True
            assert output_file.exists()
            created_files.append(output_file)
        
        # All files should exist
        assert len(created_files) == 3
        for file in created_files:
            assert file.exists()
            assert file.stat().st_size > 0  # Not empty


if __name__ == "__main__":
    pytest.main([__file__, "-v"])