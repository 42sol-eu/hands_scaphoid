# Summary of file system operations 

!!! Excludes

    This does not include operations for processes and system management.
    But the related remote commands (network based file system), user and groups are included.

## Elements:

``` mermaid
---
config:
  layout: elk
---
graph TD;
    ItemCore@{ shape: rounded} --> ObjectItem@{ shape: rounded}
    ObjectItem --> n1@{ shape: anchor}
    ItemCore --> PathVariable@{ shape: rounded};
    ItemCore --> System['system']@{ shape: card};
    System['system'] -->|provides| Filesystem['filesystem'];
    ItemCore --> VariableItem@{ shape: rounded};
    Environment['environment']@{ shape: card} -->|contains| VariableItem;
    
```

- `ItemCore` is the top most generic items
- `VariableItem` is a special simple `ItemCore` that hold configuration values like environment settings or default paths they have a `Key` (e.g. `$HOME`, `$PATH`, `$USER`) and a `Value` (e.g. `/home/user`, `/usr/bin:/bin`, `user`)
- `Environment` holds  `Variable(s)` that hold information about the execution environment (e.g. paths, user info)
- `PathVariable` is a string representation of file system locations
- `System` is a special `ItemCore` that holds addresses or URLs (`PathVariable`) to remote file systems (e.g. network shares, cloud storage or inside containers)


``` mermaid
---
config:
  layout: elk
---
flowchart TD
    MountPoint@{ label: "'mount'" } -- provides --> DirectoryObject["DirectoryObject"]
    ObjectItem["ObjectItem"] --> DirectoryObject & FileObject["FileObject"] & LinkObject["LinkObject"]
    DirectoryObject -- contains --> FileObject
    ArchiveFile["ArchiveFile"] -- extracts --> DirectoryObject
    FileObject --> ExecutableFile["ExecutableFile"] & ScriptFile["ScriptFile"]
    ScriptFile -- uses --> ExecutableFile
    DirectoryObject -- compresses --> ArchiveFile
    Path@{ label: "'path'" } -- identifies --> FileObject & DirectoryObject

    MountPoint@{ shape: card}
    DirectoryObject@{ shape: rounded}
    ObjectItem@{ shape: rounded}
    FileObject@{ shape: rounded}
    LinkObject@{ shape: rounded}
    ArchiveFile@{ shape: rounded} 
    FileObject --> ArchiveFile
    ExecutableFile@{ shape: rounded}
    ScriptFile@{ shape: rounded}
    Path@{ shape: card}
     ArchiveFile:::Ash
     ExecutableFile:::Ash
     ScriptFile:::Ash
    classDef Ash stroke-width:1px, stroke-dasharray:none, stroke:#999999, fill:#EEEEEE, color:#000000
```

- `ObjectItem`s are generic file system items.
- `DirectoryObject`(Directories) are containers for files and other directories.
- `FileObject`s are holding data in text or binary format.
- `LinkObject`s are references to other file system items.

- `Archive`s are special `File` containers compressed files holding multiple files and directories
- `ExecutableFile`s are special binary `File`s that can be run as programs or interpreters
- `ScriptFile`s are special text `File`s that contain a series of commands to be executed by a specific interpreter
- `MountPoints` are special `Directory`s, locations in the file system where additional file systems can be attached


=== "Types of Operations"

    | Symbol | Type          | Description                                       |
    |--------|---------------|---------------------------------------------------|
    | M      | meta          | read-access that retrieves metadata               |
    | R      | read          | read-access that retrieves data                   |
    | S      | show          | read-access that displays data                    |
    | U      | update        | write-access that modifies existing meta data     |
    | C      | create        | write-access that creates new data (no overwrite) |
    | W      | write         | write-access that extends or over-writes data     |
    | D      | delete/remove | delete-access that destroys data                   |
    | E      | execute       | unknown-access execute-access that runs a program or script      |


=== "Generic Operations"

    | Operation                          | Type   | Bash                    | Description                                            |
    |------------------------------------|--------|-------------------------|--------------------------------------------------------|
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

