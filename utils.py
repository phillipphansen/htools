"""
This houses the functions used by the cli program.
"""

# =[ Imports ]=================================================================
from datetime import datetime as dt
import math
from pathlib import Path
import sys
from typing import Any, Iterable, Union

# =[ Global Variables ]========================================================



# =[ Functions ]===============================================================
def get_file_list(
        file_type: str = '*',
        file_path: Path = Path('.')
    ) -> Union[list[dict[str, str]], None]:
    """
    Creates dictionary of a list of the files and assocaited metadata.

    :param file_type: The file type to find in glob format ie '*.txt'.
        Defaults to any file.
    :type file_type: str, optional
    :param file_path: The directory to search. Defaults to current
        directory.
    :type file_path: Path, optional
    :return: The list of files found in the directory and associated
        data, None if no files found
    :rtype: Union[list[dict[str, str]], None]
    """
    # Get a list of files of specified file_type in specified path.
    # If no path was specified, run recursively into subfolders
    if str(file_path) == '.':
        files = list(file_path.rglob(file_type))
    else:
        files = list(file_path.glob(file_type))
    # Check for empty directory:
    if not files:
        # If no path was specified and there was no file after the
        # recursive search, it ain't there.
        if str(file_path) == '.':
            return None
        # Try agian but this time no path specified to do a recursive
        # search to check the program directory and all other subdirs.
        return None
    # Initialize the return list
    file_list = []
    # Iterate through the files
    for file in files:
        # Get the stats for the specific file in this iteration.
        file_stats = file.stat()
        size = file_stats.st_size
        # Make the file modified date into a readable 'YYYY-MM-DD HH:MM'
        mod_date = dt.fromtimestamp(file_stats.st_mtime).strftime(
                "%Y-%m-%d %H:%M"
                )
        # Create the dictionary entry
        file_dict = {'name': file.name, 'size': size, 'mdate': mod_date, 'path': str(file)}
        # Add to the file list
        file_list.append(file_dict)
    return file_list