from Typing import List, Optional, Any
from pathlib import Path
from rich.console import Console
import hands_scaphoid.Archive_Old_Context as ArchiveModule
from ..contexts.Context import Context
#TODO: Use __base__ for os, zipfile, console, etc.
console = Console()

def create_archive(archive_name: str, source: Path, dry_run: bool = False) -> bool:
    """
    Create a zip archive from the specified source directory.
    
    Args:
        archive_name: Name of the output archive file (without extension)
        source: Path to the source directory to archive
        dry_run: If True, simulate the operation without making changes
    
    Returns:
        bool: True if the archive was created, False otherwise
    """
    
    archive_path = Path(f"{archive_name}.zip")
    
    if not source.exists() or not source.is_dir():
        console.print(f"[red]Source directory does not exist or is not a directory:[/red] {source}")
        return
    
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(source):
                for file in files:
                    file_path = Path(root) / file
                    zipf.write(file_path, file_path.relative_to(source))
        console.print(f"[green]Created archive:[/green] {archive_path}")
    except Exception as e:
        console.print(f"[red]Error creating archive {archive_path}:[/red] {e}")

def list_archives(dry_run: bool = False) -> List[Path]:
    """
    List all archive files in the current directory.
    
    Args:
        dry_run: If True, simulate the operation without making changes
    Returns:
        List of archive file paths
    """
    current_context = Context.get_current_context()
    if current_context and current_context.dry_run:
        dry_run = True
    
    if dry_run:
        console.print(f"[dim][DRY RUN] Would list archives in: {Path.cwd()}[/dim]")
        return []
    
    archive_extensions = ['.zip', '.tar', '.tar.gz', '.tgz', '.tar.bz2', '.tbz2']
    archives = []
    try:
        for item in Path.cwd().iterdir():
            if item.is_file() and item.suffix in archive_extensions:
                archives.append(item)
    except PermissionError:
        console.print(f"[red]Permission denied listing archives in:[/red] {Path.cwd()}")
    except Exception as e:
        console.print(f"[red]Error listing archives in {Path.cwd()}:[/red] {e}")
    
    return archives
