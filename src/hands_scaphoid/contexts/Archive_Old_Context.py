


class ArchiveContextOld(Context):
    """
    Archive context manager for hierarchical file system operations.
    
    This class allows you to work with archives (ZIP, TAR, etc.) in a hierarchical context,
    providing convenient methods for creating, reading, and manipulating archive content
    while maintaining awareness of the current directory context.
    
    Example:
        with DirectoryCore('~') as home:
            with DirectoryCore('projects') as projects:
                with ArchiveFile(source='myproject', target='backup.zip') as archive:
                    archive.add_directory('myproject')
                    archive.add_file('README.md')
    """
    
    def __init__(self, source: Optional[PathLike] = None, target: Optional[PathLike] = None, 
                 archive_type: str = 'zip', create: bool = True, dry_run: bool = False, enable_globals: bool = False):
        """
        Initialize a new Archive context.
        
        Args:
            source: Source directory, file, or existing archive to work with (optional)
            target: Target archive file path (defaults to source name with archive extension)
            archive_type: Type of archive ('zip', 'tar', 'tar.gz', 'tar.bz2')
            create: Whether to create the archive if it doesn't exist (default: True)
            dry_run: Whether to simulate operations without making actual changes
            enable_globals: Whether to enable global function access within context
        """
        self.source_is_archive = False
        
        if target is None and source is not None:
            source_path = Path(source)
            
            # Check if source is an existing archive
            if source_path.exists() and source_path.is_file():
                source_suffix = source_path.suffix.lower()
                if source_suffix in ['.zip', '.tar', '.gz', '.bz2'] or source_path.name.endswith(('.tar.gz', '.tar.bz2')):
                    # Source is an existing archive, use it as target
                    target = source
                    self.source_is_archive = True
                    # Determine archive type from file extension
                    if source_suffix == '.zip':
                        archive_type = 'zip'
                    elif source_path.name.endswith('.tar.gz'):
                        archive_type = 'tar.gz'
                    elif source_path.name.endswith('.tar.bz2'):
                        archive_type = 'tar.bz2'
                    elif source_suffix in ['.tar']:
                        archive_type = 'tar'
                    # Clear source since we're working with the archive directly
                    source = None
            else:
                # Source is a directory or file to be archived
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
        
        if target is None:
            raise ValueError("Either source or target must be specified")
        
        super().__init__(target, create, dry_run, enable_globals)
        self.source = Path(source) if source else None
        self.archive_type = archive_type.lower()
        self.archive_handle: Optional[Any] = None
        self._temp_dir: Optional[Path] = None
        
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
            
        try:
            # Create parent directories if they don't exist
            resolved_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create empty archive if it doesn't exist
            if not resolved_path.exists():
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(resolved_path, 'w') as zf:
                        pass  # Create empty zip
                elif self.archive_type.startswith('tar'):
                    mode = 'w'
                    if self.archive_type == 'tar.gz':
                        mode = 'w:gz'
                    elif self.archive_type == 'tar.bz2':
                        mode = 'w:bz2'
                    
                    with tarfile.open(resolved_path, mode) as tf:
                        pass  # Create empty tar
                
                console.print(f"[green]Created archive:[/green] {resolved_path}")
        except PermissionError:
            console.print(f"[red]Permission denied creating archive:[/red] {resolved_path}")
            raise
        except Exception as e:
            console.print(f"[red]Error creating archive {resolved_path}:[/red] {e}")
            raise
    
    def _enter_context(self, resolved_path: Path) -> None:
        """
        Open the archive when entering the context.
        
        Args:
            resolved_path: The resolved absolute path for this context
        """
        if not resolved_path.exists():
            raise FileNotFoundError(f"Archive does not exist: {resolved_path}")
        
        try:
            if self.archive_type == 'zip':
                self.archive_handle = zipfile.ZipFile(resolved_path, 'a')
            elif self.archive_type.startswith('tar'):
                mode = 'a'
                if self.archive_type == 'tar.gz':
                    mode = 'a:gz'
                elif self.archive_type == 'tar.bz2':
                    mode = 'a:bz2'
                
                # For new files, use write mode instead of append
                if resolved_path.stat().st_size == 0:
                    mode = mode.replace('a', 'w')
                
                self.archive_handle = tarfile.open(resolved_path, mode)
            
            # If source is specified and it's not already an archive being opened, add it to the archive
            if self.source and self.source.exists() and not self.source_is_archive:
                self._add_source_to_archive()
            
            console.print(f"[blue]Opened archive:[/blue] {resolved_path}")
        except PermissionError:
            console.print(f"[red]Permission denied opening archive:[/red] {resolved_path}")
            raise
        except Exception as e:
            console.print(f"[red]Error opening archive {resolved_path}:[/red] {e}")
            raise
    
    def _exit_context(self, resolved_path: Path) -> None:
        """
        Close the archive when exiting the context.
        
        Args:
            resolved_path: The resolved absolute path for this context
        """
        if self.archive_handle:
            try:
                self.archive_handle.close()
                console.print(f"[blue]Closed archive:[/blue] {resolved_path}")
            except Exception as e:
                console.print(f"[red]Error closing archive {resolved_path}:[/red] {e}")
                # Don't raise here as we're exiting
        
        # Clean up temporary directory if created
        if self._temp_dir and self._temp_dir.exists():
            try:
                shutil.rmtree(self._temp_dir)
            except Exception:
                pass  # Ignore cleanup errors
    
    def _add_source_to_archive(self) -> None:
        """Add the source directory or file to the archive."""
        if not self.source or not self.source.exists():
            return
        
        if self.source.is_file():
            self.add_file(self.source)
        elif self.source.is_dir():
            self.add_directory(self.source)
    
    def add_file(self, file_path: PathLike, archive_name: Optional[str] = None) -> 'Archive':
        """
        Add a file to the archive.
        
        Args:
            file_path: Path to the file to add
            archive_name: Name to use in the archive (defaults to file name)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would add file to archive: {file_path}[/dim]")
            return self
            
        if not self._entered:
            # Standalone mode - temporarily open archive
            return self._standalone_add_file(file_path, archive_name)
        
        # Context mode
        file_path = self._resolve_relative_path(file_path)
        
        if not file_path.exists():
            console.print(f"[yellow]Warning: File does not exist:[/yellow] {file_path}")
            return self
        
        if not file_path.is_file():
            console.print(f"[yellow]Warning: Path is not a file:[/yellow] {file_path}")
            return self
        
        if archive_name is None:
            archive_name = file_path.name
        
        try:
            if self.archive_type == 'zip':
                self.archive_handle.write(file_path, archive_name)
            elif self.archive_type.startswith('tar'):
                self.archive_handle.add(file_path, arcname=archive_name)
            
            console.print(f"[green]Added file to archive:[/green] {archive_name}")
        except Exception as e:
            console.print(f"[red]Error adding file {file_path} to archive:[/red] {e}")
            raise
        
        return self
    
    def add_directory(self, dir_path: PathLike, archive_name: Optional[str] = None) -> 'Archive':
        """
        Add a directory and its contents to the archive.
        
        Args:
            dir_path: Path to the directory to add
            archive_name: Name to use in the archive (defaults to directory name)
            
        Returns:
            Self for method chaining
        """
        if self.dry_run:
            console.print(f"[dim][DRY RUN] Would add directory to archive: {dir_path}[/dim]")
            return self
            
        if not self._entered:
            # Standalone mode - temporarily open archive
            return self._standalone_add_directory(dir_path, archive_name)
        
        # Context mode
        dir_path = self._resolve_relative_path(dir_path)
        
        if not dir_path.exists():
            console.print(f"[yellow]Warning: Directory does not exist:[/yellow] {dir_path}")
            return self
        
        if not dir_path.is_dir():
            console.print(f"[yellow]Warning: Path is not a directory:[/yellow] {dir_path}")
            return self
        
        if archive_name is None:
            archive_name = dir_path.name
        
        try:
            # Add all files in the directory recursively
            for file_path in dir_path.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path within the directory
                    rel_path = file_path.relative_to(dir_path)
                    archive_file_name = str(Path(archive_name) / rel_path)
                    
                    if self.archive_type == 'zip':
                        self.archive_handle.write(file_path, archive_file_name)
                    elif self.archive_type.startswith('tar'):
                        self.archive_handle.add(file_path, arcname=archive_file_name)
            
            console.print(f"[green]Added directory to archive:[/green] {archive_name}")
        except Exception as e:
            console.print(f"[red]Error adding directory {dir_path} to archive:[/red] {e}")
            raise
        
        return self
    
    def list_contents(self) -> List[str]:
        """
        List the contents of the archive.
        
        Returns:
            List of file names in the archive
        """
        if not self._entered or not self.archive_handle:
            # If not in context, open temporarily to list contents
            resolved_path = self.resolve_path()
            if not resolved_path.exists():
                return []
            
            try:
                if self.archive_type == 'zip':
                    with zipfile.ZipFile(resolved_path, 'r') as zf:
                        return zf.namelist()
                elif self.archive_type.startswith('tar'):
                    mode = 'r'
                    if self.archive_type == 'tar.gz':
                        mode = 'r:gz'
                    elif self.archive_type == 'tar.bz2':
                        mode = 'r:bz2'
                    
                    with tarfile.open(resolved_path, mode) as tf:
                        return tf.getnames()
            except Exception as e:
                console.print(f"[red]Error listing archive contents:[/red] {e}")
                return []
        
        try:
            if self.archive_type == 'zip':
                return self.archive_handle.namelist()
            elif self.archive_type.startswith('tar'):
                return self.archive_handle.getnames()
        except Exception as e:
            console.print(f"[red]Error listing archive contents:[/red] {e}")
            return []
        
        return []
    
    def extract_to(self, extract_path: PathLike) -> None:
        """
        Extract the archive to a directory.
        
        Args:
            extract_path: Directory to extract to
        """
        extract_path = Path(extract_path)
        extract_path.mkdir(parents=True, exist_ok=True)
        
        resolved_path = self.resolve_path()
        if not resolved_path.exists():
            raise FileNotFoundError(f"Archive does not exist: {resolved_path}")
        
        try:
            if self.archive_type == 'zip':
                with zipfile.ZipFile(resolved_path, 'r') as zf:
                    zf.extractall(extract_path)
            elif self.archive_type.startswith('tar'):
                mode = 'r'
                if self.archive_type == 'tar.gz':
                    mode = 'r:gz'
                elif self.archive_type == 'tar.bz2':
                    mode = 'r:bz2'
                
                with tarfile.open(resolved_path, mode) as tf:
                    tf.extractall(extract_path)
            
            console.print(f"[green]Extracted archive to:[/green] {extract_path}")
        except Exception as e:
            console.print(f"[red]Error extracting archive:[/red] {e}")
            raise
    
    def _resolve_relative_path(self, path: PathLike) -> Path:
        """
        Resolve a path relative to the current context.
        
        Args:
            path: Path to resolve
            
        Returns:
            Resolved absolute path
        """
        path = Path(path)
        if path.is_absolute():
            return path
        
        # Resolve relative to current context
        current_context = self.get_current_context()
        if current_context and current_context != self:
            return current_context.resolve_path() / path
        
        return Path.cwd() / path
    
    def get_archive_info(self) -> Dict[str, Any]:
        """
        Get information about the archive.
        
        Returns:
            Dictionary with archive information
        """
        resolved_path = self.resolve_path()
        info = {
            'path': str(resolved_path),
            'type': self.archive_type,
            'exists': resolved_path.exists(),
            'size': 0,
            'file_count': 0
        }
        
        if resolved_path.exists():
            try:
                info['size'] = resolved_path.stat().st_size
                info['file_count'] = len(self.list_contents())
            except Exception:
                pass
        
        return info
    
    def _standalone_add_file(self, file_path: PathLike, archive_name: Optional[str] = None) -> 'Archive':
        """Add a file to the archive in standalone mode."""
        resolved_path = self.resolve_path()
        if not resolved_path.exists():
            if self.create:
                self._create_path(resolved_path)
            else:
                raise FileNotFoundError(f"Archive does not exist: {resolved_path}")
        
        file_path = self._resolve_relative_path(file_path)
        if not file_path.exists() or not file_path.is_file():
            console.print(f"[yellow]Warning: File does not exist or is not a file:[/yellow] {file_path}")
            return self
        
        if archive_name is None:
            archive_name = file_path.name
        
        try:
            if self.archive_type == 'zip':
                with zipfile.ZipFile(resolved_path, 'a') as zf:
                    zf.write(file_path, archive_name)
            elif self.archive_type.startswith('tar'):
                mode = 'a'
                if self.archive_type == 'tar.gz':
                    mode = 'a:gz'
                elif self.archive_type == 'tar.bz2':
                    mode = 'a:bz2'
                
                with tarfile.open(resolved_path, mode) as tf:
                    tf.add(file_path, arcname=archive_name)
            
            console.print(f"[green]Added file to archive:[/green] {archive_name}")
        except Exception as e:
            console.print(f"[red]Error adding file {file_path} to archive:[/red] {e}")
            raise
        
        return self
    
    def _standalone_add_directory(self, dir_path: PathLike, archive_name: Optional[str] = None) -> 'Archive':
        """Add a directory to the archive in standalone mode."""
        resolved_path = self.resolve_path()
        if not resolved_path.exists():
            if self.create:
                self._create_path(resolved_path)
            else:
                raise FileNotFoundError(f"Archive does not exist: {resolved_path}")
        
        dir_path = self._resolve_relative_path(dir_path)
        if not dir_path.exists() or not dir_path.is_dir():
            console.print(f"[yellow]Warning: Directory does not exist or is not a directory:[/yellow] {dir_path}")
            return self
        
        if archive_name is None:
            archive_name = dir_path.name
        
        try:
            if self.archive_type == 'zip':
                with zipfile.ZipFile(resolved_path, 'a') as zf:
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(dir_path)
                            archive_file_name = str(Path(archive_name) / rel_path)
                            zf.write(file_path, archive_file_name)
            elif self.archive_type.startswith('tar'):
                mode = 'a'
                if self.archive_type == 'tar.gz':
                    mode = 'a:gz'
                elif self.archive_type == 'tar.bz2':
                    mode = 'a:bz2'
                
                with tarfile.open(resolved_path, mode) as tf:
                    for file_path in dir_path.rglob('*'):
                        if file_path.is_file():
                            rel_path = file_path.relative_to(dir_path)
                            archive_file_name = str(Path(archive_name) / rel_path)
                            tf.add(file_path, arcname=archive_file_name)
            
            console.print(f"[green]Added directory to archive:[/green] {archive_name}")
        except Exception as e:
            console.print(f"[red]Error adding directory {dir_path} to archive:[/red] {e}")
            raise
        
        return self
