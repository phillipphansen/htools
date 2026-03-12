"""
This is an importable helper file for working with various data files. It uses 
built-in modules. CLI based.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
from collections.abc import Iterable
import csv
import json
from pathlib import Path

# =[ Global variables ]========================================================

# =[ Function definitions ]====================================================
def _iter_csv_reader(
        file_name: str,
        delim: str = ',',
        encoding: str = 'utf-8',
        key_col: str | None = None,
        sec_col: str | None = None
    ) -> Iterable[dict[str, str]]:
    """
    This is an iterator function to allow the two different read-in functions
    to efficiently readin a csv file.

    :param file_name: The name of the file to read
    :type file_name: str
    :param delim: The delimiter to read in the file with. Default comma (,).
    :type delim: str, optional
    :param key_col: The column name to be used a the primary key for the dict.
        Default None, the user will select from a list of columns present.
    :type key_col: str | None, optional
    :return: The next row of the read-in iterator
    :rtype: Iterable[dict[str, str]]
    :raises ValueError: No header row in the file, or passed key_col not found
        present column names.
    """
    # Open the file
    with open(file_name, newline='', encoding=encoding) as csvfile:
        # Create the reader iterable.
        reader = csv.DictReader(csvfile, delimiter=delim)
        # Check for a missing header row.
        if reader.fieldnames is None:
            raise ValueError(f"{file_name} has no header!")
        col_keys = reader.fieldnames
        # Check if a key column was passed.
        # TODO: Add logic to check for secondary grouping.
        if key_col is None:
            # The error message will allow users to select a key column.
            error_msg = (
                "\nPlease type in one of the columns present to use as the "
                f"dictionary key:\n{col_keys}"
            )
            raise ValueError(error_msg)
        # Check if the passed key_col is actually in the list of columns.
        if key_col not in col_keys:
            # The error message will allow users to select a new key column.
            error_msg = (
                f"\n'{key_col}' column not found in {file_name}! Please use "
                f"one of these columns present:\n{col_keys}"
            )
            raise ValueError(error_msg)
        # Yield to allow iteration from the reader
        yield from reader

def read_to_grouped_dict(
        file_name: str,
        delim: str = ',',
        encoding: str = 'utf-8',
        key_col: str | None = None
    ) -> dict[str, list[dict[str, str]]]:
    """
    Creates a grouped dictionary keyed by the passed key column name.

    :param file_name: The name of the file to read in.
    :type file_name: str
    :param delim: The delimiter used in the file. Default comma (,)
    :type delim: str, optional
    :param key_col: The name of the column to use as group keys. Default None, 
        the user will get the opportunity to select.
    :type key_col: str | None, optional
    :return: The grouped dictionary from the file.
    :rtype: dict[str, list[dict[str, str]]]
    """
    file_dict = {}
    prime_keys = []
    for row in _iter_csv_reader(file_name, delim, encoding, key_col):
        # This is guaranteed from the _iter_csv_reader function, but shuts the
        # type checker up.
        assert key_col is not None
        prime_key = row[key_col]
        # NOTE: Is the below needed anymore? Where used?
        if prime_key not in prime_keys:
            prime_keys.append(prime_key)
            file_dict[prime_key] = []
        file_dict[prime_key].append(row)
    return file_dict

def read_to_double_grouped_dict(
        file_name: str,
        delim: str = ',',
        encoding: str = 'utf-8',
        key_col: str | None = None,
        sec_col: str | None = None
    ) -> dict[str, dict[str, list[dict[str, str]]]]:
    file_dict = {}
    found_keys = {}
    for row in _iter_csv_reader(file_name, delim, encoding, key_col):
        # This is guaranteed from the _iter_csv_reader function, but shuts the
        # type checker up.
        assert key_col is not None
        prime_key = row[key_col]
        sec_key = row[sec_col]
        if prime_key not in found_keys:
            found_keys[prime_key] = []
            file_dict[prime_key] = {}
        if sec_key not in found_keys[prime_key]:
            found_keys[prime_key].append(sec_key)
            file_dict[prime_key][sec_key] = []
        file_dict[prime_key][sec_key].append(row)
    return file_dict

def read_to_indexed_dict(
        file_name: str,
        delim: str = ',',
        encoding: str = 'utf-8',
        key_col: str | None = None,
    ) -> dict[str, dict[str, str]]:
    file_dict = {}
    for row in _iter_csv_reader(file_name, delim, encoding, key_col):
        # This is guaranteed from the _iter_csv_reader function, but shuts the
        # type checker up.
        assert key_col is not None
        file_dict[row[key_col]] = row
    return file_dict
   
def write_csv(out_dict: dict[str, list[dict[str, str]]], out_name: str) -> None:
    out_file_name = Path(out_name)
    first_rows = next(iter(out_dict.values()))
    first_row = first_rows[0]
    field_names = list(first_row.keys())
    with out_file_name.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for keys, values in out_dict.items():
            for value in values:
                writer.writerow(value)

def write_json(out_dict: dict[str, list[dict[str, str]]], out_name: str) -> None:
    """
    Docstring for write_json
    
    :param out_dict: Description
    :type out_dict: dict[str, list[dict[str, str]]]
    """
    out_file_name = Path(out_name)
    flat_cases = [case for cases in out_dict.values() for case in cases]
    with out_file_name.open("w", encoding="utf-8") as f:
        json.dump(flat_cases, f, indent=2, ensure_ascii=False)
    # TODO: Write .json writer
    pass
