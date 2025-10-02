"""
TarArchiveHandler class module.
---yaml
File:
    name:   TarArchiveHandler.py
    uuid:   w7x3y9z5-6a1b-2c8d-uv9w-1w2x3y4z5a6b
    date:   2025-09-30

Description:
    Handler for TAR-based archives (.tar, .tar.gz, .tar.bz2, .tar.xz)

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

#%% [Standard library imports]
import tarfile
from pathlib import Path
from typing import List

#%% [Project base imports]
from ....__base__ import logger, PathLike

#%% [Local imports]
from ..ArchiveHandler import ArchiveHandler


class TarArchiveHandler(ArchiveHandler):
    """Handler for TAR-based archives (.tar, .tar.gz, .tar.bz2, .tar.xz)."""
    
    def __init__(self, compression_mode: str = ""):
        """Initialize with compression mode (e.g., 'gz', 'bz2', 'xz')."""
        self.compression_mode = compression_mode
        self.mode_suffix = f":{compression_mode}" if compression_mode else ""
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract TAR archive to specified directory."""
        try:
            with tarfile.open(archive_path, f'r{self.mode_suffix}') as tar_ref:
                tar_ref.extractall(extract_to)
            logger.info(f"Extracted TAR archive {archive_path} to {extract_to}")
            return True
        except Exception as e:
            logger.error(f"Failed to extract TAR archive {archive_path}: {e}")
            return False
    
    def pack(self, source_path: PathLike, archive_path: PathLike, **kwargs) -> bool:
        """Create TAR archive from source directory or files."""
        try:
            source = Path(source_path)
            with tarfile.open(archive_path, f'w{self.mode_suffix}') as tar_ref:
                if source.is_dir():
                    tar_ref.add(source, arcname=source.name)
                else:
                    tar_ref.add(source, arcname=source.name)
            logger.info(f"Created TAR archive {archive_path} from {source_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create TAR archive {archive_path}: {e}")
            return False
    
    def test(self, archive_path: PathLike) -> bool:
        """Test TAR archive integrity."""
        try:
            with tarfile.open(archive_path, f'r{self.mode_suffix}') as tar_ref:
                # Try to read all members
                for member in tar_ref.getmembers():
                    if member.isfile():
                        tar_ref.extractfile(member)
            logger.debug(f"TAR archive {archive_path} integrity test passed")
            return True
        except Exception as e:
            logger.error(f"TAR archive {archive_path} integrity test failed: {e}")
            return False
    
    def list_files(self, archive_path: PathLike) -> List[str]:
        """List files in TAR archive."""
        try:
            with tarfile.open(archive_path, f'r{self.mode_suffix}') as tar_ref:
                return tar_ref.getnames()
        except Exception as e:
            logger.error(f"Failed to list files in TAR archive {archive_path}: {e}")
            return []