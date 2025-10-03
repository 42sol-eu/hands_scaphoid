"""
Create file command module.
"""

import rich_click as click
from rich.console import Console
from pathlib import Path

from .file_creator import (
    create_file_from_template as _create_file,
    create_file_from_copier_template,
    list_templates
)

console = Console()


@click.command()
@click.argument('filename', required=False)
@click.option('--template', '-t', help='Template name to use (use --list to see available)')
@click.option('--author', default='', help='Author name for the file header')
@click.option('--description', default='', help='Description for the file')
@click.option('--license', default='MIT', help='License type')
@click.option('--list', 'list_templates_flag', is_flag=True, help='List available templates')
@click.option('--copier', is_flag=True, help='Use copier template with interactive prompts')
@click.option('--output-dir', default='.', help='Output directory for copier templates')
def create_file(filename, template, author, description, license, list_templates_flag, copier, output_dir):
    """
    📄 **Create a new file** from a template.
    
    This command creates new Python files using Jinja2 templates or advanced
    copier templates with interactive prompts for ItemCore-style classes.
    
    **Examples:**
    
    ```bash
    # List available templates
    do create-file --list
    
    # Create using simple Jinja2 templates
    do create-file mymodule.py --template class --author "John Doe"
    do create-file utils.py --template module --description "Utility functions"
    
    # Create using copier templates (interactive)
    do create-file --copier --template itemcore --output-dir src/
    
    # Create using copier templates (with pre-filled values)
    do create-file MyClass.py --copier --author "John Doe" --description "My class"
    ```
    """
    # List templates if requested
    if list_templates_flag:
        templates = list_templates()
        console.print("\n📄 [bold]Available Templates:[/bold]\n")
        
        # Group templates
        jinja_templates = {k: v for k, v in templates.items() if not k.startswith('copier:')}
        copier_templates = {k: v for k, v in templates.items() if k.startswith('copier:')}
        
        if jinja_templates:
            console.print("[bold cyan]Jinja2 Templates:[/bold cyan]")
            for name, desc in jinja_templates.items():
                console.print(f"  • [green]{name}[/green]: {desc}")
            console.print()
        
        if copier_templates:
            console.print("[bold magenta]Copier Templates:[/bold magenta]")
            for name, desc in copier_templates.items():
                clean_name = name.replace('copier:', '')
                console.print(f"  • [green]{clean_name}[/green]: {desc}")
        
        return
    
    # Handle copier templates
    if copier or (template and template.startswith('copier:')):
        template_name = template.replace('copier:', '') if template else 'itemcore'
        
        # Prepare template variables from command line
        template_vars = {}
        if author:
            template_vars['author'] = author
        if description:
            template_vars['description'] = description
        if filename:
            # Extract class name from filename
            class_name = Path(filename).stem
            template_vars['class_name'] = class_name
            template_vars['filename'] = class_name
        
        success = create_file_from_copier_template(
            output_path=output_dir,
            template_name=template_name,
            interactive=True,  # Always interactive for rich experience
            **template_vars
        )
        
        if success:
            console.print(f"✅ [green]Successfully created files using '{template_name}' template[/green]")
        else:
            console.print(f"❌ [red]Failed to create files from copier template[/red]")
        return
    
    # Require filename for regular templates
    if not filename:
        console.print("❌ [red]Filename is required for regular templates. Use --copier for interactive mode.[/red]")
        return
    
    # Handle regular Jinja2 templates
    success = _create_file(
        filename=filename,
        template=template,
        author=author,
        description=description,
        license=license
    )
    
    if success:
        console.print(f"✅ [green]Successfully created {filename}[/green]")
    else:
        console.print(f"❌ [red]Failed to create {filename}[/red]")