=== "Archive Operations"

      | Operation                          | Type   | Implementation Status | Test Coverage | Description                                            |
      |------------------------------------|--------|--------------------- |---------------|--------------------------------------------------------|
      | is_archive_file( path )            | M      | ✅ Implemented       | ✅ Complete   | Check if file is an archive based on extension         |
      | create_zip_archive( name, source ) | C      | ✅ Implemented       | ✅ Complete   | Create ZIP archive from directory                       |
      | create_tar_archive( name, source ) | C      | ✅ Implemented       | ✅ Complete   | Create TAR archive (with optional compression)         |
      | create_7z_archive( name, source )  | C      | ✅ Implemented       | ✅ Complete   | Create 7Z archive from directory                        |
      | create_rar_archive( name, source ) | C      | ✅ Implemented       | ✅ Complete   | Create RAR archive (requires external rar command)     |
      | extract( archive_path, target )    | C      | ✅ Implemented       | ✅ Complete   | Extract archive contents to target directory           |
      | list_contents( archive_path )      | S      | ✅ Implemented       | ✅ Complete   | List files and directories in archive                  |

=== "File Operations"

    | Operation                          | Type   | Implementation Status | Test Coverage | Description                                            |
    |------------------------------------|--------|--------------------- |---------------|--------------------------------------------------------|
    | read( path, head, tail )           | R      | ✅ Implemented       | ✅ Complete   | Read file content with optional head/tail limits       |
    | filter( path, pattern )            | S      | 🔄 TODO              | 🔄 Placeholder| Filter files by pattern (planned)                      |
    | write( path, data )                | W      | 🔄 TODO              | 🔄 Placeholder| Write data to file (planned)                           |
    | append( path, data )               | W      | 🔄 TODO              | 🔄 Placeholder| Append data to file (planned)                          |
    | create( path, data )               | C      | 🔄 TODO              | 🔄 Placeholder| Create new file with data (planned)                    |=== "Core Utilities"

    | Operation                          | Type   | Implementation Status | Test Coverage | Description                                            |
    |------------------------------------|--------|--------------------- |---------------|--------------------------------------------------------|
    | exists( path )                     | M      | ✅ Implemented       | ✅ Complete   | Check if path exists                                    |
    | does_not_exists( path )            | M      | ✅ Implemented       | ✅ Complete   | Check if path does not exist                            |
    | is_file( path )                    | M      | ✅ Implemented       | ✅ Complete   | Check if path is a file                                 |
    | is_directory( path )               | M      | ✅ Implemented       | ✅ Complete   | Check if path is a directory                            |
    | is_link( path )                    | M      | ✅ Implemented       | ✅ Complete   | Check if path is a symbolic link                        |
    | is_object( path )                  | M      | ✅ Implemented       | ✅ Complete   | Check if path is any file system object                |
    | is_project( path )                 | M      | ✅ Implemented       | ✅ Complete   | Check if directory is a project (git/vscode/hands)     |
    | get_file_extension( filename )     | M      | ✅ Implemented       | ✅ Complete   | Get file extension (supports complex extensions)       |
    | which( executable )                | M      | ✅ Implemented       | ✅ Complete   | Find executable in system PATH                          |
    | filter( path, pattern )            | S      | ✅ Implemented       | ✅ Complete   | Filter directory contents by glob pattern              |


=== "Generic commands"

    | Operation                          | Bash                  | Description                                          |
    |------------------------------------|-----------------------|------------------------------------------------------|
    | show_user                          | `whoami`              | Show current user name                               |
    | change_user( user )                | `su - user`           | Change to another user                               |
    | show_groups( user )                | `groups`              | Show groups of given user name, defaults to current user |
    | change_owner( user, file )         | `chown user file`     | Change owner of a file or directory                  |
    | change_group( group, file )        | `chgrp group file`    | Change group of a file or directory                  |


## Reports

=== "Test Coverage Summary"

    | Module              | Functions Tested | Coverage Level | Status        |
    |--------------------|------------------|----------------|---------------|
    | file_commands      | 1/5 functions    | 🟡 Partial     | Ready for expansion |
    | archive_commands   | 11/11 functions  | 🟢 Complete    | Fully tested |
    | core_commands      | 15/15 functions  | 🟢 Complete    | Comprehensive |

    **Legend:**
    - ✅ Implemented & Tested
    - 🔄 TODO/Planned
    - 🟢 Complete Coverage
    - 🟡 Partial Coverage  
    - 🔴 Needs Attention
