"""
OfficeDocumentHandler class module.
---yaml
File:
    name:   OfficeDocumentHandler.py
    uuid:   a1b7c3d9-0e5f-6g2h-ab3c-5a6b7c8d9e0f
    date:   2025-09-30

Description:
    Handler for Office documents (.docx, .xlsx, .pptx) with structure validation

Project:
    name:   hands_scraphoid
    uuid:   2945ba3b-2d66-4dff-b898-672c386f03f4
    url:    https://github.com/42sol-eu/hands_scraphoid

Authors:    ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# [Standard library imports]
from typing import List

# [Project base imports]
from ....__base__ import logger, PathLike

# [Local imports]
from ..archives.ZipArchiveHandler import ZipArchiveHandler


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