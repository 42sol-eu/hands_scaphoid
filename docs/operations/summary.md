# Summary of file system operations 

!!! Excludes

    This does not include operations for processes and system management.
    But the related remote commands (network based file system), user and groups are included.

## Elements:

```mermaid
graph TD;
    Item --> Object;
    Object --> Directory;
    Object --> File;
    Directory -contains-> File;
    Directory -contains-> Directory; 
    Object --> Link;
    File --> Archive;
    File --> Executable;
    File --> Script;
    Script -uses-> Executable;
    Directory --> MountPoint;
    Item --> Path;
    Item --> System;
    Item --> Variable;
```

- `Object`s are generic file system items
- `Directory`(Directories) are containers for files and other directories
- `File`s are holding data in text or binary format
- `Link`s are references to other file system items

- `Archive`s are special `File` containers compressed files holding multiple files and directories
- `Executable`s are special binary `File`s that can be run as programs or interpreters
- `Script`s are special text `File`s that contain a series of commands to be executed by a specific interpreter
- `Mount points` are special `Directory`s, locations in the file system where additional file systems can be attached

- `Path`s are `Item`s (string representation) of the location of a file system `Item`
- `System`s are addresses or URLs to remote file systems (e.g. network shares, cloud storage or inside containers)
- `Variable`s are special simple `Item`s that hold configuration values like environment settings or default paths they have a `Key` (e.g. `$HOME`, `$PATH`, `$USER`) and a `Value` (e.g. `/home/user`, `/usr/bin:/bin`, `user`)

=== Types of Operations

Types of operations:

| Symbol | Type          | Description                                       |
|--------|---------------|---------------------------------------------------|
| M      | meta          | read-access that retrieves metadata               |
| R      | read          | read-access that retrieves data                   |
| S      | show          | read-access that displays data                    |
| U      | update        | write-access that modifies existing meta data     |
| C      | create        | write-access that creates new data (no overwrite) |
| W      | write         | write-access that extends or over-writes data     |
| D      | delete/remove | write-access that destroys data                   |


=== Generic Operations


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
=== Generic commands

| Operation                          | Bash                  | Description                                          |
|------------------------------------|-----------------------|------------------------------------------------------|
| show_user                          | `whoami`              | Show current user name                               |
| change_user( user )                | `su - user`           | Change to another user                               |
| show_groups( user )                | `groups`              | Show groups of given user name, defaults to current user |
| change_owner( user, file )         | `chown user file`     | Change owner of a file or directory                  |
| change_group( group, file )        | `chgrp group file`    | Change group of a file or directory                  |