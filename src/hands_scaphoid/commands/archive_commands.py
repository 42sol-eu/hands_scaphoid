"""
Generic archive commands.
----
file:
    name:        archive_commands.py  
    uuid:        5bcba9a5-9afb-44a1-b711-3f971fb419fc
description:     archive commands
authors:         felix@42sol.eu
project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid
"""

from ..__base__ import logger, PathLike, Path
from typing import List, Optional, Any
from .core_commands import (
    CompressionType, 
    exists,
    ensure_path,
    does_not_exists,
    get_file_extension, 
    is_directory,
    is_file,
    is_instance,
    which,
)
from .directory_commands import CompressionType, list_contents

import rarfile  # Requires 'rarfile' package
import tarfile
import py7zr    # Requires 'py7zr' package
import zipfile
import os
import subprocess

logger.debug("Importing archive_commands module")
# used in hands_scaphoid.objects.ArchiveFile

def is_archive_file(file_path: PathLike) -> bool:
    """
    Check if a file is an archive based on its extension.

    Args:
        file_path: Path to check

    Returns:
        True if file appears to be an archive, False otherwise
    """
    archive_types = CompressionType.list_types()
    file_extension = get_file_extension(file_path).lower()
    return file_extension in archive_types

def core_preconditions(target: PathLike, source: PathLike) -> bool:
    """
    Perform core checks before creating an archive.

    Args:
        target: Path to the target archive file
        source: Path to the source directory to archive

    Returns:
        True if all checks pass, False otherwise
    """
    if exists(target):
        logger.error(f"[red]Archive already exists:[/red] {target}")
        return False

    if not exists(source) or not is_directory(source):
        logger.error(
            f"[red]Source directory does not exist or is not a directory:[/red] {source}"
        )
        return False

    return True

def create_7z_archive(archive_name: PathLike, source: PathLike) -> bool:
    """
    Create a 7z archive from the specified source directory.

    Args:
        archive_name: Name of the output archive file (without extension)
        source: Path to the source directory to archive
    Returns:
        bool: True if the archive was created, False otherwise
    """
    ext = get_file_extension(archive_name)
    if ext.lower() != ".7z":
        archive_name += ".7z"
    archive_path = Path(archive_name)
    
    if not core_preconditions(archive_path, source):
        return False

    try:
        with py7zr.SevenZipFile(archive_path, 'w') as archive:
            # Add all files and subdirectories from source
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = Path(root) / file
                    archive.write(file_path, arcname=file_path.relative_to(source))
        logger.info(f"[green]Created archive:[/green] {archive_path}")
        return True
    except Exception as e:
        logger.error(f"[red]Error creating archive {archive_path}:[/red] {e}")
    
    return False

