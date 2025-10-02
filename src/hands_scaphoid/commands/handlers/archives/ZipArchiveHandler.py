"""
ZipArchiveHandler class module.
---yaml
File:
    name:   ZipArchiveHandler.py
    uuid:   v6w2x8y4-5z0a-1b7c-st8u-0v1w2x3y4z5a
    date:   2025-09-30

Description:
    Handler for ZIP-based archives (.zip, .whl, .docx, .xlsx, etc.)

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scaphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import zipfile
from pathlib import Path
from typing import List

#%% [Project base imports]
from ....__base__ import logger, PathLike

#%% [Local imports]
from ..ArchiveHandler import ArchiveHandler


class ZipArchiveHandler(ArchiveHandler):
    """Handler for ZIP-based archives (.zip, .whl, .docx, .xlsx, etc.)."""
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract ZIP archive to specified directory."""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            logger.info(f"Extracted ZIP archive {archive_path} to {extract_to}")
            return True
        except Exception as e:
            logger.error(f"Failed to extract ZIP archive {archive_path}: {e}")
            return False
    
    def pack(self, source_path: PathLike, archive_path: PathLike, 
             compression_level: int = 6) -> bool:
        """Create ZIP archive from source directory or files."""
        try:
            source = Path(source_path)
            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED, 
                               compresslevel=compression_level) as zip_ref:
                if source.is_dir():
                    for file_path in source.rglob('*'):
                        if file_path.is_file():
                            arcname = file_path.relative_to(source)
                            zip_ref.write(file_path, arcname)
                else:
                    zip_ref.write(source, source.name)
            logger.info(f"Created ZIP archive {archive_path} from {source_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create ZIP archive {archive_path}: {e}")
            return False
    
    def test(self, archive_path: PathLike) -> bool:
        """Test ZIP archive integrity."""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                bad_file = zip_ref.testzip()
                if bad_file:
                    logger.warning(f"ZIP archive {archive_path} has corrupted file: {bad_file}")
                    return False
            logger.debug(f"ZIP archive {archive_path} integrity test passed")
            return True
        except Exception as e:
            logger.error(f"ZIP archive {archive_path} integrity test failed: {e}")
            return False
    
    def list_files(self, archive_path: PathLike) -> List[str]:
        """List files in ZIP archive."""
        try:
            with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                return zip_ref.namelist()
        except Exception as e:
            logger.error(f"Failed to list files in ZIP archive {archive_path}: {e}")
            return []