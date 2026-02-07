"""
This is an importable helper file for working with various data files. It uses 
panda, geopandas, numpy, etc. CLI based.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import pandas as pd
import geopandas as gp
import re

# =[ Global variables ]========================================================

# =[ Function definitions ]====================================================
def combine_simple() -> None:
    df_list = []
    read_file_list = []
    file_path = cu.Path(input("Enter a file path to search in: "))
    file_name = input(f"Enter a file to search for in {file_path}: ")
    while True:
        file = cu.select_file(file_name, file_path)
        print(cu.format(f"Reading {file}...", "yellow"), end="", flush=True)
        file_type = str(file)[-3:]
        if file_type == 'txt':
            df = pd.read_csv(file, delimiter="|")
        elif file_type == 'csv':
            df = pd.read_csv(file, index_col=None, header=0)
        else:
            print(cu.format(
                f"I'm not sure how to read a '{file_type}' file yet...",
                "red"
            ))
            continue
        print(cu.format("Done!", "yellow"))
        read_file_list.append(file)
        df_list.append(df)
        print(f"{len(read_file_list)} files will be combined: ")
        for i, file in enumerate(read_file_list, start=1):
            print(i, file)
            
        if not cu.ask_yesno("Select another file?"):
            break
    print(cu.format(f"Combining {len(df_list)} files...", "yellow"), end="", flush=True)
    combined_df = pd.concat(df_list, axis=0, ignore_index=True)
    print(cu.format("Done!", "yellow"))
    save_name = input("Enter a name to give the new file: ") + "." + file_type
    print(cu.format(f"Saving {save_name}...", "yellow"), end="", flush=True)
    combined_df.to_csv(save_name, index=False)
    print(cu.format("Done!", "yellow"))

def get_df_headrow(
        df: pd.DataFrame | gp.GeoDataFrame
    ) -> list[dict[str, str]]:
    """
    Gets the column names and first row values from a dataframe. 1-based
    int keyed dict for user selection mapping later.
    
    :param df: The dataframe to get the header from
    :return: The list of the column names and first row values
    """
    # Get the data values for the dataframes first row.
    first_row = df.head(1).iloc[0]
    header_names = []
    # Gets all column names from the dataframe and iterates through them
    for col in df.columns:
        # Add the column name and value of the first row to the dict
        header_names.append({
            'name': col,
            'value': str(first_row[col])
        })
    return header_names

def select_df_key_col(
        df: pd.DataFrame | gp.GeoDataFrame,
        **kwargs: cu.Any
    ) -> str:
    """
    Allows the user to select a column to key a dataframe with.
    
    :param df: The dataframe to select columns from.
    :param **kwargs: Keyword parameters to pass to select_item()
    :return: The selected column name.
    """
    # Dictionary map for a more readable selection header for the user.
    df_header_map = ['Column Name', 'First Row Value']
    df_headrow = get_df_headrow(df)
    df_header_map = cu.build_header(df_headrow, df_header_map)
    key = cu.select_item(df_headrow, df_header_map, **kwargs)
    return key

def find_match_col_auto(
        df: pd.DataFrame,
        reg_ex: re.Pattern,
        deep: bool=False
    ) -> str | None:
    """
    Attempts to find a column that matches a given regular expression
    pattern. Returns None for no matches.

    :param df: The dataframe to check columns in.
    :param reg_ex: The regual expression pattern to look for.
    :param deep: Whether to search all data or just the first row.
        Default to False, just the first row.
    :return: The column name that matches the pattern. Returns None if
        there are no matches.
    """
    # Looping through all the columns in the dataframe
    for col in df.columns:
        # Not consistent data, see if some of the data matches
        if deep:
            # A sum of the number of rows that match the pattern
            num_match = df[col].astype(str).str.match(reg_ex).sum()
            # There was at least one
            if num_match > 0:
                return col
        # The data is consistent 
        else:
            # Just the first value for speed
            first_value = str(df[col].dropna().iloc[0])
            # Check against the passed reg ex pattern. 
            if re.match(reg_ex, first_value):
                return col
    # No match found
    return None

def check_auto_match(
        df: pd.DataFrame | gp.GeoDataFrame,
        regex: re.Pattern,
        file: str="",
        sought: str="",
        verify: bool=True,
        **kwargs: cu.Any
    ) -> str:
    """
    Checks for an automatch using regular expressions to a column in a
    DataFrame, asks the user for confirmation, or tells the user there
    was no match
    
    :param df: The Dataframe to check columns in.
    :param regex: The regular expression to match against
    :param file: File name being searched, to give information to the
        user. Defaults to empty string.onal
    :param sought: The name of data being sought, to give information to the
        user. Defaults to empty string.
    :param verify: Whether or not to have the user to verify the match.
        Defaults to True.
    :param **kwargs: Keyword Args passed to find_match_col_auto()
    :return: The column name detected by the regex or the one selected
        by the user.
    """
    key = find_match_col_auto(df, regex, **kwargs)
    # Check for a match. Show the user what the auto match found.
    if sought:
        sought = f"{cu.format(sought, 'green')}"
    else:
        sought = "key"
    if key is not None:
        if file:
            file = f" in {file}"
        print(
            f"Automatically selected column {cu.format(key, 'green')}"
            f"{file} as the {sought} column."
        )
        # Double check with the user it was correct.
        if verify:
            print(
                "The first value in that column is "
                f"{cu.format(df[key].iloc[0], 'green')}.\n"
            )
            if not cu.ask_yesno():
                key = select_df_key_col(df, suggestion=key)
    # No auto match
    else:
        print(
            f"No matching {sought} column was automatically detected."
            " Please select one:\n"
        )
        # Have the user select the column manually
        key = select_df_key_col(df)
    return key
