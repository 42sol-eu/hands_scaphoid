"""
PythonScriptHandler class module.
---yaml
File:
    name:   PythonScriptHandler.py
    uuid:   t4u0v6w2-3x8y-9z5a-qr6s-8t9u0v1w2x3y
    date:   2025-09-30

Description:
    Handler for Python scripts with execution and validation

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import ast
import subprocess
from typing import Any, Dict, List

#%% [Project base imports]
from ....__base__ import Path, PathLike

#%% [Local imports]
from .ExecutableHandler import ExecutableHandler


class PythonScriptHandler(ExecutableHandler):
    """Handler for Python scripts."""
    
    def execute(self, exe_path: PathLike, args: List[str] = None, **kwargs) -> Dict[str, Any]:
        """Execute Python script."""
        cmd = ['python', str(exe_path)] + (args or [])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, **kwargs)
            return {
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'returncode': -1,
                'stdout': '',
                'stderr': str(e),
                'success': False,
                'error': str(e)
            }
    
    def validate(self, exe_path: PathLike) -> bool:
        """Validate Python script syntax."""
        try:
            with open(exe_path, 'r', encoding='utf-8') as f:
                content = f.read()
            compile(content, exe_path, 'exec')
            return True
        except (SyntaxError, OSError, UnicodeDecodeError):
            return False
    
    def get_info(self, exe_path: PathLike) -> Dict[str, Any]:
        """Get Python script information."""
        path = Path(exe_path)
        info = {
            'type': 'python_script',
            'size_bytes': path.stat().st_size,
            'is_valid': self.validate(exe_path),
            'has_shebang': False,
            'imports': []
        }
        
        try:
            with open(exe_path, 'r', encoding='utf-8') as f:
                first_line = f.readline().strip()
                if first_line.startswith('#!') and 'python' in first_line:
                    info['has_shebang'] = True
                
                # Simple import detection
                f.seek(0)
                content = f.read()
                tree = ast.parse(content)
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        info['imports'].extend(alias.name for alias in node.names)
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            info['imports'].append(node.module)
        except Exception as e:
            info['parse_error'] = str(e)
        
        return info