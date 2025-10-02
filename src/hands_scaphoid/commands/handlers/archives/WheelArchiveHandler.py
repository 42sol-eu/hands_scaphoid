"""
WheelArchiveHandler class module.
---yaml
File:
    name:   WheelArchiveHandler.py
    uuid:   z0a6b2c8-9d4e-5f1g-za2b-4z5a6b7c8d9e
    date:   2025-09-30

Description:
    Handler for Python wheel files (.whl) with metadata validation

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Project base imports]
from ....__base__ import logger, PathLike

#%% [Local imports]
from ..ArchiveHandler import ArchiveHandler
from .ZipArchiveHandler import ZipArchiveHandler


class WheelArchiveHandler(ZipArchiveHandler):
    """Handler for Python wheel files (.whl) with metadata validation."""
    
    def validate_wheel_structure(self, archive_path: PathLike) -> bool:
        """Validate that the archive has proper wheel structure."""
        files = self.list_files(archive_path)
        
        # Check for METADATA file
        has_metadata = any(f.endswith('/METADATA') or f == 'METADATA' for f in files)
        has_wheel_info = any('.dist-info' in f for f in files)
        
        if not (has_metadata and has_wheel_info):
            logger.warning(f"Wheel {archive_path} missing required metadata structure")
            return False
        
        logger.debug(f"Wheel {archive_path} structure validation passed")
        return True
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract wheel with structure validation."""
        if not self.validate_wheel_structure(archive_path):
            logger.error(f"Wheel {archive_path} has invalid structure")
            return False
        
        return super().extract(archive_path, extract_to)