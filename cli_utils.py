"""
Name:       cli_utils.py
Author:     Phil Hansen
Version:    20260227

Contains functions for formatting the Command Line Interface output.
"""

# =[ Imports ]=================================================================
from collections.abc import Iterable
from datetime import datetime as dt
import math
from pathlib import Path
import re
import shutil
import sys
from typing import Any

# =[ Global Variables ]========================================================

# =[ Custom Exceptions ]=======================================================
class UserQuitException(Exception):
    pass

# =[ Functions ]===============================================================
def scale_size(bytes: int) -> str:
    """
    Scales the input number of bytes into a more readable format.

    :param bytes: The number of bytes.
    :type bytes: int
    :return: The formatted size with units.
    :rtype: str
    """
    # Check for zero to avoid math errors.
    if bytes == 0:
        return "0 B"
    # Units defined in a list
    units = ["B", "KB", "MB", "GB", "TB"]
    # Index calculated logarithmically to get the 'unit level'.
    index = int(math.floor(math.log(bytes, 1024)))
    # To set up for division: how many bytes are needed to reach the
    # calculated 'unit level'.
    power = math.pow(1024, index)
    # Divide the orginal byte number by the calculated minimum to reach
    # that 'unit level' and round to 2 places.
    size = round(bytes/power, 2)
    # Return the formated string.
    return f"{size} {units[index]}"

def truncate(text: str, max_len: int) -> str:
    """
    Truncates a string to a maximum length adding an ellipsis to indicate
    truncation.
    
    :param text: The string to truncate.
    :type text: str
    :param max_len: The maximum length to truncate to.
    :type max_len: int
    :return: The truncated string.
    :rtype: str
    """
    # If the text is shorter than the max length, just return it.
    if len(text) <= max_len:
        return text
    # Otherwise trim it to the max length, minus 3 to add an ellipsis
    # to visually indicate the tuncation.
    else:
        return text[:max_len-3] + "..."
    
def camel_case(text: str) -> str:
    """
    Converts passed to text in Camel Case format, preserves spacing.
    
    :param text: The text to convert
    :type text: str
    :return: The converted string.
    :rtype: str
    """
    # First convert underscores and dashes to spaces.
    norm_spaces = text.replace('_', ' ').replace('-', ' ')
    # Split off the text separated by spaces into a list
    words = norm_spaces.split()
    # Return the capitalized joins
    return ' '.join(word.capitalize() for word in words)

def format(
        text: object,
        color: str = '',
        *,
        style: str = 'bold',
        reset: bool = True
    ) -> str:
    """
    Format text for terminal output using ANSI styles and colors.

    :param text: Text to format. Converts Objects to text.
    :type text: object
    :param color: Text color. Default no change.
    :type color: str, optional
    :param style: Text style. Default "bold".
    :type style: str, optional
    :param reset: Reset formatting after text. Default True.
    :type reset: bool, optional
    :return: Formatted text.
    :rtype: str
    """
    # Alias assignment check
    # Dictionary to match style choices.
    styles = {
        'bold': '\033[1m',
        'italic': '\033[3m',
        'underline': '\033[4m',
        'bold_underline': '\033[1m\033[4m'
    }
    # Dictionary to match color choices.
    colors = {
        'black': '\033[30m',
        'red': '\033[31m',
        'green': '\033[32m',
        'yellow': '\033[33m',
        'blue': '\033[34m',
        'magenta': '\033[35m',
        'cyan': '\033[36m',
        'white': '\033[37m',
        'bright_black': '\033[90m',
        'bright_red': '\033[91m',
        'bright_green': '\033[92m',
        'bright_yellow': '\033[93m',
        'bright_blue': '\033[94m',
        'bright_magenta': '\033[95m',
        'bright_cyan': '\033[96m',
        'bright_white': '\033[97m'
    }
    # This resets the formatting back to default text.
    if reset:
        reset_str = "\033[0m"
    else:
        reset_str = ""
    # Using .get() to avoid dictionary key errors.
    style = f"{styles.get(style, "")}"
    color = f"{colors.get(color, "")}"
    # Put it all together with the reset at the end.
    return f"{style}{color}{text}{reset_str}"

