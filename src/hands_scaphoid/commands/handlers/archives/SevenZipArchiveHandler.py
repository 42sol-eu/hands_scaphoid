"""
SevenZipArchiveHandler class module.
---yaml
File:
    name:   SevenZipArchiveHandler.py
    uuid:   x8y4z0a6-7b2c-3d9e-wx0y-2x3y4z5a6b7c
    date:   2025-09-30

Description:
    Handler for 7-Zip archives (.7z) using external 7z command

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import shutil
import subprocess
from typing import List, Optional

#%% [Project base imports]
from ....__base__ import logger, PathLike

#%% [Local imports]
from ..ArchiveHandler import ArchiveHandler


class SevenZipArchiveHandler(ArchiveHandler):
    """Handler for 7-Zip archives (.7z) using external 7z command."""
    
    def __init__(self):
        """Initialize and check for 7z availability."""
        self.seven_zip_cmd = self._find_seven_zip()
    
    def _find_seven_zip(self) -> Optional[str]:
        """Find 7z executable."""
        for cmd in ['7z', '7za', '7zz']:
            if shutil.which(cmd):
                return cmd
        return None
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract 7z archive using external command."""
        if not self.seven_zip_cmd:
            logger.error("7-Zip command not found")
            return False
        
        try:
            result = subprocess.run([
                self.seven_zip_cmd, 'x', str(archive_path), 
                f'-o{extract_to}', '-y'
            ], capture_output=True, text=True, check=True)
            logger.info(f"Extracted 7z archive {archive_path} to {extract_to}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to extract 7z archive {archive_path}: {e}")
            return False
    
    def pack(self, source_path: PathLike, archive_path: PathLike, **kwargs) -> bool:
        """Create 7z archive using external command."""
        if not self.seven_zip_cmd:
            logger.error("7-Zip command not found")
            return False
        
        try:
            result = subprocess.run([
                self.seven_zip_cmd, 'a', str(archive_path), str(source_path)
            ], capture_output=True, text=True, check=True)
            logger.info(f"Created 7z archive {archive_path} from {source_path}")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to create 7z archive {archive_path}: {e}")
            return False
    
    def test(self, archive_path: PathLike) -> bool:
        """Test 7z archive integrity."""
        if not self.seven_zip_cmd:
            logger.error("7-Zip command not found")
            return False
        
        try:
            result = subprocess.run([
                self.seven_zip_cmd, 't', str(archive_path)
            ], capture_output=True, text=True, check=True)
            logger.debug(f"7z archive {archive_path} integrity test passed")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"7z archive {archive_path} integrity test failed: {e}")
            return False
    
    def list_files(self, archive_path: PathLike) -> List[str]:
        """List files in 7z archive."""
        if not self.seven_zip_cmd:
            logger.error("7-Zip command not found")
            return []
        
        try:
            result = subprocess.run([
                self.seven_zip_cmd, 'l', str(archive_path)
            ], capture_output=True, text=True, check=True)
            
            # Parse 7z output to extract file names
            files = []
            in_file_list = False
            for line in result.stdout.split('\n'):
                if '---' in line and 'Name' in line:
                    in_file_list = True
                    continue
                if in_file_list and line.strip():
                    if '---' in line:
                        break
                    # Extract filename from 7z list output
                    parts = line.split()
                    if len(parts) >= 6:
                        filename = ' '.join(parts[5:])
                        files.append(filename)
            
            return files
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to list files in 7z archive {archive_path}: {e}")
            return []