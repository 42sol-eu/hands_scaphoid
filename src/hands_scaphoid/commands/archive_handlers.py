#!/usr/bin/env python3
"""
Archive handlers for different archive types.

This module provides concrete implementations of ArchiveHandler for various
archive formats, including standard archives and special formats like app bundles.
---yaml
File:
    name: archive_handlers.py
    date: 2025-09-28

Description:
    Concrete ArchiveHandler implementations for extensible archive system

Project:
    name:        a7d
    uuid:        2cc2a024-ae2a-4d2c-91c2-f41348980f7f
    url:         https://github.com/42sol-eu/a7d

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Standard library imports]
import shutil
import subprocess
import tarfile
import zipfile
from pathlib import Path

# [Local imports]
from ..__base__ import (
    Any,
    console,
    Dict,
    List,
    logger,
    Optional,
    PathLike,
)
from .handlers.ArchiveHandler import ArchiveHandler

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


class OfficeDocumentHandler(ZipArchiveHandler):
    """Handler for Office documents (.docx, .xlsx, .pptx) with structure validation."""
    
    def __init__(self, document_type: str):
        """Initialize with document type (docx, xlsx, pptx)."""
        super().__init__()
        self.document_type = document_type
        self.required_files = self._get_required_files()
    
    def _get_required_files(self) -> List[str]:
        """Get required files for different Office document types."""
        base_files = ['[Content_Types].xml', '_rels/.rels']
        
        type_specific = {
            'docx': ['word/document.xml'],
            'xlsx': ['xl/workbook.xml'],
            'pptx': ['ppt/presentation.xml']
        }
        
        return base_files + type_specific.get(self.document_type, [])
    
    def validate_office_structure(self, archive_path: PathLike) -> bool:
        """Validate Office document structure."""
        files = self.list_files(archive_path)
        
        for required in self.required_files:
            if required not in files:
                logger.warning(f"Office document {archive_path} missing: {required}")
                return False
        
        logger.debug(f"Office document {archive_path} structure validation passed")
        return True
    
    def extract(self, archive_path: PathLike, extract_to: PathLike) -> bool:
        """Extract Office document with structure validation."""
        if not self.validate_office_structure(archive_path):
            logger.error(f"Office document {archive_path} has invalid structure")
            return False
        
        return super().extract(archive_path, extract_to)


# Factory function to create appropriate handlers
def create_archive_handler(archive_type: str) -> ArchiveHandler:
    """Create appropriate archive handler for given type."""
    handlers = {
        'zip': ZipArchiveHandler(),
        'whl': WheelArchiveHandler(),
        'docx': OfficeDocumentHandler('docx'),
        'xlsx': OfficeDocumentHandler('xlsx'), 
        'pptx': OfficeDocumentHandler('pptx'),
        'app': AppBundleHandler(),
        'tar': TarArchiveHandler(),
        'tar.gz': TarArchiveHandler('gz'),
        'tar.bz2': TarArchiveHandler('bz2'),
        'tar.xz': TarArchiveHandler('xz'),
        '7z': SevenZipArchiveHandler(),
    }
    
    handler = handlers.get(archive_type)
    if not handler:
        logger.warning(f"No handler found for archive type: {archive_type}")
        return ZipArchiveHandler()  # Default fallback
    
    return handler