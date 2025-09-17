from enum import Enum

class ItemType(str, Enum):
    """Enum representing different types of items."""
    ITEM       = "item"
    VARIABLE   = "variable"
    PATH       = "path"
    FILE       = "file"
    DIRECTORY  = "directory"
    ARCHIVE    = "archive"
    LINK       = "link"
    MOUNT      = "mount"
    SYSTEM     = "system"
    # Additional item types can be added here as needed.

class SimpleCommandType(str, Enum):
    """Enum representing different types of simple commands."""
    READ = "read-access"
    WRITE = "write-access"
    DELETE = "delete-access"
    EXECUTE = "execute-access"
    # Additional command types can be added here as needed.

class AccessCommandType(str, Enum):
    """Enum representing different types of access permissions.

    Each access type is represented by a single character symbol.
    see https://hands-scaphoid.readthedocs.io/en/latest/operations/summary.html
    
    """

    META    = "M"
    READ    = "R"
    SHOW    = "S"
    UPDATE  = "U"
    CREATE  = "C"
    WRITE   = "W"
    DELETE  = "D"
    EXECUTE = "E"
    # Additional access types can be added here as needed.

class CommandType(str, Enum):
    """Enum representing different command categories."""
    EXISTS = "exists"
    

| exists( path )                     | M      | `test -e {path}`        | Check if an object exists at the given path            |
| exists( system_path )              | M      | `test -e {system_path}` | Check if a system object exists at the given path      |
| type( path )                       | M      | `file {path}`           | Show the type of object at the given path              |
| permissions( path )                | M      | `ls -l {path}`          | Show the permissions of the object at the given path   |
| size( path )                       | M      | `du -sh {path}`         | Show the size of the object at the given path          |
| list( path, pattern )              | S      | `ls -l {path} | grep {pattern}` | List contents of a directory, archive or file path |
| ...                                | S      | `cat {file_path}`       | Show contents of a file at the given path              |
| list( file_path, head=<n>)         | S      | `head {file_path}`      | Show first lines of a file at the given path           |
| list( file_path, tail=<n>)         | S      | `tail {file_path}`      | Show last lines of a file at the given path            |
| list( file_path, pattern )         | S      | `grep {pattern} {file_path}`    | Show lines matching pattern in a file            |
| list( archive_path )               | S      | `tar -tf {archive_path}`| List contents of an archive at the given path          |
| show( type )                       | R      | `ls -l`                 | Show all objects of the given type in the current directory |
| permissions( path, mode )          | U      | `chmod {mode} {path}`   | Change the permissions of the object at the given path |
| permissions( path, user, group )   | U      | `chown {user:group} {path}` | Change the owner and group of the object at the given path |
| link( path )                       | C      | `ln -s {path}`          | Create a (symbolic) link at the given path             |
| mount( system, mount_point )       | C      | `mount {system} {path}` | Mount a remote file system at the given mount point |
| extract( archive_path, target )    | C      | `tar -xf {archive_path} -C {target}` | Extract contents of an archive to the target path |
| create( object_path )              | C/W    | `touch {path}`          | Create an empty object at the given path               |
| move( source, destination )        | W      | `mv {source} {target}`  | Move or rename an object from source to target path    |
| copy( source, destination )        | W      | `cp {source} {target}`  | Copy or duplicate an object from source to target path |
| unlink( path )                     | D      | `rm {path}`             | Remove a (symbolic) link at the given path             |
| delete( path, recursive=false )    | D      | `rm {path}`             | Delete the object at the given path                    |
| delete( path, recursive=true )     | D+     | `rm -r {path}`          | Recursively delete the object at the given path        |
| unmount( mount_point )             | D      | `umount {path}`         | Unmount a remote file system from the given mount point |
| execute( file_path, args )        | E      | `{file_path} {args}`    | Execute a file at the given path with optional arguments |
