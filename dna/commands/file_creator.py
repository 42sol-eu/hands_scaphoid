"""
File creator utility using Jinja2 templates and copier.

This module provides functionality to create new Python files from templates
with customizable headers and content. Supports both simple Jinja2 templates
and advanced copier templates with interactive prompts.
"""

import os
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

try:
    from jinja2 import Environment, BaseLoader, Template
except ImportError:
    print("Jinja2 is required. Install it with: uv add jinja2")
    raise

try:
    import copier
    COPIER_AVAILABLE = True
except ImportError:
    COPIER_AVAILABLE = False
    print("Copier not available. Advanced template features disabled.")

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class StringTemplateLoader(BaseLoader):
    """A simple template loader that works with string templates."""
    
    def __init__(self, templates: Dict[str, str]):
        self.templates = templates
    
    def get_source(self, environment: Environment, template: str) -> tuple:
        if template not in self.templates:
            raise FileNotFoundError(f"Template '{template}' not found")
        
        source = self.templates[template]
        return source, None, lambda: True


# Default templates
DEFAULT_TEMPLATES = {
    'module': '''"""
{{ description or 'Module: ' + filename }}

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""

# Add your module code here
''',

    'class': '''"""
{{ description or 'Module containing the ' + class_name + ' class.' }}

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""


class {{ class_name }}:
    """
    {{ class_description or 'A class that does something useful.' }}
    
    Attributes:
        # Add your attributes here
        
    Methods:
        # Add your methods here
    """
    
    def __init__(self):
        """Initialize the {{ class_name }}."""
        pass
    
    def __repr__(self) -> str:
        """Return a string representation of the {{ class_name }}."""
        return f"{{ class_name }}()"
''',

    'function': '''"""
{{ description or 'Module containing utility functions.' }}

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""


def {{ function_name }}():
    """
    {{ function_description or 'A function that does something useful.' }}
    
    Args:
        # Add your arguments here
        
    Returns:
        # Add your return type here
        
    Raises:
        # Add your exceptions here
    """
    pass
''',

    'test': '''"""
Tests for {{ test_module }}.

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""

import pytest
from {{ module_path }} import {{ test_class or 'YourClass' }}


class Test{{ test_class or 'YourClass' }}:
    """Test cases for {{ test_class or 'YourClass' }}."""
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        pass
    
    def teardown_method(self):
        """Tear down test fixtures after each test method."""
        pass
    
    def test_example(self):
        """Test example functionality."""
        # Add your test code here
        assert True
''',

    'script': '''#!/usr/bin/env python3
"""
{{ description or 'A Python script that does something useful.' }}

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""

import argparse
import sys
from pathlib import Path


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="{{ description or 'Script description' }}")
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    args = parser.parse_args()
    
    if args.verbose:
        print("Running in verbose mode...")
    
    # Add your script logic here
    print("Hello, World!")


if __name__ == "__main__":
    main()
''',

    'package': '''"""
{{ package_name }} package.

{{ description or 'A Python package that provides useful functionality.' }}

{% if author %}Author: {{ author }}{% endif %}
{% if license %}License: {{ license }}{% endif %}
Created: {{ created_date }}
"""

__version__ = "0.1.0"
__author__ = "{{ author or 'Your Name' }}"

# Import main classes/functions here
# from .module import YourClass

__all__ = [
    # Add your public API here
    # "YourClass",
]
'''
}


def create_file_from_template(
    filename: str,
    template: Optional[str] = None,
    author: str = "",
    description: str = "",
    license: str = "MIT",
    custom_vars: Optional[Dict[str, Any]] = None,
    template_content: Optional[str] = None
) -> bool:
    """
    Create a new file from a template.
    
    Args:
        filename: Name of the file to create
        template: Template name to use (or None for custom template)
        author: Author name for the file header
        description: Description for the file
        license: License type
        custom_vars: Additional variables for template rendering
        template_content: Custom template content (if template is None)
        
    Returns:
        True if file was created successfully, False otherwise
    """
    filepath = Path(filename)
    
    # Check if file already exists
    if filepath.exists():
        print(f"File {filename} already exists. Use --force to overwrite.")
        return False
    
    # Prepare template variables
    template_vars = {
        'filename': filepath.name,
        'author': author,
        'description': description,
        'license': license,
        'created_date': datetime.now().strftime('%Y-%m-%d'),
        'created_datetime': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # Add derived variables based on filename
    stem = filepath.stem
    template_vars.update({
        'class_name': _to_class_name(stem),
        'function_name': _to_function_name(stem),
        'package_name': stem,
        'test_module': stem,
        'test_class': _to_class_name(stem),
        'module_path': stem,
    })
    
    # Add custom variables
    if custom_vars:
        template_vars.update(custom_vars)
    
    # Create Jinja2 environment
    if template_content:
        # Use custom template content
        template_obj = Template(template_content)
    else:
        # Use predefined template
        if template not in DEFAULT_TEMPLATES:
            available = ', '.join(DEFAULT_TEMPLATES.keys())
            print(f"Template '{template}' not found. Available templates: {available}")
            return False
        
        loader = StringTemplateLoader(DEFAULT_TEMPLATES)
        env = Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)
        template_obj = env.get_template(template)
    
    try:
        # Render template
        content = template_obj.render(**template_vars)
        
        # Create directory if it doesn't exist
        filepath.parent.mkdir(parents=True, exist_ok=True)
        
        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return True
        
    except Exception as e:
        print(f"Error creating file: {e}")
        return False


