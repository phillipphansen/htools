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
        *,
        delim: str | None = None,
        file_path: cu.Path = cu.Path('.'),
        file_name: str = "*",
        prime: str | None = None
    ) -> tuple[dict[str, list[dict[str, str]]], str]:
    # file_path = cu.Path(input("Enter a file path to search in: "))
    # file_name = input(f"Enter a file to search for in {file_path}: ")
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
        if prime not in col_keys:
            print(format("Primary key column not found! Please select one:"), "red")
            prime = cu.select_item_simple(col_keys, return_index=False)
        prime_keys = []
        for row in reader:
            prime_key = row[prime]
            if prime_key not in prime_keys:
                prime_keys.append(prime_key)
                file_dict[prime_key] = []
            file_dict[prime_key].append(row)
    print(cu.format("Done!", "yellow"))
    return file_dict, file

def write_csv(
        out_dict: dict[str, list[dict[str, str]]]
    ) -> None:
    out_file_name = cu.Path(input("Give the new file a name: "))
    print(cu.format(f"Writing {out_file_name}...", "yellow"), end="", flush=True)
    first_rows = next(iter(out_dict.values()))
    first_row = first_rows[0]
    field_names = list(first_row.keys())
    with out_file_name.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for keys, values in out_dict.items():
            for value in values:
                writer.writerow(value)
    print(cu.format("Done!", "yellow"))
