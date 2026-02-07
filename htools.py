"""
This is an importable helper file for working with various data files. It uses 
panda, geopandas, numpy, etc. CLI based.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import pandas_utils as pu
import std_utils as su
import sys

# =[ Global variables ]========================================================
main_menu = [
    {"name": "Simple-Combine Files"},
    {"name": "Advanced-Combine Files"},
    {"name": "Remove words from column"}
]
place_names = ["CDP", "city", "town", "village", "borough", "zona",
                   "urbana", "(balance)", "and", "government", "unified",
                   "county", "consolidated", "urban", "metro", "comunidad",
                   "municipality"]
key_fields = ["USPS", "State"]
states = {
    "Alabama": "AL",
    "Alaska": "AK",
    "Arizona": "AZ",
    "Arkansas": "AR",
    "California": "CA",
    "Colorado": "CO",
    "Connecticut": "CT",
    "Delaware": "DE",
    "Florida": "FL",
    "Georgia": "GA",
    "Hawaii": "HI",
    "Idaho": "ID",
    "Illinois": "IL",
    "Indiana": "IN",
    "Iowa": "IA",
    "Kansas": "KS",
    "Kentucky": "KY",
    "Louisiana": "LA",
    "Maine": "ME",
    "Maryland": "MD",
    "Massachusetts": "MA",
    "Michigan": "MI",
    "Minnesota": "MN",
    "Mississippi": "MS",
    "Missouri": "MO",
    "Montana": "MT",
    "Nebraska": "NE",
    "Nevada": "NV",
    "New Hampshire": "NH",
    "New Jersey": "NJ",
    "New Mexico": "NM",
    "New York": "NY",
    "North Carolina": "NC",
    "North Dakota": "ND",
    "Ohio": "OH",
    "Oklahoma": "OK",
    "Oregon": "OR",
    "Pennsylvania": "PA",
    "Rhode Island": "RI",
    "South Carolina": "SC",
    "South Dakota": "SD",
    "Tennessee": "TN",
    "Texas": "TX",
    "Utah": "UT",
    "Vermont": "VT",
    "Virginia": "VA",
    "Washington": "WA",
    "West Virginia": "WV",
    "Wisconsin": "WI",
    "Wyoming": "WY",

    # District
    "District of Columbia": "DC",

    # Territories
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "U.S. Virgin Islands": "VI"
}

# =[ Function definitions ]====================================================
def clean_placenames(place_list: list[dict[str, str]]) -> list[dict[str, str]]:
    while True:
        corrections = 0
        for i, place in enumerate(place_list):
            corrected = False
            key_list = list(place.keys())
            if "NAME" not in key_list:
                raise KeyError("NAME key not found!")
            name_breakout = place["NAME"].split(' ')
            for name in place_names:
                if name == name_breakout[-1]:
                    new_name = ' '.join(name_breakout[:-1])
                    corrected = True
                    break
            if corrected:                
                place["NAME"] = new_name
                place_list[i] = place
                corrections += 1
        if corrections == 0:
            return place_list

# =[ Main Fuction ]============================================================
def main():
    print(cu.format("\nFile Combiner. Good luck.\n", 'cyan'))
    # Try/except block for all user inputs
    frames = []
    try:
        while True:
            choice = cu.select_item(main_menu, return_key="_index_")
            if choice == "0":
                if not frames:
                    pu.combine_simple()
                else:
                    print(frames)
            elif choice == "1":
                delimiter = input("Enter the delimiter: ")
                file_dict = su.read_to_dict(delim=delimiter)
                key_list = list(file_dict.keys())
                if delimiter == '|':
                    for key in key_list:
                        file_dict[key] = clean_placenames(file_dict[key])
                for key in key_list:
                    print(key)
                    print(len(file_dict[key]))
                frames.append(file_dict)
            elif choice == "2":
                pass
            else:
                print("I don't know that command yet.")
    
    except cu.UserQuitException:
        print(cu.format(f"\nSee you later!\n", 'blue'))
        input(cu.format("Press ENTER to exit...", 'cyan'))
        sys.exit()
    # except FileNotFoundError as e:
    #     print(cu.format(f"File Error: {e}", 'red'))
    #     input(cu.format("Press ENTER to exit...", 'cyan'))
    #     sys.exit()
    # except ValueError as e:
    #     print(cu.format(f"Value Error: {e}", 'red'))
    #     input(cu.format("Press ENTER to exit...", 'cyan'))
    #     sys.exit()
    # except KeyError as e:
    #     print(cu.format(f"Key Error: {e}", 'red'))
    #     input(cu.format("Press ENTER to exit...", 'cyan'))
    #     sys.exit()
    
if __name__ == "__main__":
    main()
