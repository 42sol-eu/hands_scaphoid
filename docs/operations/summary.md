# Summary of file system operations 

!!! Excludes

    This does not include operations for processes and system management.
    But the related remote commands (network based file system), user and groups are included.

## Elements:

- `Object`s are generic file system items
- `Directory`(Directories) are containers for files and other directories
- `File`s are holding data in text or binary format
- `Link`s are references to other file system items

- `Archive`s are special `file` containers compressed files holding multiple files and directories
- `Executable`s are special binary `file`s that can be run as programs or interpreters
- `Script`s are special text `file`s that contain a series of commands to be executed by a specific interpreter
- `Mount points` are special `directory`s, locations in the file system where additional file systems can be attached

- `Path`s are the string representation of the location of a file system `Item`
- `System`s are addresses or URLs to remote file systems (e.g. network shares, cloud storage or inside containers)
- `Variable`s are special simple `objects`s that hold configuration values like environment settings or default paths (e.g. `$HOME`, `$PATH`, `$USER`)

- 
=== Generic Operations

| Operation                          | Bash                  | Description                                            |
|------------------------------------|-----------------------|--------------------------------------------------------|
| show( type )                       | `ls -l`               | Show all objects of the given type in the current directory |
| create( object_path )              | `touch path`          | Create an empty object at the given path               |
| delete( path, recursive=false )    | `rm path`             | Delete the object at the given path                    |
| delete( path, recursive=true )     | `rm -r path`          | Recursively delete the object at the given path        |
| exists( path )                     | `test -e path`        | Check if an object exists at the given path            |
| exists( system_path )              | `test -e system_path` | Check if a system object exists at the given path      |
| type( path )                       | `file path`           | Show the type of object at the given path              |
| size( path )                       | `du -sh path`         | Show the size of the object at the given path          |
| link( path )                       | `ln -s path`          | Create a (symbolic) link at the given path             |
| unlink( path )                     | `rm path`             | Remove a (symbolic) link at the given path             |
| move( source, destination )        | `mv source target`    | Move or rename an object from source to target path    |
| copy( source, destination )        | `cp source target`    | Copy or duplicate an object from source to target path |
| list( path, pattern )              | `ls -l path | grep pattern` | List contents of a directory, archive or file path |
| ...                                | `cat file_path`       | Show contents of a file at the given path              |
| list( file_path, head=<n>)         | `head file_path`      | Show first lines of a file at the given path           |
| list( file_path, tail=<n>)         | `tail file_path`      | Show last lines of a file at the given path            |
| list( file_path, pattern )         | `grep pattern file_path`    | Show lines matching pattern in a file            |
| list( archive_path )               | `tar -tf archive_path`| List contents of an archive at the given path          |
| extract( archive_path, target )    | `tar -xf archive_path -C dest` | Extract contents of an archive to the target path |

=== Generic commands

| Operation                          | Bash                  | Description                                          |
|------------------------------------|-----------------------|------------------------------------------------------|
| show_user                          | `whoami`              | Show current user name                               |
| change_user( user )                | `su - user`           | Change to another user                               |
| show_groups( user )                | `groups`              | Show groups of given user name, defaults to current user |
| change_owner( user, file )         | `chown user file`     | Change owner of a file or directory                  |
| change_group( group, file )        | `chgrp group file`    | Change group of a file or directory                  |