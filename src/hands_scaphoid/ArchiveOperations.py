#!/usr/bin/env python3
"""
Archive operations module for hands-scaphoid package.

This module provides the Archive class for pure archive operations
without context management.

File:
    name: ArchiveOperations.py
    date: 2025-09-16

Description:
    Pure archive operations class - no context management

Authors: ["Andreas Häberle"]
"""

import zipfile
import tarfile
import shutil
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from .__base__ import PathLike, console


class Archive:
    """
    Pure archive operations class without context management.
    
    This class provides static methods for archive operations that can be used
    independently of any context manager. All methods operate on explicit
    archive paths and do not maintain any state.
    
    Supported formats: ZIP, TAR, TAR.GZ, TAR.BZ2
    
    Example:
        # Direct archive operations
        Archive.create_zip_archive(Path("backup.zip"), Path("source_dir"))
        Archive.add_file_to_zip(Path("backup.zip"), Path("new_file.txt"))
        files = Archive.list_archive_contents(Path("backup.zip"))
    """
    
    @staticmethod
    def detect_archive_type(archive_path: PathLike) -> str:
        """
        Detect the archive type from file extension.
        
        Args:
            archive_path: Path to the archive file
            
        Returns:
            Archive type ('zip', 'tar', 'tar.gz', 'tar.bz2')
            
        Raises:
            ValueError: If archive type cannot be determined
        """
        path = Path(archive_path)
        
        if path.suffix.lower() == '.zip':
            return 'zip'
        elif path.suffixes[-2:] == ['.tar', '.gz']:
            return 'tar.gz'
        elif path.suffixes[-2:] == ['.tar', '.bz2']:
            return 'tar.bz2'
        elif path.suffix.lower() == '.tar':
            return 'tar'
        else:
            raise ValueError(f"Unsupported archive type for file: {path}")
    
    @staticmethod
    def is_archive_file(file_path: PathLike) -> bool:
        """
        Check if a file is an archive based on its extension.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file appears to be an archive, False otherwise
        """
        try:
            Archive.detect_archive_type(file_path)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def create_zip_archive(archive_path: PathLike, source_path: Optional[PathLike] = None) -> None:
        """
        Create a new ZIP archive.
        
        Args:
            archive_path: Path for the new archive
            source_path: Optional source directory/file to add initially
            
        Raises:
            PermissionError: If lacking create permissions
        """
        path = Path(archive_path)
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            with zipfile.ZipFile(path, 'w', zipfile.ZIP_DEFLATED) as zf:
                if source_path:
                    source = Path(source_path)
                    if source.is_file():
                        zf.write(source, source.name)
                    elif source.is_dir():
                        for file_path in source.rglob('*'):
                            if file_path.is_file():
                                arcname = file_path.relative_to(source.parent)
                                zf.write(file_path, arcname)
            
            console.print(f"[green]Created ZIP archive:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied creating archive:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error creating ZIP archive {path}:[/red] {e}")
            raise
    
    @staticmethod
    def create_tar_archive(archive_path: PathLike, source_path: Optional[PathLike] = None, 
                          compression: Optional[str] = None) -> None:
        """
        Create a new TAR archive.
        
        Args:
            archive_path: Path for the new archive
            source_path: Optional source directory/file to add initially
            compression: Compression type ('gz', 'bz2', or None)
            
        Raises:
            PermissionError: If lacking create permissions
        """
        path = Path(archive_path)
        try:
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'w'
            if compression == 'gz':
                mode = 'w:gz'
            elif compression == 'bz2':
                mode = 'w:bz2'
            
            with tarfile.open(path, mode) as tf:
                if source_path:
                    source = Path(source_path)
                    if source.exists():
                        tf.add(source, arcname=source.name)
            
            console.print(f"[green]Created TAR archive:[/green] {path}")
        except PermissionError:
            console.print(f"[red]Permission denied creating archive:[/red] {path}")
            raise
        except Exception as e:
            console.print(f"[red]Error creating TAR archive {path}:[/red] {e}")
            raise
    
    @staticmethod
    def add_file_to_zip(archive_path: PathLike, file_path: PathLike, 
                       archive_name: Optional[str] = None) -> None:
        """
        Add a file to an existing ZIP archive.
        
        Args:
            archive_path: Path to the ZIP archive
            file_path: Path to the file to add
            archive_name: Name to use in archive (defaults to filename)
            
        Raises:
            FileNotFoundError: If archive or file doesn't exist
        """
        archive = Path(archive_path)
        file_to_add = Path(file_path)
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")
        if not file_to_add.exists():
            raise FileNotFoundError(f"File not found: {file_to_add}")
        
        try:
            arcname = archive_name or file_to_add.name
            
            with zipfile.ZipFile(archive, 'a', zipfile.ZIP_DEFLATED) as zf:
                zf.write(file_to_add, arcname)
            
            console.print(f"[green]Added file to ZIP archive:[/green] {arcname}")
        except Exception as e:
            console.print(f"[red]Error adding file to ZIP archive:[/red] {e}")
            raise
    
    @staticmethod
    def add_directory_to_zip(archive_path: PathLike, dir_path: PathLike, 
                            archive_name: Optional[str] = None) -> None:
        """
        Add a directory to an existing ZIP archive.
        
        Args:
            archive_path: Path to the ZIP archive
            dir_path: Path to the directory to add
            archive_name: Name to use in archive (defaults to directory name)
        """
        archive = Path(archive_path)
        directory = Path(dir_path)
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")
        if not directory.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")
        if not directory.is_dir():
            raise NotADirectoryError(f"Path is not a directory: {directory}")
        
        try:
            base_name = archive_name or directory.name
            
            with zipfile.ZipFile(archive, 'a', zipfile.ZIP_DEFLATED) as zf:
                for file_path in directory.rglob('*'):
                    if file_path.is_file():
                        relative_path = file_path.relative_to(directory)
                        arcname = f"{base_name}/{relative_path}"
                        zf.write(file_path, arcname)
            
            console.print(f"[green]Added directory to ZIP archive:[/green] {base_name}")
        except Exception as e:
            console.print(f"[red]Error adding directory to ZIP archive:[/red] {e}")
            raise
    
    @staticmethod
    def add_file_to_tar(archive_path: PathLike, file_path: PathLike, 
                       archive_name: Optional[str] = None) -> None:
        """
        Add a file to an existing TAR archive.
        
        Args:
            archive_path: Path to the TAR archive
            file_path: Path to the file to add
            archive_name: Name to use in archive (defaults to filename)
        """
        archive = Path(archive_path)
        file_to_add = Path(file_path)
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")
        if not file_to_add.exists():
            raise FileNotFoundError(f"File not found: {file_to_add}")
        
        try:
            # Determine TAR mode based on archive type
            archive_type = Archive.detect_archive_type(archive)
            if archive_type == 'tar.gz':
                mode = 'a:gz'
            elif archive_type == 'tar.bz2':
                mode = 'a:bz2'
            else:
                mode = 'a'
            
            arcname = archive_name or file_to_add.name
            
            with tarfile.open(archive, mode) as tf:
                tf.add(file_to_add, arcname=arcname)
            
            console.print(f"[green]Added file to TAR archive:[/green] {arcname}")
        except Exception as e:
            console.print(f"[red]Error adding file to TAR archive:[/red] {e}")
            raise
    
    @staticmethod
    def list_archive_contents(archive_path: PathLike) -> List[str]:
        """
        List contents of an archive.
        
        Args:
            archive_path: Path to the archive
            
        Returns:
            List of file paths in the archive
            
        Raises:
            FileNotFoundError: If archive doesn't exist
        """
        path = Path(archive_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archive not found: {path}")
        
        try:
            archive_type = Archive.detect_archive_type(path)
            
            if archive_type == 'zip':
                with zipfile.ZipFile(path, 'r') as zf:
                    contents = zf.namelist()
            else:
                # TAR archive
                with tarfile.open(path, 'r') as tf:
                    contents = tf.getnames()
            
            console.print(f"[blue]Listed {len(contents)} items in archive:[/blue] {path}")
            return contents
            
        except Exception as e:
            console.print(f"[red]Error listing archive contents {path}:[/red] {e}")
            raise
    
    @staticmethod
    def extract_archive(archive_path: PathLike, target_path: Optional[PathLike] = None) -> None:
        """
        Extract all contents from an archive.
        
        Args:
            archive_path: Path to the archive to extract
            target_path: Target directory for extraction (defaults to current directory)
            
        Raises:
            FileNotFoundError: If archive doesn't exist
        """
        archive = Path(archive_path)
        target = Path(target_path) if target_path else Path.cwd()
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")
        
        try:
            # Create target directory if it doesn't exist
            target.mkdir(parents=True, exist_ok=True)
            
            archive_type = Archive.detect_archive_type(archive)
            
            if archive_type == 'zip':
                with zipfile.ZipFile(archive, 'r') as zf:
                    zf.extractall(target)
            else:
                # TAR archive
                with tarfile.open(archive, 'r') as tf:
                    tf.extractall(target)
            
            console.print(f"[green]Extracted archive:[/green] {archive} → {target}")
            
        except Exception as e:
            console.print(f"[red]Error extracting archive {archive}:[/red] {e}")
            raise
    
    @staticmethod
    def extract_file_from_archive(archive_path: PathLike, file_name: str, 
                                 target_path: Optional[PathLike] = None) -> None:
        """
        Extract a specific file from an archive.
        
        Args:
            archive_path: Path to the archive
            file_name: Name of file to extract from archive
            target_path: Target directory for extraction (defaults to current directory)
            
        Raises:
            FileNotFoundError: If archive doesn't exist or file not in archive
        """
        archive = Path(archive_path)
        target = Path(target_path) if target_path else Path.cwd()
        
        if not archive.exists():
            raise FileNotFoundError(f"Archive not found: {archive}")
        
        try:
            # Create target directory if it doesn't exist
            target.mkdir(parents=True, exist_ok=True)
            
            archive_type = Archive.detect_archive_type(archive)
            
            if archive_type == 'zip':
                with zipfile.ZipFile(archive, 'r') as zf:
                    if file_name not in zf.namelist():
                        raise FileNotFoundError(f"File '{file_name}' not found in archive")
                    zf.extract(file_name, target)
            else:
                # TAR archive
                with tarfile.open(archive, 'r') as tf:
                    if file_name not in tf.getnames():
                        raise FileNotFoundError(f"File '{file_name}' not found in archive")
                    tf.extract(file_name, target)
            
            console.print(f"[green]Extracted file:[/green] {file_name} → {target}")
            
        except Exception as e:
            console.print(f"[red]Error extracting file from archive:[/red] {e}")
            raise
    
    @staticmethod
    def archive_info(archive_path: PathLike) -> Dict[str, Any]:
        """
        Get information about an archive.
        
        Args:
            archive_path: Path to the archive
            
        Returns:
            Dictionary with archive information
            
        Raises:
            FileNotFoundError: If archive doesn't exist
        """
        path = Path(archive_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Archive not found: {path}")
        
        try:
            archive_type = Archive.detect_archive_type(path)
            file_size = path.stat().st_size
            
            if archive_type == 'zip':
                with zipfile.ZipFile(path, 'r') as zf:
                    file_count = len(zf.namelist())
                    info = zf.infolist()
                    total_uncompressed = sum(f.file_size for f in info)
            else:
                # TAR archive
                with tarfile.open(path, 'r') as tf:
                    members = tf.getmembers()
                    file_count = len([m for m in members if m.isfile()])
                    total_uncompressed = sum(m.size for m in members if m.isfile())
            
            return {
                'type': archive_type,
                'file_count': file_count,
                'compressed_size': file_size,
                'uncompressed_size': total_uncompressed,
                'compression_ratio': (file_size / total_uncompressed) if total_uncompressed > 0 else 0
            }
            
        except Exception as e:
            console.print(f"[red]Error getting archive info {path}:[/red] {e}")
            raise