def norm_string(text: any) -> str:
    """
    Normalizes string for fuzzy matching. Returns BLANK_STRING if the passed
    text is empty.

    :param text: The string to be normalized.
    :type text: str
    :return: The normalized string. 
    :rtype: str
    """
    text = str(text).lower().strip()
    text = re.sub(r"[.,'()\-\u2013\u2014]", " ", text)
    text = re.sub(r"\bst\b", "saint", text)
    text = re.sub(r"\bste\b", "sainte", text)
    text = re.sub(r"\s+", " ", text).strip()
    if not text:
        text = "BLANK_STRING"
    return text

def grade_color(value: int) -> str:
    """
    Converts an integer into a color based on value.
    <=69: Red, 70-89: Yellow, >=90: Green

    :param value: The input number value.
    :type value: int
    :return: The color associated with the number value.
    :rtype: str
    """
    if value >= 90:
        return "green"
    elif value  >= 70:
        return "yellow"
    return "red"

def ask_yesno(question: str="Is this correct?") -> bool:
    """
    Simple yes or no input. Allows the user to quit too.
    
    :param question: A question to ask the user. (default: "Is this correct?")
    :type question: str, optional
    :return: True of False depending on the user saying yes or no
    :rtype: bool
    :raises UserQuitException: The user chose to quit.
    """
    # Standard loop to catch weird inputs.
    while True:
        choice = input(f"{question} (y/n): ")
        if choice.lower() == 'y':
            return True
        elif choice.lower() == 'n':
            return False
        elif choice.lower() == 'q':
            raise UserQuitException
        else:
            # Give some helpful text for the user.
            print(
                f"'{format(choice, 'red')}' isn't a valid option,"
                " please enter 'y' for yes, 'n' for no, or 'q' to quit."
            )

def map_desc(
        items: list[dict[str, str]],
        head: dict[str, str],
        map: dict[str, str]
    ) -> tuple[list[dict[str, str]], dict[str, str]]:
    """
    This maps a description to items in a list. It also serves to trim the list
    to items with a description.
    
    :param items: The passed list of items.
    :type items: list[dict[str, str]]
    :param head: The header to display when listing the items.
    :type head: dict[str, str]
    :param map: The descriptions to map to the list.
    :type map: dict[str, str]
    :return: The updated head and list of items.
    :rtype: tuple[list[dict[str, str]], dict[str, str]]
    """
    # Rebuild the head, adding a description key after first key.
    new_head = {}
    head_key_list = list(head.keys())
    first_key = head_key_list[0]
    new_head[first_key] = head[first_key]
    new_head['desc'] = 'Description'
    for key in head_key_list[1:]:
        new_head[key] = head[key]
    # Initialize a new list for the filtered items from the
    # item list
    trimmed_items = []
    # Get the dictionaries in items.
    for item in items:
        # Grab just the first first_key, this will be the one
        # matched to the map. Also needed to maintain the
        # structure of the original selection list in the new one.
        first_key = next(iter(item.keys()))
        # The value, not the key, is actually checked against the map dict.
        first_field = item[first_key]
        # Check if the field is in the map
        if first_field in map.keys():
            # It matched so replace the value with the value from
            # the map. But there are more keys and values than
            # just the first one so iterate through the them all.
            # Initialize a new dict to append to the list.
            new_dict = {}
            for key, value in item.items():
                # If its that first key, add the desc key after
                if key == first_key:
                    new_dict[key] = value
                    new_dict['desc'] = map[value]
                # Otherwise just copy the key value pair over.
                else:
                    new_dict[key] = value
            # Add the new dict to the list outside of the inner loop
            trimmed_items.append(new_dict)
    # Make sure there were actually matches, check for empty list
    if trimmed_items:
        # Replace the selection dict with the new one.
        return trimmed_items, new_head
    return items, head

