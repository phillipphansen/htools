"""
This is an importable helper file for working with various data files. It uses 
built-in modules. CLI based.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import csv

# =[ Global variables ]========================================================

# =[ Function definitions ]====================================================

def read_to_dict(
        delim: str | None = None,
        prime: str | None = None
    ) -> dict[str, list[dict[str, str]]]:
    file_path = cu.Path(input("Enter a file path to search in: "))
    file_name = input(f"Enter a file to search for in {file_path}: ")
    file = cu.select_file(file_name, file_path)
    file_dict = {}
    print(cu.format(f"Reading {file}...", "yellow"), end="", flush=True)
    with open(file, newline='') as csvfile:
        if delim is not None:
            reader = csv.DictReader(csvfile, delimiter=delim)
        else:
            reader = csv.DictReader(csvfile)
        if reader.fieldnames is None:
            raise ValueError("File has no header!")
        col_keys = list(reader.fieldnames)
        if prime in col_keys:
            prime_col = col_keys.index(prime)
        else:
            print()
            prime_col = int(cu.select_item_simple(col_keys))
        prime_keys = []
        for row in reader:
            prime_key = list(row.values())[prime_col]
            if prime_key not in prime_keys:
                prime_keys.append(prime_key)
                file_dict[prime_key] = []
            file_dict[prime_key].append(row)
    print(cu.format("Done!", "yellow"))
    return file_dict