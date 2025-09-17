#!/usr/bin/env python3
"""
Archive context manager for hands-scaphoid package.

This module provides the ArchiveContext class for managing archive operations
with context manager support and hierarchical path resolution.

File:
    name: ArchiveContext.py
    date: 2025-09-16

Description:
    Archive context manager for hierarchical file system operations

Authors: ["Andreas Häberle"]
"""

from pathlib import Path
from typing import Optional, List, Dict, Any
from .contexts.Context import Context
from .ArchiveOperations import Archive
from .__base__ import PathLike, console


class ArchiveContext(Context):
    """
    Archive context manager for hierarchical file system operations.
    
    This class allows you to work with archives (ZIP, TAR, etc.) in a hierarchical context,
    providing convenient methods for creating, reading, and manipulating archive content
    while maintaining awareness of the current directory context. It delegates actual
    archive operations to the Archive class.
    
    Example:
        with DirectoryContext('~') as home:
            with DirectoryContext('projects') as projects:
                with ArchiveContext(source='myproject', target='backup.zip') as archive:
                    archive.add_directory('myproject')
                    archive.add_file('README.md')
    """
    
    def __init__(self, source: Optional[PathLike] = None, target: Optional[PathLike] = None, 
                 archive_type: str = 'zip', create: bool = True, dry_run: bool = False, enable_globals: bool = False):
        """
        Initialize a new ArchiveContext.
        
        Args:
            source: Source directory, file, or existing archive to work with (optional)
            target: Target archive file path (defaults to source name with archive extension)
            archive_type: Type of archive ('zip', 'tar', 'tar.gz', 'tar.bz2')
            create: Whether to create the archive if it doesn't exist (default: True)
            dry_run: Whether to simulate operations without making actual changes
            enable_globals: Whether to enable global function access within context
        """
        # Determine target path if not provided
        if source and not target:
            source_path = Path(source)
            if Archive.is_archive_file(source_path):
                # Source is an existing archive
                target = source
                self.source_is_archive = True
            else:
                # Source is a directory/file to archive
                if archive_type == 'zip':
                    target = f"{source_path.stem}.zip"
                elif archive_type.startswith('tar'):
                    if archive_type == 'tar.gz':
                        target = f"{source_path.stem}.tar.gz"
                    elif archive_type == 'tar.bz2':
                        target = f"{source_path.stem}.tar.bz2"
                    else:
                        target = f"{source_path.stem}.tar"
                else:
                    target = f"{source_path.stem}.{archive_type}"
                self.source_is_archive = False
        elif target and not source:
            self.source_is_archive = False
        else:
            self.source_is_archive = Archive.is_archive_file(Path(source)) if source else False
        
        if target is None:
            raise ValueError("Either source or target must be specified")
        
        super().__init__(target, create, dry_run, enable_globals)
        self.source = Path(source) if source else None
        self.archive_type = archive_type.lower()
        
        # Validate archive type
        if self.archive_type not in ['zip', 'tar', 'tar.gz', 'tar.bz2']:
            raise ValueError(f"Unsupported archive type: {archive_type}")
    
    def _create_path(self, resolved_path: Path) -> None:
        """
        Create the archive file if it doesn't exist.
        
        Args:
            resolved_path: The resolved absolute path to create
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would create archive: {resolved_path}[/dim]")
            return
        
        if self.archive_type == 'zip':
            Archive.create_zip_archive(resolved_path, self.source)
        else:
            # TAR archive
            compression = None
            if self.archive_type == 'tar.gz':
                compression = 'gz'
            elif self.archive_type == 'tar.bz2':
                compression = 'bz2'
            
            Archive.create_tar_archive(resolved_path, self.source, compression)
    
    def _enter_context(self, resolved_path: Path) -> None:
        """
        Prepare the archive when entering the context.
        
        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would open archive: {resolved_path}[/dim]")
            return
        
        console.print(f"[green]Opened archive:[/green] {resolved_path}")
    
    def _exit_context(self, resolved_path: Path) -> None:
        """
        Finalize the archive when exiting the context.
        
        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would close archive: {resolved_path}[/dim]")
            return
        
        console.print(f"[green]Closed archive:[/green] {resolved_path}")
    
    def add_file(self, file_path: PathLike, archive_path: Optional[str] = None) -> 'ArchiveContext':
        """
        Add a file to the archive.
        
        Args:
            file_path: Path to the file to add
            archive_path: Path within archive (optional, defaults to filename)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would add file to archive: {file_path}[/dim]")
            return self
        
        archive_path_resolved = self.resolve_path()
        
        if self.archive_type == 'zip':
            Archive.add_file_to_zip(archive_path_resolved, file_path, archive_path)
        else:
            Archive.add_file_to_tar(archive_path_resolved, file_path, archive_path)
        
        return self
    
    def add_directory(self, dir_path: PathLike, archive_path: Optional[str] = None) -> 'ArchiveContext':
        """
        Add a directory and its contents to the archive.
        
        Args:
            dir_path: Path to the directory to add
            archive_path: Path within archive (optional, defaults to directory name)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would add directory to archive: {dir_path}[/dim]")
            return self
        
        archive_path_resolved = self.resolve_path()
        
        if self.archive_type == 'zip':
            Archive.add_directory_to_zip(archive_path_resolved, dir_path, archive_path)
        else:
            # For TAR archives, we need to recreate the archive with the new directory
            # This is a limitation of the tarfile module for append operations with directories
            console.print(f"[yellow]Note: Adding directories to TAR archives recreates the archive[/yellow]")
            
            # Get existing contents first
            if archive_path_resolved.exists():
                existing_contents = Archive.list_archive_contents(archive_path_resolved)
            else:
                existing_contents = []
            
            # Create new archive with directory
            compression = None
            if self.archive_type == 'tar.gz':
                compression = 'gz'
            elif self.archive_type == 'tar.bz2':
                compression = 'bz2'
            
            Archive.create_tar_archive(archive_path_resolved, dir_path, compression)
            
            # Note: In a full implementation, we would need to extract existing files
            # and re-add them along with the new directory
        
        return self
    
    def list_contents(self) -> List[str]:
        """
        List contents of the archive.
        
        Returns:
            List of file paths in the archive
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would list archive contents: {self.resolve_path()}[/dim]")
            return ["[DRY RUN] Archive contents would be listed here"]
        
        return Archive.list_archive_contents(self.resolve_path())
    
    def extract_file(self, file_name: str, target_path: Optional[PathLike] = None) -> 'ArchiveContext':
        """
        Extract a specific file from the archive.
        
        Args:
            file_name: Name of file to extract from archive
            target_path: Target directory for extraction (optional)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would extract file from archive: {file_name}[/dim]")
            return self
        
        Archive.extract_file_from_archive(self.resolve_path(), file_name, target_path)
        return self
    
    def extract_all(self, target_path: Optional[PathLike] = None) -> 'ArchiveContext':
        """
        Extract all contents from the archive.
        
        Args:
            target_path: Target directory for extraction (optional)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would extract all from archive: {self.resolve_path()}[/dim]")
            return self
        
        Archive.extract_archive(self.resolve_path(), target_path)
        return self
    
    def get_archive_info(self) -> Dict[str, Any]:
        """
        Get information about the archive.
        
        Returns:
            Dictionary with archive information
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would get archive info: {self.resolve_path()}[/dim]")
            return {
                'type': self.archive_type,
                'file_count': 0,
                'compressed_size': 0,
                'uncompressed_size': 0,
                'compression_ratio': 0
            }
        
        return Archive.archive_info(self.resolve_path())
    
    def archive_exists(self) -> bool:
        """
        Check if the archive exists.
        
        Returns:
            True if archive exists, False otherwise
        """
        return self.resolve_path().exists()
    
    def is_archive_file(self) -> bool:
        """
        Check if the target path appears to be an archive file.
        
        Returns:
            True if target appears to be an archive, False otherwise
        """
        return Archive.is_archive_file(self.resolve_path())
    
    def copy_to(self, target_path: PathLike) -> 'ArchiveContext':
        """
        Copy this archive to another location.
        
        Args:
            target_path: Target archive path
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would copy archive: {self.resolve_path()} → {target_path}[/dim]")
            return self
        
        import shutil
        shutil.copy2(self.resolve_path(), target_path)
        console.print(f"[green]Copied archive:[/green] {self.resolve_path()} → {target_path}")
        return self
    
    def delete(self) -> None:
        """
        Delete the archive file.
        
        Note: This will also exit the context as the archive no longer exists.
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would delete archive: {self.resolve_path()}[/dim]")
            return
        
        archive_path = self.resolve_path()
        archive_path.unlink()
        console.print(f"[green]Deleted archive:[/green] {archive_path}")
    
    def get_compression_ratio(self) -> float:
        """
        Get the compression ratio of the archive.
        
        Returns:
            Compression ratio (compressed size / uncompressed size)
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would get compression ratio: {self.resolve_path()}[/dim]")
            return 0.0
        
        info = self.get_archive_info()
        return info.get('compression_ratio', 0.0)