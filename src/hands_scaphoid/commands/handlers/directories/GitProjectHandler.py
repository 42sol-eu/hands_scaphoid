"""
GitProjectHandler class module.
---yaml
File:
    name:   GitProjectHandler.py
    uuid:   q1r7s3t9-0u5v-6w2x-no3p-5q6r7s8t9u0v
    date:   2025-09-30

Description:
    Handler for Git repositories with initialization and info gathering

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Standard library imports]
import subprocess
from typing import Any, Dict, List

# [Project base imports]
from ....__base__ import logger, Path, PathLike

# [Local imports]
from ..DirectoryHandler import DirectoryHandler


class GitProjectHandler(DirectoryHandler):
    """Handler for Git repositories."""
    
    def validate(self, dir_path: PathLike) -> bool:
        """Check if directory is a valid Git repository."""
        git_dir = Path(dir_path) / '.git'
        return git_dir.exists() and (git_dir.is_dir() or git_dir.is_file())
    
    def initialize(self, dir_path: PathLike, **kwargs) -> bool:
        """Initialize Git repository."""
        try:
            result = subprocess.run(['git', 'init', str(dir_path)], 
                                  capture_output=True, text=True, check=True)
            logger.info(f"Initialized Git repository at {dir_path}")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            logger.error(f"Failed to initialize Git repository: {e}")
            return False
    
    def get_structure_info(self, dir_path: PathLike) -> Dict[str, Any]:
        """Get Git repository information."""
        path = Path(dir_path)
        info = {
            'type': 'git_repository',
            'has_git_dir': (path / '.git').exists(),
            'has_gitignore': (path / '.gitignore').exists(),
            'has_readme': any((path / f).exists() for f in ['README.md', 'README.txt', 'README'])
        }
        
        if self.validate(dir_path):
            try:
                # Get current branch
                result = subprocess.run(['git', 'branch', '--show-current'], 
                                      cwd=dir_path, capture_output=True, text=True)
                info['current_branch'] = result.stdout.strip() if result.returncode == 0 else None
                
                # Get remote info
                result = subprocess.run(['git', 'remote', '-v'], 
                                      cwd=dir_path, capture_output=True, text=True)
                info['has_remote'] = bool(result.stdout.strip()) if result.returncode == 0 else False
                
            except Exception as e:
                logger.warning(f"Failed to get Git info for {dir_path}: {e}")
        
        return info
    
    def list_contents(self, dir_path: PathLike, pattern: str = "*") -> List[Path]:
        """List Git repository contents, respecting .gitignore."""
        try:
            # Use git ls-files to respect .gitignore
            result = subprocess.run(['git', 'ls-files'], 
                                  cwd=dir_path, capture_output=True, text=True)
            if result.returncode == 0:
                files = [Path(dir_path) / f.strip() for f in result.stdout.split('\n') if f.strip()]
                return [f for f in files if f.match(pattern)]
        except Exception:
            pass
        
        # Fallback to regular directory listing
        return list(Path(dir_path).glob(pattern))