def create_file_from_copier_template(
    output_path: str = ".",
    template_name: str = "itemcore",
    interactive: bool = True,
    **template_vars
) -> bool:
    """
    Create files from copier templates with interactive prompts.
    
    Args:
        output_path: Directory where files will be created
        template_name: Name of the copier template to use (subfolder name)
        interactive: Whether to prompt user for template variables
        **template_vars: Pre-defined template variables
        
    Returns:
        True if files were created successfully, False otherwise
    """
    if not COPIER_AVAILABLE:
        print("❌ Copier is not available. Please install it first.")
        return False
    
    # Get the specific template directory
    templates_base_dir = Path(__file__).parent / "_templates"
    template_dir = templates_base_dir / template_name
    
    if not templates_base_dir.exists():
        print(f"❌ Templates base directory not found: {templates_base_dir}")
        return False
    
    if not template_dir.exists():
        available_templates = list(get_available_copier_templates().keys())
        print(f"❌ Template '{template_name}' not found. Available templates: {', '.join(available_templates)}")
        return False
    
    # Check if copier.yml exists in the template directory
    copier_config = template_dir / "copier.yml"
    if not copier_config.exists():
        print(f"❌ Copier configuration not found: {copier_config}")
        return False
    
    try:
        # Prepare template variables with defaults
        data = {
            "current_date": datetime.now().strftime('%Y-%m-%d'),
            "uuid": str(uuid.uuid4()),
            **template_vars
        }
        
        # Use copier to generate files
        if interactive:
            # Interactive mode - copier will prompt for variables
            copier.run_copy(
                src_path=str(template_dir),
                dst_path=output_path,
                data=data,
                answers_file=None,
                overwrite=True,
                pretend=False
            )
        else:
            # Non-interactive mode - use provided data
            copier.run_copy(
                src_path=str(template_dir),
                dst_path=output_path,
                data=data,
                answers_file=None,
                overwrite=True,
                pretend=False,
                defaults=True
            )
        
        print(f"✅ Successfully created files using '{template_name}' template")
        return True
        
    except Exception as e:
        print(f"❌ Error creating files from copier template: {e}")
        return False


def get_available_copier_templates() -> Dict[str, str]:
    """
    Get list of available copier templates by scanning subfolders.
    
    Returns:
        Dictionary mapping template names to descriptions
    """
    templates_base_dir = Path(__file__).parent / "_templates"
    
    if not templates_base_dir.exists():
        return {}
    
    templates = {}
    
    # Scan for template subfolders containing copier.yml
    for template_dir in templates_base_dir.iterdir():
        if not template_dir.is_dir():
            continue
            
        copier_config = template_dir / "copier.yml"
        if not copier_config.exists():
            continue
            
        template_name = template_dir.name
        
        # Try to read description from copier.yml metadata
        try:
            if YAML_AVAILABLE:
                with open(copier_config, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                
                metadata = config.get('_metadata', {})
                description = metadata.get('description', f'{template_name.title()} template')
            else:
                description = f'{template_name.title()} template'
                
            templates[template_name] = description
            
        except Exception:
            # Fallback description if YAML parsing fails
            templates[template_name] = f'{template_name.title()} template'
    
    return templates


def list_templates() -> Dict[str, str]:
    """
    List available templates with descriptions.
    
    Returns:
        Dictionary mapping template names to descriptions
    """
    descriptions = {
        'module': 'Basic Python module with docstring',
        'class': 'Python module with a class definition',
        'function': 'Python module with a function definition',
        'test': 'Test file using pytest',
        'script': 'Executable Python script with argparse',
        'package': 'Package __init__.py file',
    }
    
    # Add copier templates if available
    if COPIER_AVAILABLE:
        copier_templates = get_available_copier_templates()
        for name, desc in copier_templates.items():
            descriptions[f"copier:{name}"] = f"Copier: {desc}"
    
    return descriptions


def _to_class_name(name: str) -> str:
    """Convert a string to a valid class name (PascalCase)."""
    # Remove file extension and split on common separators
    name = Path(name).stem
    parts = name.replace('-', '_').replace(' ', '_').split('_')
    return ''.join(word.capitalize() for word in parts if word)


def _to_function_name(name: str) -> str:
    """Convert a string to a valid function name (snake_case)."""
    # Remove file extension and convert to snake_case
    name = Path(name).stem
    name = name.replace('-', '_').replace(' ', '_')
    # Remove any non-alphanumeric characters except underscores
    name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name)
    # Remove multiple consecutive underscores
    while '__' in name:
        name = name.replace('__', '_')
    # Remove leading/trailing underscores
    name = name.strip('_')
    # Ensure it doesn't start with a number
    if name and name[0].isdigit():
        name = f"func_{name}"
    return name or 'my_function'


def create_custom_template(template_name: str, template_content: str) -> bool:
    """
    Create a custom template file.
    
    Args:
        template_name: Name of the template
        template_content: Content of the template
        
    Returns:
        True if template was created successfully
    """
    # This could be extended to save custom templates to a user directory
    # For now, just validate the template content
    try:
        Template(template_content)
        print(f"Template '{template_name}' is valid Jinja2 syntax")
        return True
    except Exception as e:
        print(f"Invalid template syntax: {e}")
        return False