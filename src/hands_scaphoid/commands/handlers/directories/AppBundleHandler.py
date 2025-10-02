"""
AppBundleHandler class module.
---yaml
File:
    name:   AppBundleHandler.py
    uuid:   y9z5a1b7-8c3d-4e0f-yz1a-3y4z5a6b7c8d
    date:   2025-09-30

Description:
    Handler for macOS app bundles (.app) - treated as special ZIP archives

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Project base imports]
from ....__base__ import logger, PathLike

#%% [Local imports]
from ..archives.ZipArchiveHandler import ZipArchiveHandler


class AppBundleHandler(ZipArchiveHandler):
    """Handler for macOS app bundles (.app) - treated as special ZIP archives."""
    
    def validate_app_structure(self, archive_path: PathLike) -> bool:
        """Validate that the archive has proper .app bundle structure."""
        required_files = [
            'Contents/Info.plist',
            'Contents/MacOS/'
        ]
        
        files = self.list_files(archive_path)
        for required in required_files:
            if not any(f.startswith(required) for f in files):
                logger.warning(f"App bundle {archive_path} missing required: {required}")
                return False
        
        logger.debug(f"App bundle {archive_path} structure validation passed")
        return True
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract app bundle with structure validation."""
        if not self.validate_app_structure(archive_path):
            logger.error(f"App bundle {archive_path} has invalid structure")
            return False
        
        return super().extract(archive_path, extract_to)