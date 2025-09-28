"""
CLI archive commands.
---yaml
File:
    name:        archive.py  
    uuid:        186217d9-4814-4c02-ae38-52ba508c1221
    date:        2025-09-28
Description:     archive commands line interface

Project:
    name:        hands_scaphoid
    uuid:        2945ba3b-2d66-4dff-b898-672c386f03f4
    url:         https://github.com/42sol-eu/hands_scaphoid

Authors: ["Andreas Felix Häberle <felix@42sol.eu>"]
"""

from ..__base__ import PathLike, console
import click
from rich_click import *
from rich.console import Console

from ..contexts.ArchiveContext import ArchiveContext 

@click.group()
def cli() -> int:
    """Archive command group."""
    return 0

@click.argument("archive_path", type=click.Path(exists=True), 
                help="Path to the archive file.")
@cli.command()
def test(archive_path: PathLike) -> int:
    """List content of an archive, for all supported types."""
    with ArchiveContext(source=archive_path) as archive:
        result = archive.test()
    return result


@click.argument("archive_path", type=click.Path(exists=True), 
                help="Path to the archive file.")
@cli.command()
def list(archive_path: PathLike) -> int:
    """List content of an archive, for all supported types."""
    with ArchiveContext(source=archive_path) as archive:
        result = archive.list_contents()
    return result


@click.argument("archive_path", type=click.Path(exists=True),
                help="Path to the archive file.")
@click.argument("target_path", type=click.Path(exists=False),
                help="Path to the target directory, to be used for extractions.")
@cli.command()
def extract(archive_path: PathLike, target_path: PathLike) -> int:
    """Extract an archive to a specified location."""
    with ArchiveContext(source=archive_path, target=target_path) as archive:
        result = archive.extract()
    return result


@click.argument("source_path", type=click.Path(exists=True),
                help="Path to the source directory.")
@click.argument("archive_path", type=click.Path(exists=False),
                help="Path to the archive file, to be created.")
@cli.command()
def compress(source_path: PathLike, archive_path: PathLike) -> int:
    """Compress a directory into an archive."""
    with ArchiveContext(source=source_path, target=archive_path) as archive:
        result = archive.compress()
    return result