def get_choice(
        selections: list[str] | list[dict[str, str]],
        return_key: str
    ) -> str:
    """
    Docstring for get_choice
    
    :param selections: Description
    :type selections: list[dict[str, str]]
    :param return_key: Description
    :type return_key: str
    :return: Description
    :rtype: str
    """
    while True:
        selection = input(
            "Enter the number of the item to select ('q' to quit): "
        )
        # User chose to quit.
        if selection.lower() == 'q':
            raise UserQuitException
        try:
            sel_num = int(selection)
            # Make sure the number is in the selction list.
            if 1 <= sel_num <= len(selections):
                # The first key in the selected dict is the return.
                if return_key == "_index_":
                    return str(int(selection)-1)
                # Check if its a simple list or complex. Type checkers hate this
                if isinstance(selections[0], str):
                    return selections[sel_num-1] # type: ignore
                else:
                    return selections[sel_num-1][return_key] # type: ignore
            else:
                print(
                    # Give the user help to correctly choose an item.
                    f"{format(sel_num, 'red')} isn't a valid option,"
                    f" please enter a number (1 - {len(selections)}), or 'q'"
                    " to quit."
                )
        # Exception needed for int(selection) input errors.
        except ValueError:
            print(
                f"'{format(selection, 'red')}' isn't a valid option,"
                f" please enter a number (1 - {len(selections)}), or 'q'"
                " to quit."
            )

def select_item(
        selections: list[dict[str, str]],
        header: dict[str, str] | None = None,
        *,
        return_key: str | None = None,
        suggestion: str | None = None,
        field_list: list | None = None,
        desc_map: dict[str, str] | None = None
    ) -> str:
    """
    Has the user select an item from a list. Command Line Interface.

    :param selections: The list of items to select from.
    :param header: Gives more readable name to the column headers.
        Builds a header from the keys in the selection dictionary if not
        passed. (default: None)
    :param return_key: A specific key from the dictionary in the selection list
        to return. Returns the first key value if not specified or not found.
        Use "_index_" to return the item number. (default: None)
    :param suggestion: Highlight item in the list. (default: None)
    :param field_list: Used to limit the selection list. (default: None)
    :param desc_map: A Dictionary of items to limit the selection list
        to. Doubles as map to give more readable names to the items by
        adding a 'Description' column. (default: None)
    :return: The selected item from the list.
    :raises UserQuitException: The user chose to quit. 
    :raises ValueError: An empty or improperly structured selection list.
    """
    # Check for empty list
    if selections and isinstance(selections, list):
        # Make sure its a list of dicts
        if not isinstance(selections[0], dict):
            raise ValueError("Invalid selection list passed!")
    else:
        raise ValueError("Invalid Selection list passed!")
    # No header passed, build one
    if header is None:
        header = {}
        # Get the keys from the first dictionary in the selection list.
        keys = selections[0].keys()
        # Iterate through them and make the text just a little nicer.
        for key in keys:
            # The expected header dictionary format is the keys match
            # the selection dict keys, and the values are the readable
            # display names for the columns.
            header[key] = camel_case(key)
    # Check if a Field Map dictionary was passed
    if desc_map is not None:
        selections, header = map_desc(selections, header, desc_map)
    # Check for field list if no field map, this is to prefer the map.
    # The logic is the same as the map but no swapping of values.
    elif field_list is not None:
        trimmed_selections = []
        for item in selections:
            first_key = next(iter(item.keys()))
            first_field = item[first_key]
            if first_field in field_list:
                new_dict = {}
                for key, value in item.items():
                    new_dict[key] = value
                trimmed_selections.append(new_dict)
        if trimmed_selections:
            selections = trimmed_selections
    # Get the values used as keys for the selections.
    key_list = list(header.keys())
    if return_key not in key_list and return_key != "_index_":
        return_key = key_list[0]
    # This list to set floors for the max_field_len_list values.
    min_field_len_list = []
    # Get the length of the keys. This sets the minimum length to the
    # column display field name.
    for value in header.values():
        min_field_len = len(value)
        min_field_len_list.append(min_field_len)
    max_field_len_list = []
    # Keep track of how much space is left in the terminal window.
    # subtract for {'#':<index_width} index column, the max width of the size
    # and date modified column, 10 and 17 respectively, and 1 for
    # the ending " " total 28
    # and another -1 for the last end=" "
    terminal_width = shutil.get_terminal_size().columns
    index_width = len(str(len(selections)))
    max_field_len_remaining = terminal_width - (index_width+1) - 1
    # Enumerate to index the min_field_len_list list with 'i'.
    for i, key in enumerate(header.keys()):
        # Used as a floor for the max() function below.
        max_len = min_field_len_list[i]
        for item in selections:
            # Field key is constant, get the max_len of the values.
            current_field_len = len(item[key])
            # Check for long values running off the terminal window
            if (
                max_field_len_remaining - (current_field_len+1) > 0
                and max_field_len_remaining - (max_len+1) > 0
            ):
                # Still have space in the terminal.
                max_len = max(current_field_len, max_len)
            else:
                # Ran out of space, cap it.
                max_len = max_field_len_remaining
        # Append outside of inner loop to single high value.
        max_field_len_remaining = max(0, max_field_len_remaining-(max_len+1))
        max_field_len_list.append(max_len)
    # Print the index line.
    print(f"{'#':<{index_width}}", end=" ")
    # Enumerated to index max_field_len_list with 'i'.
    for i, value in enumerate(header.values()):
        print(f"{value:<{max_field_len_list[i]}}", end=" ")
    # Advance to a new line after using end=" " and print line for index.
    print("\n" + "-" * index_width, end=" ")
    # Print a dashed line under the header for readability
    for length in max_field_len_list:
        print("-" * length, end=" ")
    # Advance to a new line after using end=" "
    print()
    # There was a suggested column passed:
    if suggestion is not None:
        # Get the value of the first key in the dictionary. This
        # should always be the key for the suggestion.
        first_key = next(iter(selections[0].keys()))
        # Enumerate here matches the keys of selections.
        for i, item in enumerate(selections, start=1):
            # Print the line/item number
            if selections[i-1][first_key] == suggestion:
                # This will highlight the suggestion for the user.
                print(format(f"{i:<{index_width}}", 'green'), end=" ")
            else:
                print(f"{i:<{index_width}}", end=" ")
            # Enumerated to index max_field_len_list.
            for j, key in enumerate(key_list):
                # Spacing set by max_field_len_list.
                length = max_field_len_list[j]
                # Print data at the intersection of i, key.
                # Check for the suggestion
                if selections[i-1][first_key] == suggestion:
                    # This will highlight the suggestion for the user.
                    print(format(
                        f"{truncate(selections[i-1][key], length):<{length}}",
                        'green'),
                        end = " "
                    )
                # Not the suggestion
                else:
                    print(
                        f"{truncate(selections[i-1][key], length):<{length}}",
                        end = " "
                    )
            print()
        # Add helper text for the user. Adds a newline for readability.
        print(
            f"\nThe suggested column '{suggestion}' is highlighted in "
            f"{format("green", 'green')}."
        )
    # No suggested column passed:
    else:
        # Enumerate here matches the keys of selections.
        for i, item in enumerate(selections, start=1):
            # Print the line/item number
            print(f"{i:<{index_width}}", end=" ")
            # Enumerated to index max_field_len_list.
            for j, key in enumerate(key_list):
                # Spacing set by max_field_len_list.
                length = max_field_len_list[j]
                # Print the piece of data at the intersection of i, key.
                print(
                    f"{truncate(selections[i-1][key], length):<{length}}",
                    end=" "
                )
            print()
        # Add a line after the selection list for readability.
        print()
    # Selection loop
    return get_choice(selections, return_key)

