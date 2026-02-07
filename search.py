"""
Contains functions for searching in dataframes.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import numpy as np
import pandas as pd
import geopandas as gp
import operator as op

# =[ Global Variables ]========================================================
# Used to store search selections based on data types.
search_types = {
    'num': [
        {'operator': 'result > x', 'name' : 'Greater Than'},
        {'operator': 'result >= x', 'name' : 'Greater Than or Equal To'},
        {'operator': 'result == x', 'name' : 'Equal To'},
        {'operator': 'result != x', 'name': 'Not Equal To'},
        {'operator': 'result <= x', 'name' : 'Less Than or Equal To'},
        {'operator': 'result < x', 'name' : 'Less Than'},
        {'operator': 'x < result < y', 'name': 'Between (exclusive)'},
        {'operator': 'x <= result <= y', 'name': 'Between (inclusive)'}
    ],
    'bool': [
        {'operator': 'True', 'name': 'The column is True'},
        {'operator': 'False', 'name': 'The column is False'}
    ],
    'str': [
        {'operator': 'in', 'name': 'The column includes the text'},
        {'operator': 'not in', 'name': 'The column does NOT include the text'},
        {'operator': 'exactly', 'name': 'The column exactly matches the text'}
    ]
}
# Maps operations to the operators in the selected num-type search
operator_map = {
    '>': op.gt,
    '>=': op.ge,
    '==': op.eq,
    '!=': op.ne,
    '<=': op.le,
    '<': op.lt,
    'in': lambda series, term: series.str.contains(
        term,
        case=False,
        na=False
    ),
    'not in': lambda series, term: ~series.str.contains(
        term,
        case=False,
        na=False
    ),
    'exactly': lambda series, term: series.str.lower() == term.lower()
}

# =[ Functions ]===============================================================
def search_list_builder_cli(df: gp.GeoDataFrame) -> list[dict[str, str]]:
    """
    Builds the list of searches to narrow the dataframe.
    
    :param df: The dataframe to search in
    :type df: gp.GeoDataFrame
    :return: The FIFO list of searches to perform.
    :rtype: list[dict[str, str]]
    """
    search_list = []
    add_term = True
    while True:
        # Show the list of searches to perform to the user
        if search_list:
            print("\nCurrently searching for (in this order):")
            # Enumerate to show the user the search order clearly
            for i, search in enumerate(search_list, start=1):
                # Display the first key, value pair, the rest of the
                # dictionary data is for internal use.
                if 'in' in search['type']:
                    text = ""
                else:
                    text = "in "
                print(
                    f"{i} {cu.format(search['term'], c='green')} {text}column "
                    f"{cu.format(search['col'], c='green')}."
                )
            print()
            add_term = cu.ask_yesno(
                "Would you like to add another search term?"
            )
        # User chose to add term, or first run.
        if add_term:
            # Have the user select the search column.
            print("\nSelect the column to search in:\n")
            search_column = cu.select_df_key_col_cli(df)
            print()
            # Have the user input a search term, based on the column
            # data type.
            data_type = df[search_column].dtype.type
            # Initialize the search with column
            search = {'col': search_column}
            # Search will be against numerical data.
            if data_type in [float, int, np.integer, np.float64]:
                print(
                    f"The {cu.format(search_column, c='green')} column"
                    " contains data in numerical format and will be searched"
                    " as a number."
                )
                # Show the user options for searching numbers.
                search_style  = select_item_cli(search_types['num'])
                # All the simple operators are len 1 or 2, look for
                # users selecting the 'Between' options
                if search_style[-1] == 'y':
                    # Get the lower bound number
                    low_num = input (
                        "Enter the low number (x) to bound your "
                        f"{cu.format(search_style, c='green')}"
                        " search in the "
                        f"{cu.format(search_column, c='green')}"
                        " column: "
                    )
                    # Replace 'x' with the low bound.
                    search_style = search_style.replace('x', low_num)
                    # Get the higher bound number
                    high_num = input (
                        "Enter the high number (y) to bound your "
                        f"{cu.format(search_style, c='green')}"
                        " search in the "
                        f"{cu.format(search_column, c='green')}"
                        " column: "
                    )
                    # Replace 'y' with the high bound assign to
                    # search_term to add to the search dict.
                    search_term = search_style.replace('y', high_num)
                # A simple operator was selected
                else:
                    # Get the number
                    search_num = input(
                        "Enter the number (x) for your "
                        f"{cu.format(search_style, c='green')}"
                        " search in the "
                        f"{cu.format(search_column, c='green')}"
                        " column: "
                    )
                    # Assign the operator and number to search term.
                    search_term = search_style.replace('x', search_num)
                # Add the search term to the search dictionary.
                search['term'] = search_term
                # Add the search type to the search dictionary.
                search['type'] = 'num'
            # Search will be against boolean data.
            elif data_type in [bool, np.bool]:
                print(
                    f"The {cu.format(search_column, c='green')} column"
                    " contains data in boolean (True or False) format and will"
                    " be searched as a boolean."
                )
                # Have user pick True or False
                search_term = select_item_cli(search_types['bool'])
                search['term'] = search_term
                search['type'] = 'bool'
            # Search will be against string data.
            else:
                print(
                    f"The {cu.format(search_column, c='green')} column"
                    " contains data in text format and will be searched as"
                    " text (case-insensitive).\nAND/OR logic is supported by"
                    f" typing either {cu.format("and", c='green')} or"
                    f" {cu.format("or", c='green')} between terms."
                )
                search_style = select_item_cli(search_types['str'])
                # Hide the extra in for 'in' and 'not in' searches
                if 'in' in search_style:
                    text = ""
                else:
                    text = "in "
                search_text = input(
                    "Enter what to search "
                    f"{cu.format(search_style, c='green')} {text}the "
                    f"{cu.format(search_column, c='green')} column: "
                )
                # Logic to look for or/and logic in searches
                if " or " in search_text.lower():
                    # Split the terms on the ' or '
                    terms = search_text.lower().split(" or ")
                    # Rejoin the terms highlighting 'or' to show it was
                    # detected. This will be used to detect the 'or'
                    # search in the search function.
                    search_text = (" *OR* ").join(terms)
                # Same deal for 'and', elif to avoid combined or/and.
                # I might do that later but not right now!
                elif " and " in search_text.lower():
                    terms = search_text.lower().split(" and ")
                    search_text = (" *AND* ").join(terms)   
                search_term = f"'{search_text}' {search_style}"
                search['term'] = search_term
                search['type'] = f"str.{search_style}"
            # Append the search to the search list.
            search_list.append(search)
        else:
            break
    return search_list

def search_df(
        df: gp.GeoDataFrame,
        search_list: list[dict[str, str]]
    ) -> gp.GeoDataFrame:
    """
    Recursively iterates through a search list to narrow a dataframe.
    
    :param df: The dataframe to be narrowed.
    :type df: gp.GeoDataFrame
    :param search_list: The search list to execute.
    :type search_list: list[dict[str, str]]
    :return: The narrowed dataframe.
    :rtype: GeoDataFrame
    """
    # Check for empty list.
    if not search_list:
        raise ValueError("There are no searches in the search list!")
        # Pull the first item from the list.
    search = search_list[0]
    col = search['col']
    term = search['term']
    stype = search['type']
    if 'in' in search['type']:
        text = ""
    else:
        text = "in "
    search_text = (f"{term} {text}column {col}")
    print(
        cu.format(f"Searching {len(df)} items for {search_text}", c='yellow'),
        end="...",
        flush=True
    )
    # Check the type of search, number search.
    if stype == 'num':
        # Extract the operator and number into a list
        term_parts = term.split(' ')
        # If it is a simple operator the len of the list will be 2.
        if len(term_parts) == 3:
            operator = operator_map[term_parts[1]]
            num = float(term_parts[-1])
            result = operator(df[col], num)
            df = df[result]
        # It is a Between operation
        else:
            # The low bound will the the first item in term_parts list
            low = float(term_parts[0])
            # The operators will match, only need one
            operator = operator_map[term_parts[1]]
            # The high bound will be the last item
            high = float(term_parts[-1])
            # Check for less than vs less than or equal for inclusivity.
            if operator == op.lt:
                df = df[df[col].between(low, high, inclusive='neither')]
            else:
                df = df[df[col].between(low, high)]
    # Boolean search.
    elif stype == 'bool':
        # Convert the string term to a boolean
        term = True if term == 'True' else False
        if term:
            df = df[df[col]]
        else:
            df = df[~df[col]]
    # String search.
    else:
        # For strings, the term format is "'search term' operator"
        # Split on ' and get the middle item.
        term = term.split("'")[1]
        # And the search type format is 'str.operator'.
        stype = stype.split('.')[-1]
        operator = operator_map[stype]
        # This logic is for processing AND and OR logic in searches.
        # If this is a 'not in' search, read the else comments first.
        if stype == 'not in':
            if '*OR*' in term:
                term_list = term.split(" *OR* ")
                # For 'not in' note that the .any() and .all() are
                # swapped for OR and AND searches!
                mask = pd.concat(
                    [operator(df[col], t) for t in term_list],
                    axis=1
                ).all(axis=1)
                df = df[mask]
            elif '*AND*' in term:
                term_list = term.split(" *AND* ")
                mask = pd.concat(
                    [operator(df[col], t) for t in term_list],
                    axis=1
                ).any(axis=1)
                df = df[mask]
            else:
                df = df[operator(df[col], term)]
        # This is an 'in' or 'exactly' search, same logic
        else:
            # If this is an 'or' search.
            if '*OR*' in term:
                # Separate out the terms.
                term_list = term.split(" *OR* ")
                # Create a data mask with or terms selected against the
                # columns, returning the ROW truth list (axis=1), then
                # .any() of those, again axis=1.
                mask = pd.concat(
                    [operator(df[col], t) for t in term_list],
                    axis=1
                ).any(axis=1)
                # Save the mask applied data frame as the new dataframe.
                df = df[mask]
            # This is an 'and' search.
            elif '*AND*' in term:
                term_list = term.split(" *AND* ")
                mask = pd.concat(
                    [operator(df[col], t) for t in term_list],
                    axis=1
                ).all(axis=1)
                df = df[mask]
            # This is a single term/phrase search
            else:
                df = df[operator(df[col], term)]
    # Recursively go on to the next search, narrowing the dataframe
    # results by FIFO searches.
    if len(search_list) > 1:
        print(cu.format("done!", c='yellow'))
        df = search_df(df, search_list[1:])
    # Reset the index to the new results, drop the original index col.
    df = df.reset_index(drop=True)
    # Make the index 1-based
    df.index = range(1, len(df) + 1)
    # Return the sesults of the dataframe search narrowing.
    return df
