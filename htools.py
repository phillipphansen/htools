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
    {"name": "Simple-Combine Files"},   # 0
    {"name": "Read-in Case Files"},     # 1
    {"name": "Read-in Geo-files"},      # 2
    {"name": "Normalize place names"},  # 3
    {"name": "Enrich with place location data"},    # 4
    {"name": "Enrich with county location data"},   # 5
    {"name": "Combine enriched case files"},        # 6
    {"name": "List loaded files"},      # 7
    {"name": "List file header"},       # 8
    {"name": "Write-out File"}          #9
]
islands = {
    "GU": {"INTPTLAT": "13.3824", "INTPTLONG": "144.6973"},
    "VI": {"INTPTLAT": "18.3358", "INTPTLONG": "-64.8963"},
    "AS": {"INTPTLAT": "-14.2710", "INTPTLONG": "-170.1322"},
    "MP": {"INTPTLAT": "16.70", "INTPTLONG": "145.78"}
}
place_names = ["CDP", "city", "town", "village", "borough", "zona",
                "urbana", "(balance)", "and", "government", "unified",
                "county", "consolidated", "urban", "metro", "comunidad",
                "municipality", "County"]
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
    "Virgin Islands": "VI"
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
    frames = {}
    try:
        while True:
            choice = cu.select_item(main_menu, return_key="_index_")
            if choice == "0":
                if not frames:
                    pu.combine_simple()
                else:
                    print(frames)
            elif choice == "1":
                delimiter = ','
                file_dict, file_name = su.read_to_dict(delim=delimiter)
                key_list = list(file_dict.keys())
                # if delimiter == '|':
                #     for key in key_list:
                #         file_dict[key] = clean_placenames(file_dict[key])
                if key_list[0] in list(states.keys()):
                    new_dict = {}
                    for key in key_list:
                        new_key = states[key]
                        new_dict[new_key] = file_dict[key]
                    file_dict = new_dict
                    key_list = list(file_dict.keys())
                # for key in key_list:
                #     print(key)
                #     print(len(file_dict[key]))
                frames[file_name] = file_dict
            elif choice == "2":
                delimiter = '|'
                file_dict, file_name = su.read_to_dict(delim=delimiter)
                key_list = list(file_dict.keys())
                # for key in key_list:
                #     print(key)
                #     print(len(file_dict[key]))
                frames[file_name] = file_dict
            elif choice == "3":
                file = cu.select_item_simple(list(frames.keys()), return_index=False)
                key_list = list(frames[file].keys())
                for key in key_list:
                    frames[file][key] = clean_placenames(frames[file][key])
            elif choice == "4":
                print("Select the Places Geo file to enrich with:")
                geo_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                geo_dict = frames[geo_file]
                print("Select the case file to be enriched:")
                case_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                case_dict = frames[case_file]
                tot_fixes = 0
                tot_items = 0
                for state in case_dict.keys():
                    st_fixes = 0
                    st_total = 0
                    for i, row in enumerate(case_dict[state]):
                        if state in islands.keys():
                            row["INTPTLAT_City"] = islands[state]["INTPTLAT"]
                            row["INTPTLONG_City"] = islands[state]["INTPTLONG"]
                            # print(f"Added ({row["INTPTLAT_City"]}, {row["INTPTLONG_City"]}) for Row {i}")
                            st_fixes += 1
                            st_total += 1
                            continue
                        no_match = True
                        for place in geo_dict[state]:
                            if place["NAME"] == row["City"]:
                                row["INTPTLAT_City"] = place["INTPTLAT"]
                                row["INTPTLONG_City"] = place["INTPTLONG"]
                                # print(f"Added ({row["INTPTLAT_City"]}, {row["INTPTLONG_City"]}) for {row["City"]}")
                                no_match = False
                                st_fixes += 1
                                break
                        if no_match:
                            row["INTPTLAT_City"] = None
                            row["INTPTLONG_City"] = None
                            # print(f"No lat/lons added for {row["City"]}!")
                        case_dict[state][i] = row
                        st_total += 1
                    tot_fixes += st_fixes
                    tot_items += st_total
                    percent = round((st_fixes / st_total) * 100)
                    print(f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.")
                tot_per = round((tot_fixes / tot_items) * 100)
                print(f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for Places.")
                frames[case_file] = case_dict
            elif choice == "5":
                print("Select the Counties Geo file to enrich with:")
                geo_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                geo_dict = frames[geo_file]
                print("Select the case file to be enriched:")
                case_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                case_dict = frames[case_file]
                tot_fixes = 0
                tot_items = 0
                for state in case_dict.keys():
                    st_fixes = 0
                    st_total = 0
                    for i, row in enumerate(case_dict[state]):
                        if state in islands.keys():
                            row["INTPTLAT_County"] = islands[state]["INTPTLAT"]
                            row["INTPTLONG_County"] = islands[state]["INTPTLONG"]
                            st_fixes += 1
                            st_total += 1
                            continue
                        no_match = True
                        for county in geo_dict[state]:
                            if county["NAME"] == row["County"]:
                                row["INTPTLAT_County"] = county["INTPTLAT"]
                                row["INTPTLONG_County"] = county["INTPTLONG"]
                                no_match = False
                                st_fixes += 1
                                break
                        if no_match:
                            row["INTPTLAT_County"] = None
                            row["INTPTLONG_County"] = None
                            # print(f"No lat/lons added for {row["County"]}!")
                        case_dict[state][i] = row
                        st_total += 1
                    tot_fixes += st_fixes
                    tot_items += st_total
                    percent = round((st_fixes / st_total) * 100)
                    print(f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.")
                tot_per = round((tot_fixes / tot_items) * 100)
                print(f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for Counties.")
                frames[case_file] = case_dict
            elif choice == "7":
                print("Files loaded:")
                for key in frames.keys():
                    print(key)
            elif choice == "8":
                # frames[file][state] = List[dict[str, str]]
                file = cu.select_item_simple(list(frames.keys()), return_index=False)
                first_state = list(frames[file].keys())[0]
                first_row = frames[file][first_state][0]
                for key, value in first_row.items():
                    print(key, value)
            elif choice == "9":
                # TODO: write a csv writer script :(
                pass
            else:
                print("I don't know that command yet.\n")
    
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
