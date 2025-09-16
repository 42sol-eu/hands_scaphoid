#TODO: use Directory and DirectoryContext

#TODO: implement functions 

from pathlib import Path


def get_current(self) -> Path:
    """
    Get the current absolute path of this directory context.
    
    Returns:
        The absolute path of this directory
    """
    return self.resolve_path()

def list_contents(self) -> list[Path]:
    """
    List the contents of this directory.
    
    Returns:
        List of paths in this directory
    """
    if self.dry_run:
        print(f"[DRY RUN] Would list contents of: {self.resolve_path()}")
        return []
        
    if not self._entered:
        # If not in context, list the resolved path
        path = self.resolve_path()
    else:
        # If in context, list current directory
        path = Path.cwd()
    
    try:
        return list(path.iterdir())
    except PermissionError:
        print(f"Permission denied listing directory: {path}")
        return []
    except Exception as e:
        print(f"Error listing directory {path}: {e}")
        return []

def create_directory(self, name: str) -> 'Directory':
    """
    Create a subdirectory within this directory context.
    
    Args:
        name: Name of the subdirectory to create
        
    Returns:
        A new Directory instance for the subdirectory
    """
    return Directory(name, create=True, dry_run=self.dry_run)

def delete_directory(self, name: str, recursive: bool = False, force: bool = False, allow_empty: bool = False, dry_run: bool = False) -> bool: 
    """
    Delete a subdirectory within this directory context.
    
    Args:
        name: Name of the subdirectory to delete
        
    Returns:
        True if deleted successfully, False otherwise
    """
    subdir = self.resolve_path() / name
    if not subdir.exists() or not subdir.is_dir():
        if not self.allow_empty:
            print(f"Directory does not exist: {subdir}")
        return False
    
    try:
        if dry_run:
            print(f"[DRY RUN] Would delete directory: {subdir}")
            return True
        subdir.rmdir()
        print(f"Deleted directory: {subdir}")
        return True
    except Exception as e:
        print(f"Error deleting directory {subdir}: {e}")
        return False