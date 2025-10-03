"""
PythonProjectHandler class module.
---yaml
File:
    name:   PythonProjectHandler.py
    uuid:   r2s8t4u0-1v6w-7x3y-op4q-6r7s8t9u0v1w
    date:   2025-09-30

Description:
    Handler for Python projects with structure initialization and info gathering

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Standard library imports]
from typing import Any, Dict, List

# [Project base imports]
from ....__base__ import logger, Path, PathLike

# [Local imports]
from ..DirectoryHandler import DirectoryHandler


class PythonProjectHandler(DirectoryHandler):
    """Handler for Python projects."""
    
    def validate(self, dir_path: PathLike) -> bool:
        """Check if directory is a Python project."""
        path = Path(dir_path)
        python_indicators = [
            'setup.py', 'pyproject.toml', 'requirements.txt', 
            'Pipfile', 'setup.cfg', 'environment.yml'
        ]
        return any((path / indicator).exists() for indicator in python_indicators)
    
    def initialize(self, dir_path: PathLike, project_name: str = None, **kwargs) -> bool:
        """Initialize Python project structure."""
        path = Path(dir_path)
        project_name = project_name or path.name
        
        try:
            # Create basic structure
            (path / 'src' / project_name).mkdir(parents=True, exist_ok=True)
            (path / 'tests').mkdir(exist_ok=True)
            (path / 'docs').mkdir(exist_ok=True)
            
            # Create basic files
            (path / 'src' / project_name / '__init__.py').touch()
            (path / 'README.md').write_text(f'# {project_name}\n\nA Python project.')
            (path / 'requirements.txt').touch()
            
            logger.info(f"Initialized Python project structure at {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Python project: {e}")
            return False
    
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get Python project information."""
        path = Path(dir_path)
        
        return {
            'type': 'python_project',
            'has_setup_py': (path / 'setup.py').exists(),
            'has_pyproject_toml': (path / 'pyproject.toml').exists(),
            'has_requirements': (path / 'requirements.txt').exists(),
            'has_src_layout': (path / 'src').exists(),
            'has_tests': (path / 'tests').exists(),
            'has_docs': (path / 'docs').exists(),
            'python_files_count': len(list(path.rglob('*.py'))),
            'package_directories': [d.name for d in path.rglob('*') if d.is_dir() and (d / '__init__.py').exists()]
        }
    
    def list_contents(self, dir_path: PathLike, pattern: str = "*.py") -> List[Path]:
        """List Python files in project."""
        return list(Path(dir_path).rglob(pattern))