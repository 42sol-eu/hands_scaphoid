

def get_file_extension(filename: str) -> str:
    """
    Get the file extension from a filename.
    
    Also supports double extensions like .tar.gz and modern graphical extensions like .drawio.png.

    Args:
        filename (str): The name of the file.
    Returns:
        str: The file extension, or an empty string if none exists.
    """
    filename = filename.lower()
    parts = filename.rsplit('.', 1)
    if len(parts) == 0:
        return ''

    extension = parts[-1]

    #!md|# Handle double extensions
    if len(parts) > 2:
        #!md|- Archive  extensions like .tar.gz
        if extension == 'gz' and len(parts) > 2 and parts[-2] == 'tar':
            extension = 'tar.gz'

        #!md|# Handle modern graphical extensions
        #!md|- Excalidraw and Draw.io use double extensions
        if extension in ['png', 'svg'] and len(parts) > 2:
            extension = f'{parts[-2]}.{extension}'

    return extension

