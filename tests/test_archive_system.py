#!/usr/bin/env python3
"""
Unit tests for the DynamicArchiveType and ArchiveHandler system.
---yaml
File:
    name: test_archive_system.py
    uuid: 3e4f5a6b-7c8d-9e0f-1234-567890abcdef
    date: 2025-09-28

Description:
    Comprehensive tests for the new archive system including DynamicArchiveType,
    ArchiveHandler patterns, and centralized registry functionality.

Project:
    name: hands_scaphoid
    uuid: 2945ba3b-2d66-4dff-b898-672c386f03f4
    url: https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

# Standard library imports
import tempfile
import zipfile
import tarfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Third-party imports
import pytest

from hands_scaphoid.commands.core_commands import DynamicArchiveType, ArchiveHandler
from hands_scaphoid.commands.archive_handlers import (
    ZipArchiveHandler,
    TarArchiveHandler,
    AppBundleHandler,
    WheelArchiveHandler,
    OfficeDocumentHandler
)
from hands_scaphoid.commands.archive_registry import (
    ArchiveRegistry,
    get_archive_registry,
    get_archive_handler,
    register_archive_type,
    is_archive_supported
)


class TestDynamicArchiveType:
    """Test the DynamicArchiveType registry system."""
    
    def test_create_empty_registry(self):
        """Test creating an empty archive type registry."""
        archive_type = DynamicArchiveType()
        assert archive_type._next_id == 1
        assert len(archive_type._members) == 0
        assert len(archive_type._extensions) == 0
        assert len(archive_type._handler) == 0
    
    def test_add_archive_type(self):
        """Test adding a new archive type."""
        archive_type = DynamicArchiveType()
        handler = Mock(spec=ArchiveHandler)
        
        result = archive_type.add('zip', '.zip', handler)
        
        assert result is True
        assert 'zip' in archive_type._members
        assert archive_type._extensions['zip'] == '.zip'
        assert archive_type._handler['zip'] is handler
    
    def test_add_duplicate_archive_type(self):
        """Test that adding duplicate archive type raises error."""
        archive_type = DynamicArchiveType()
        handler = Mock(spec=ArchiveHandler)
        
        archive_type.add('zip', '.zip', handler)
        
        with pytest.raises(ValueError, match='zip is already defined'):
            archive_type.add('zip', '.zip', handler)
    
    def test_add_similar_archive_type(self):
        """Test adding an archive type similar to existing one."""
        archive_type = DynamicArchiveType()
        zip_handler = Mock(spec=ArchiveHandler)
        
        archive_type.add('zip', '.zip', zip_handler)
        result = archive_type.add_similar('jar', '.jar', 'zip')
        
        assert result is True
        assert 'jar' in archive_type._members
        assert archive_type._extensions['jar'] == '.jar'
        assert archive_type._handler['jar'] is zip_handler  # Same handler
    
    def test_add_similar_nonexistent_type(self):
        """Test adding similar to non-existent type raises error."""
        archive_type = DynamicArchiveType()
        
        with pytest.raises(ValueError, match='nonexistent is not defined'):
            archive_type.add_similar('jar', '.jar', 'nonexistent')
    
    def test_get_handler(self):
        """Test getting handler for archive type."""
        archive_type = DynamicArchiveType()
        handler = Mock(spec=ArchiveHandler)
        
        archive_type.add('zip', '.zip', handler)
        
        retrieved_handler = archive_type.get_handler('zip')
        assert retrieved_handler is handler
    
    def test_get_nonexistent_handler(self):
        """Test getting handler for non-existent type raises error."""
        archive_type = DynamicArchiveType()
        
        with pytest.raises(ValueError, match='nonexistent.*not.*defined'):
            archive_type.get_handler('nonexistent')
    
    def test_list_types(self):
        """Test listing all registered archive types."""
        archive_type = DynamicArchiveType()
        
        archive_type.add('zip', '.zip', None)
        archive_type.add('tar', '.tar', None)
        
        types = archive_type.list_types()
        assert 'zip' in types
        assert 'tar' in types
        assert len(types) == 2
    
    def test_list_extensions(self):
        """Test listing all registered extensions."""
        archive_type = DynamicArchiveType()
        
        archive_type.add('zip', '.zip', None)
        archive_type.add('tar', '.tar', None)
        
        extensions = archive_type.list_extensions()
        assert '.zip' in extensions
        assert '.tar' in extensions
        assert len(extensions) == 2


class TestZipArchiveHandler:
    """Test ZIP archive handler functionality."""
    
    def test_create_and_extract_zip(self, temp_dir):
        """Test creating and extracting ZIP archives."""
        handler = ZipArchiveHandler()
        
        # Create test files
        source_dir = temp_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'test1.txt').write_text('Hello World 1')
        (source_dir / 'test2.txt').write_text('Hello World 2')
        
        # Create ZIP archive
        archive_path = temp_dir / 'test.zip'
        result = handler.pack(source_dir, archive_path)
        assert result is True
        assert archive_path.exists()
        
        # Extract ZIP archive
        extract_dir = temp_dir / 'extracted'
        extract_dir.mkdir()
        result = handler.extract(archive_path, extract_dir)
        assert result is True
        
        # Verify extracted files
        extracted_source = extract_dir / 'source'
        assert extracted_source.exists()
        assert (extracted_source / 'test1.txt').read_text() == 'Hello World 1'
        assert (extracted_source / 'test2.txt').read_text() == 'Hello World 2'
    
    def test_test_zip_integrity(self, temp_dir):
        """Test ZIP integrity checking."""
        handler = ZipArchiveHandler()
        
        # Create valid ZIP
        archive_path = temp_dir / 'test.zip'
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr('test.txt', 'Hello World')
        
        # Test valid ZIP
        result = handler.test(archive_path)
        assert result is True
    
    def test_list_zip_files(self, temp_dir):
        """Test listing files in ZIP archive."""
        handler = ZipArchiveHandler()
        
        # Create ZIP with specific files
        archive_path = temp_dir / 'test.zip'
        with zipfile.ZipFile(archive_path, 'w') as zf:
            zf.writestr('file1.txt', 'Content 1')
            zf.writestr('dir/file2.txt', 'Content 2')
        
        # List files
        files = handler.list_files(archive_path)
        assert 'file1.txt' in files
        assert 'dir/file2.txt' in files
        assert len(files) == 2


class TestTarArchiveHandler:
    """Test TAR archive handler functionality."""
    
    def test_create_and_extract_tar(self, temp_dir):
        """Test creating and extracting TAR archives."""
        handler = TarArchiveHandler()
        
        # Create test files
        source_dir = temp_dir / 'source'
        source_dir.mkdir()
        (source_dir / 'test1.txt').write_text('Hello World 1')
        (source_dir / 'test2.txt').write_text('Hello World 2')
        
        # Create TAR archive
        archive_path = temp_dir / 'test.tar'
        result = handler.pack(source_dir, archive_path)
        assert result is True
        assert archive_path.exists()
        
        # Extract TAR archive
        extract_dir = temp_dir / 'extracted'
        extract_dir.mkdir()
        result = handler.extract(archive_path, extract_dir)
        assert result is True
        
        # Verify extracted files
        extracted_source = extract_dir / 'source'
        assert extracted_source.exists()
        assert (extracted_source / 'test1.txt').read_text() == 'Hello World 1'
        assert (extracted_source / 'test2.txt').read_text() == 'Hello World 2'
    
    def test_compressed_tar_handler(self, temp_dir):
        """Test TAR handler with compression."""
        handler = TarArchiveHandler('gz')
        
        # Create test file
        source_file = temp_dir / 'test.txt'
        source_file.write_text('Hello World')
        
        # Create compressed TAR
        archive_path = temp_dir / 'test.tar.gz'
        result = handler.pack(source_file, archive_path)
        assert result is True
        
        # Verify it's a valid tar.gz
        with tarfile.open(archive_path, 'r:gz') as tf:
            names = tf.getnames()
            assert 'test.txt' in names


class TestAppBundleHandler:
    """Test macOS app bundle handler."""
    
    def test_validate_valid_app_structure(self, temp_dir):
        """Test validation of valid app bundle structure."""
        handler = AppBundleHandler()
        
        # Create valid app bundle structure as ZIP
        app_path = temp_dir / 'Test.app.zip'
        with zipfile.ZipFile(app_path, 'w') as zf:
            zf.writestr('Contents/Info.plist', '<?xml version="1.0"?><plist></plist>')
            zf.writestr('Contents/MacOS/TestApp', 'binary_content')
            zf.writestr('Contents/Resources/icon.icns', 'icon_data')
        
        # Test validation
        result = handler.validate_app_structure(app_path)
        assert result is True
    
    def test_validate_invalid_app_structure(self, temp_dir):
        """Test validation of invalid app bundle structure."""
        handler = AppBundleHandler()
        
        # Create invalid app bundle (missing required files)
        app_path = temp_dir / 'Invalid.app.zip'
        with zipfile.ZipFile(app_path, 'w') as zf:
            zf.writestr('SomeFile.txt', 'content')
        
        # Test validation
        result = handler.validate_app_structure(app_path)
        assert result is False


class TestWheelArchiveHandler:
    """Test Python wheel archive handler."""
    
    def test_validate_valid_wheel_structure(self, temp_dir):
        """Test validation of valid wheel structure."""
        handler = WheelArchiveHandler()
        
        # Create valid wheel structure
        wheel_path = temp_dir / 'test-1.0-py3-none-any.whl'
        with zipfile.ZipFile(wheel_path, 'w') as zf:
            zf.writestr('test/__init__.py', '')
            zf.writestr('test-1.0.dist-info/METADATA', 'Name: test\nVersion: 1.0')
            zf.writestr('test-1.0.dist-info/WHEEL', 'Wheel-Version: 1.0')
        
        # Test validation
        result = handler.validate_wheel_structure(wheel_path)
        assert result is True
    
    def test_validate_invalid_wheel_structure(self, temp_dir):
        """Test validation of invalid wheel structure."""
        handler = WheelArchiveHandler()
        
        # Create invalid wheel (missing metadata)
        wheel_path = temp_dir / 'invalid-1.0-py3-none-any.whl'
        with zipfile.ZipFile(wheel_path, 'w') as zf:
            zf.writestr('invalid/__init__.py', '')
        
        # Test validation
        result = handler.validate_wheel_structure(wheel_path)
        assert result is False


class TestOfficeDocumentHandler:
    """Test Office document handler."""
    
    def test_validate_valid_docx_structure(self, temp_dir):
        """Test validation of valid DOCX structure."""
        handler = OfficeDocumentHandler('docx')
        
        # Create valid DOCX structure
        docx_path = temp_dir / 'test.docx'
        with zipfile.ZipFile(docx_path, 'w') as zf:
            zf.writestr('[Content_Types].xml', '<?xml version="1.0"?>')
            zf.writestr('_rels/.rels', '<?xml version="1.0"?>')
            zf.writestr('word/document.xml', '<?xml version="1.0"?>')
        
        # Test validation
        result = handler.validate_office_structure(docx_path)
        assert result is True
    
    def test_validate_invalid_docx_structure(self, temp_dir):
        """Test validation of invalid DOCX structure."""
        handler = OfficeDocumentHandler('docx')
        
        # Create invalid DOCX (missing required files)
        docx_path = temp_dir / 'invalid.docx'
        with zipfile.ZipFile(docx_path, 'w') as zf:
            zf.writestr('some_file.txt', 'content')
        
        # Test validation
        result = handler.validate_office_structure(docx_path)
        assert result is False


class TestArchiveRegistry:
    """Test the centralized archive registry."""
    
    def test_create_empty_registry(self):
        """Test creating empty registry."""
        registry = ArchiveRegistry()
        assert not registry._initialized
        assert len(registry.archive_type.list_types()) == 0
    
    def test_initialize_default_types(self):
        """Test initializing registry with default types."""
        registry = ArchiveRegistry()
        registry.initialize_default_types()
        
        assert registry._initialized
        types = registry.archive_type.list_types()
        assert 'zip' in types
        assert 'tar' in types
        assert 'whl' in types
        assert 'docx' in types
        assert len(types) > 5
    
    def test_register_new_archive_type(self):
        """Test registering new archive type."""
        registry = ArchiveRegistry()
        handler = Mock(spec=ArchiveHandler)
        
        result = registry.register_archive_type('custom', '.custom', handler)
        assert result is True
        assert 'custom' in registry.archive_type.list_types()
    
    def test_get_handler_for_file(self):
        """Test getting handler based on file extension."""
        registry = ArchiveRegistry()
        registry.initialize_default_types()
        
        # Test with known extension
        handler = registry.get_handler_for_file('test.zip')
        assert handler is not None
        assert isinstance(handler, ZipArchiveHandler)
        
        # Test with unknown extension
        handler = registry.get_handler_for_file('test.unknown')
        assert handler is None
    
    def test_list_supported_unsupported_types(self):
        """Test listing supported and unsupported types."""
        registry = ArchiveRegistry()
        registry.initialize_default_types()
        
        supported = registry.list_supported_types()
        unsupported = registry.list_unsupported_types()
        
        assert 'zip' in supported
        assert 'rar' in unsupported  # RAR has no handler
        assert len(supported) + len(unsupported) == len(registry.archive_type.list_types())
    
    def test_get_registry_info(self):
        """Test getting comprehensive registry information."""
        registry = ArchiveRegistry()
        registry.initialize_default_types()
        
        info = registry.get_info()
        
        assert 'total_types' in info
        assert 'supported_types' in info
        assert 'unsupported_types' in info
        assert 'all_types' in info
        assert 'supported' in info
        assert 'unsupported' in info
        assert 'extensions' in info
        
        assert info['total_types'] > 0
        assert info['supported_types'] > 0


class TestArchiveRegistryConvenienceFunctions:
    """Test convenience functions for archive registry."""
    
    def test_get_archive_handler(self):
        """Test getting archive handler via convenience function."""
        handler = get_archive_handler('zip')
        assert handler is not None
        assert isinstance(handler, ZipArchiveHandler)
    
    def test_register_archive_type_convenience(self):
        """Test registering archive type via convenience function."""
        handler = Mock(spec=ArchiveHandler)
        result = register_archive_type('test_custom', '.test', handler)
        assert result is True
        
        # Verify it was registered
        registered_handler = get_archive_handler('test_custom')
        assert registered_handler is handler
    
    def test_is_archive_supported_convenience(self):
        """Test checking archive support via convenience function."""
        assert is_archive_supported('zip') is True
        assert is_archive_supported('rar') is False  # No handler
        assert is_archive_supported('nonexistent') is False


# Fixtures for tests
@pytest.fixture
def temp_dir():
    """Create temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_archive_handler():
    """Create mock archive handler."""
    handler = Mock(spec=ArchiveHandler)
    handler.extract.return_value = True
    handler.pack.return_value = True
    handler.test.return_value = True
    handler.list_files.return_value = ['file1.txt', 'file2.txt']
    return handler