def select_item_simple(selections: Iterable[Any], return_index: bool = True) -> str:
    """
    Docstring for select_item_simple
    
    :param selections: Description
    :param return_index: Description
    :return: Description
    """
    selections = list(selections)
    terminal_width = shutil.get_terminal_size().columns
    index_width = len(str(len(selections)))
    width = terminal_width - index_width - 2
    print("#" + " " * index_width + "Selections")
    print("-" * index_width + " " + "-" * width)
    for i, item in enumerate(selections, start=1):
        # Print the line/item number
        print(f"{i:<{index_width}}", end=" ")
        # Enumerated to index max_field_len_list.
        print(
            f"{truncate(item, width):<{width}}",
            end=" "
        )
        # Add a line after the selection list for readability.
        print()
    print()
    # Selection loop
    if return_index:
        return_key = "_index_"
    else:
        return_key = ""
    return get_choice(selections, return_key)

def get_file_list(
        file_type: str = '*',
        file_path: Path = Path('.'),
        recurs: bool = False
    ) -> list[dict[str, str]] | None:
    """
    Creates dictionary of a list of the files and assocaited metadata.

    :param file_type: The file type to find in glob format ie '*.txt'.
        (default: '*')
    :param file_path: The directory to search. (default: '.')
    :return: The list of files found in the directory and associated
        data, None if no files found
    """
    # Get a list of files of specified file_type in specified path.
    if recurs:
        files = list(file_path.rglob(file_type))
    else:
        files = list(file_path.glob(file_type))
    # Check for empty directory:
    if not files:
        return None
    # Initialize the return list
    file_list = []
    # Iterate through the files
    for file in files:
        # Skip over directories.
        if not file.is_file():
            continue
        # Get the stats for the specific file in this iteration.
        file_stats = file.stat()
        # Scale the file size (bytes) to something more readable.
        size = scale_size(file_stats.st_size)
        # Make the file modified date into a readable 'YYYY-MM-DD HH:MM'
        mod_date = dt.fromtimestamp(file_stats.st_mtime).strftime(
                "%Y-%m-%d %H:%M"
                )
        # Create the dictionary entry
        file_dict = {
            'name': file.name,
            'size': size,
            'mdate': mod_date,
            'path': str(file)
        }
        # Add to the file list
        file_list.append(file_dict)
    return file_list