def create_rar_archive(archive_name: PathLike, source: PathLike) -> bool:
    """
    Create a RAR archive from the specified source directory.

    Args:
        archive_name: Name of the output archive file (without extension)
        source: Path to the source directory to archive
    Returns:
        bool: True if the archive was created, False otherwise
    """
    ext = get_file_extension(archive_name)
    if ext.lower() != ".rar":
        archive_name += ".rar"
    archive_path = Path(archive_name)
    
    if core_preconditions(archive_path, source) is False:
        return False
    
    try:
        # rarfile does not support writing archives directly.
        # Use external 'rar' command if available.
        if not which("rar"):
            logger.error("[red]'rar' executable not found. Please install WinRAR or ensure 'rar' is in your PATH.[/red]")
            return False
        
        cmd = ["rar", "a", str(archive_path), str(source)]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            logger.info(f"[green]Created archive:[/green] {archive_path}")
            return True
        else:
            logger.error(f"[red]Error creating archive {archive_path}:[/red] {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"[red]Error creating archive {archive_path}:[/red] {e}")
        
    return False

def create_tar_archive(archive_name: PathLike, source: PathLike, compression: Optional[str] = None) -> bool:
    """
    Create a tar archive from the specified source directory.

    Args:
        archive_name: Name of the output archive file (without extension)
        source: Path to the source directory to archive
        compression: Compression type ('gz', 'bz2', 'xz', or None)
    Returns:
        bool: True if the archive was created, False otherwise
    """
    ext = get_file_extension(archive_name)
    if ".tar" not in ext.lower():
        archive_name += ".tar"
    if compression not in ext.lower():
        if compression:
            archive_name += f".{compression}"
    archive_path = Path(archive_name)
    
    if core_preconditions(archive_path, source) is False:
        return False
    
    if compression not in (None, 'gz', 'bz2', 'xz'):
        logger.error(f"[red]Unsupported compression type:[/red] {compression}")
        return False

    ext = f".tar.{compression}" if compression else ".tar"
    archive_path = Path(f"{archive_name}{ext}")

    if not source.exists() or not source.is_dir():
        logger.error(
            f"[red]Source directory does not exist or is not a directory:[/red] {source}"
        )
        return False

    try:
        mode = f"w:{compression}" if compression else "w"
        with tarfile.open(archive_path, mode) as tar_file:
            tar_file.add(source, arcname=Path(source).name)
        logger.info(f"[green]Created archive:[/green] {archive_path}")
        return True
    except Exception as e:
        logger.error(f"[red]Error creating archive {archive_path}:[/red] {e}")
        return False
    


def create_zip_archive(archive_name: str, source: PathLike) -> bool:
    """
    Create a zip archive from the specified source directory.

    Args:
        archive_name: Name of the output archive file (without extension)
        source: Path to the source directory to archive

    Returns:
        bool: True if the archive was created, False otherwise
    """

    ext = get_file_extension(archive_name)
    if ext.lower() != ".zip":
        archive_name += ".zip"
    archive_path = Path(archive_name)
    
    if core_preconditions(archive_path, source) is False:
        return False

    if not source.exists() or not source.is_dir():
        logger.error(
            f"[red]Source directory does not exist or is not a directory:[/red] {source}"
        )
        return False

    try:
        with zipfile.ZipFile(archive_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = Path(root) / file
                    zip_file.write(file_path, file_path.relative_to(source))
        logger.info(f"[green]Created archive:[/green] {archive_path}")
        return True 

    except Exception as e:
        logger.error(f"[red]Error creating archive {archive_path}:[/red] {e}")

    return False


def core_extract_conditions(archive_path: PathLike, target_dir: PathLike) -> bool:
    """
    Perform core checks before extracting an archive.

    Args:
        archive_path: Path to the archive file
        target_dir: Path to the target directory where files will be extracted

    Returns:
        True if all checks pass, False otherwise
    """
    if does_not_exists(archive_path) or not is_file(archive_path):
        logger.error(f"[red]Archive does not exist or is not a file:[/red] {archive_path}")
        return False

    if exists(target_dir):
        logger.error(f"[red]Target directory already exists:[/red] {target_dir}")
        return False

    return True

def extract_7z_archive(archive_path: PathLike, target_dir: PathLike) -> bool:
    """
    Extract a 7z archive to the specified target directory.

    Args:
        archive_path: Path to the 7z archive file
        target_dir: Path to the target directory where files will be extracted

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    if not core_extract_conditions(archive_path, target_dir):
        return False

    try:
        with py7zr.SevenZipFile(archive_path, "r") as archive:
            archive.extractall(path=target_dir)
        logger.info(f"[green]Extracted 7z archive to:[/green] {target_dir}")
        return True

    except Exception as e:
        logger.error(f"[red]Error extracting 7z archive {archive_path}:[/red] {e}")

    return False

def extract_rar_archive(archive_path: PathLike, target_dir: PathLike) -> bool:
    """
    Extract a RAR archive to the specified target directory.

    Args:
        archive_path: Path to the RAR archive file
        target_dir: Path to the target directory where files will be extracted

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    if not core_extract_conditions(archive_path, target_dir):
        return False

    try:
        with rarfile.RarFile(archive_path, "r") as archive:
            archive.extractall(path=target_dir)
        logger.info(f"[green]Extracted RAR archive to:[/green] {target_dir}")
        return True

    except Exception as e:
        logger.error(f"[red]Error extracting RAR archive {archive_path}:[/red] {e}")

    return False


def extract_tar_archive(archive_path: PathLike, target_dir: PathLike, compression: Optional[str] = None) -> bool:
    """
    Extract a tar archive to the specified target directory.

    Args:
        archive_path: Path to the tar archive file
        target_dir: Path to the target directory where files will be extracted
        compression: Compression type ('gz', 'bz2', 'xz', or None)

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    if not core_extract_conditions(archive_path, target_dir):
        return False

    if compression not in (None, 'gz', 'bz2', 'xz'):
        logger.error(f"[red]Unsupported compression type:[/red] {compression}")
        return False

    try:
        mode = f"r:{compression}" if compression else "r"
        with tarfile.open(archive_path, mode) as tar_file:
            tar_file.extractall(path=target_dir)
        logger.info(f"[green]Extracted tar archive to:[/green] {target_dir}")
        return True

    except Exception as e:
        logger.error(f"[red]Error extracting tar archive {archive_path}:[/red] {e}")

    return False

def extract_zip_archive(archive_path: PathLike, target_dir: PathLike) -> bool:
    """
    Extract a zip archive to the specified target directory.

    Args:
        archive_path: Path to the zip archive file
        target_dir: Path to the target directory where files will be extracted

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    if not core_extract_conditions(archive_path, target_dir):
        return False

    try:
        with zipfile.ZipFile(archive_path, "r") as zip_file:
            zip_file.extractall(path=target_dir)
        logger.info(f"[green]Extracted zip archive to:[/green] {target_dir}")
        return True

    except Exception as e:
        logger.error(f"[red]Error extracting zip archive {archive_path}:[/red] {e}")

    return False


def extract(archive_path: PathLike, target_dir: PathLike) -> bool:
    """
    Extract an archive to the specified target directory.

    Args:
        archive_path: Path to the archive file
        target_dir: Path to the target directory where files will be extracted

    Returns:
        bool: True if extraction was successful, False otherwise
    """
    archive_path = ensure_path(archive_path)
    target_dir = ensure_path(target_dir)
    if not core_extract_conditions(archive_path, target_dir):
        return False
    
    try:
        ext = get_file_extension(archive_path).lower()
        match ext:
            case ".7z":
                return extract_7z_archive(archive_path, target_dir)
    
            case ".rar":
                return extract_rar_archive(archive_path, target_dir)
            
            case ".tar" | ".tar.gz" | ".tar.bz2" | ".tar.xz":                
                compression = ext.replace(".tar", "").lstrip(".") or None
                return extract_tar_archive(archive_path, target_dir, compression)
            
            case ".zip":
                return extract_zip_archive(archive_path, target_dir)
            
            case _:
                logger.error(f"[red]Unsupported archive type:[/red] {ext}")
                return False
        
        return True

    except Exception as e:
        logger.error(f"[red]Error extracting archive {archive_path}:[/red] {e}")

    return False    
        
def list_content(archive_path: PathLike) -> List[Path]:
    """
    List all files in the specified archive.

    Args:
        archive_path: Path to the archive file

    Returns:
        List of file paths in the archive
    """
    archive_path = ensure_path(archive_path)
    if does_not_exists(archive_path) or not is_file(archive_path):
        logger.error(f"[red]Archive does not exist or is not a file:[/red] {archive_path}")
        return []

    try:
        ext = get_file_extension(archive_path).lower()
        match ext:
            case ".zip":
                with zipfile.ZipFile(archive_path, "r") as zip_file:
                    return [Path(file) for file in zip_file.namelist()]
            case ".7z":
                with py7zr.SevenZipFile(archive_path, "r") as archive:
                    return [Path(file) for file in archive.getnames()]
            case ".rar":
                with rarfile.RarFile(archive_path, "r") as archive:
                    return [Path(file.filename) for file in archive.infolist()]
            case ".tar" | ".tar.gz" | ".tar.bz2" | ".tar.xz":
                with tarfile.open(archive_path, "r") as archive:
                    return [Path(member.name) for member in archive.getmembers() if member.isfile()]
            case _:
                logger.error(f"[red]Unsupported archive type:[/red] {ext}")
                return []

    except Exception as e:
        logger.error(f"[red]Error listing contents of archive {archive_path}:[/red] {e}")
        
    return []

# - TODO: cli for extract, list, compress, and defaults like tar, zip, unzip, gzip, gunzip, rar, 7z(sevenz)