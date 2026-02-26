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
        key_col: str | None = None
    ) -> Iterable[dict[str, str]]:
    with open(file_name, newline='') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=delim)
        if reader.fieldnames is None:
            raise ValueError(f"{file_name} has no header!")
        col_keys = reader.fieldnames
        if key_col is None:
            error_msg = (
                "\nPlease type in one of the columns present to use as the "
                f"dictionary key:\n{col_keys}"
            )
            raise ValueError(error_msg)
        if key_col not in col_keys:
            error_msg = (
                f"\n'{key_col}' column not found in {file_name}! Please use "
                f"one of these columns present:\n{col_keys}"
            )
            raise ValueError(error_msg)
        yield from reader

def read_to_grouped_dict(
        file_name: str,
        delim: str = ',',
        key_col: str | None = None
    ) -> dict[str, list[dict[str, str]]]:
    file_dict = {}
    prime_keys = []
    for row in _iter_csv_reader(file_name, delim, key_col):
        # This is guaranteed from the _iter_csv_reader function, but shuts the
        # type checker up.
        assert key_col is not None
        prime_key = row[key_col]
        if prime_key not in prime_keys:
            prime_keys.append(prime_key)
            file_dict[prime_key] = []
        file_dict[prime_key].append(row)
    return file_dict

def read_to_indexed_dict(
        file_name: str,
        delim: str = ',',
        key_col: str | None = None,
    ) -> dict[str, dict[str, str]]:
    file_dict = {}
    for row in _iter_csv_reader(file_name, delim, key_col):
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