def build_header(
        selections: list[dict[str, str]],
        header_names: list
    ) -> dict[str, str]:
    """
    Fills out the selection header mapping dictionary. Command Line
    Interface
    
    :param selections: The list with the selectable items.
    :param header_names: The list of the readable names
        to give the selection columns
    :return: The selection header mapping dictionary now matched to the
        file list dictionary.
    :raises KeyError: If there is a mismatch in the number of keys in
        the passed dictionaries.
    """
    # Make a list of first dict's keys, should be the same for all.
    if selections is None:
        raise ValueError("No valid selections available!")
    selection_keys = list(selections[0].keys())
    # Check if lengths match to gracefully exit before other errors
    if len(selection_keys) != len(header_names):
        raise KeyError(
            "The number of keys in the selection header "
            f"({len(header_names)}) doesn't match the number of keys "
            f"in the file dictionary ({len(selection_keys)})!"
        )
    # Match the subkeys from the file dict to the selection header dict.
    header_map = {}
    for i in range(len(selection_keys)):
        header_map[selection_keys[i]] = header_names[i]
    return header_map

def select_file(
        file_type: str='*',
        file_path: Path=Path('.'),
        **kwargs: Any
    ) -> str:
    """
    Directly returns the selected file of a specified file_type from a
    directory. Command Line Interface.

    :param file_type:  The file type to find in glob format ie '*.txt'.
        Defaults to all files.
    :param file_path: The directory to search, default current
        directory.
    :param **kwargs: Keyword arguments passed to select_item()
    :return: The selected file.
    """
    # Give more readable names to the header row, make sure they match
    # contextually to not confuse users (ie. 'File Name'
    # indeed has file names listed under it in the selections list).
    selection_header = ['File Name', 'Size', 'Modified Date', 'Path']
    # This helper functions is just for cli and calls other modular
    # functions.
    file_list = get_file_list(file_type, file_path)
    # Do a little extra to check for file name mistype.
    if file_list is not None:
        selection_header = build_header(file_list, selection_header)
        return select_item(file_list, selection_header, **kwargs)
    # Error text to display
    etext = f"No {file_type} found in {file_path}!"
    # If the file type was anything, it ain't here.
    if file_type == '*':
        print(format(etext, 'red'))
        if not ask_yesno("Check subfolders for files?"):
            raise FileNotFoundError(etext)
        return select_file(file_path=file_path, recurs=True, **kwargs)
    # Otherwise give a second try with anything for the file type.
    else:
        print(format(etext, 'red'))
        if not ask_yesno("Check for *any* files?"):
            raise FileNotFoundError(etext)
        return select_file(file_path=file_path, **kwargs)  
    

def quit(keyed: bool = False) -> None:
    print(format(f"\nSee you later!\n", 'blue'))
    if keyed:
        input(format("Press ENTER to exit...", 'cyan'))
    sys.exit()