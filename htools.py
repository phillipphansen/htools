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
    "MP": {"INTPTLAT": "16.70", "INTPTLONG": "145.78"},
    "PR": {"INTPTLAT": "18.2208", "INTPTLONG": "-66.5901"}
}
place_names = ["CDP", "city", "town", "village", "borough", "zona",
                "urbana", "(balance)", "and", "government", "unified",
                "county", "consolidated", "urban", "metro", "comunidad",
                "municipality",]
county_names = ["County", "Parish", "Municipio", "CDP", "city", "town", "village", "borough", "zona",
                "urbana", "(balance)", "and", "government", "unified",
                "county", "consolidated", "urban", "metro", "comunidad",
                "municipality",]
ak_names = ["City", "and", "Borough", "Municipality", "Census", "Area"]
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
bad_states = ["NY", "ID", "AZ", "HI", "NH", "ME", "RI"]

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

def clean_countynames(
        county_list: list[dict[str, str]],
        state: str
    ) -> list[dict[str, str]]:
    if state == "AK":
        match_names = ak_names
    else:
        match_names = county_names
    while True:
        corrections = 0
        for i, place in enumerate(county_list):
            corrected = False
            key_list = list(place.keys())
            if "NAME" not in key_list:
                raise KeyError("NAME key not found!")
            name_breakout = place["NAME"].split(' ')
            for name in match_names:
                if name == name_breakout[-1]:
                    new_name = ' '.join(name_breakout[:-1])
                    corrected = True
                    break
            if corrected:                
                place["NAME"] = new_name
                county_list[i] = place
                corrections += 1
        if corrections == 0:
            return county_list
    
def clean_states(case_list: list[dict[str, str]]) -> list[dict[str, str]]:
    state_names = list(states.keys())
    for i, case in enumerate(case_list):
        if case["State"] in state_names:
            case["State"] = states[case["State"]]
        case_list[i] = case
    return case_list
        
def enrich_places(
        base: dict[str, list[dict[str, str]]],
        enrichment: dict[str, list[dict[str, str]]]
    ) -> dict[str, list[dict[str, str]]]:
    tot_fixes = 0
    tot_items = 0
    for state in base.keys():
        st_fixes = 0
        st_total = 0
        for i, row in enumerate(base[state]):
            st_total += 1
            if state in islands.keys() and state != "PR":
                row["INTPTLAT_City"] = islands[state]["INTPTLAT"]
                row["INTPTLONG_City"] = islands[state]["INTPTLONG"]
                st_fixes += 1
                continue
            no_match = True
            city_norm = row['City'].lower()
            for place in enrichment[state]:
                place_norm = str(place['NAME']).lower()
                if place_norm == city_norm or (place_norm in city_norm or city_norm in place_norm):
                    row["INTPTLAT_City"] = place["INTPTLAT"]
                    row["INTPTLONG_City"] = place["INTPTLONG"]
                    no_match = False
                    st_fixes += 1
                    break
            if no_match:
                # if state in bad_states and city_norm:
                #     print(f"No match found for {row['City']}")
                row["INTPTLAT_City"] = ""
                row["INTPTLONG_City"] = ""
            base[state][i] = row
        tot_fixes += st_fixes
        tot_items += st_total
        percent = round((st_fixes / st_total) * 100)
        if percent >= 90:
            color = "green"
        elif percent >= 70:
            color = "yellow"
        else:
            color = "red"
        print(cu.format(f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.", color))
    tot_per = round((tot_fixes / tot_items) * 100)
    print(f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for all Place data.")
    return base

def enrich_counties(
        base: dict[str, list[dict[str, str]]],
        enrichment: dict[str, list[dict[str, str]]]
    ) -> dict[str, list[dict[str, str]]]:
    tot_fixes = 0
    tot_items = 0
    for state in base.keys():
        st_fixes = 0
        st_total = 0
        for i, row in enumerate(base[state]):
            if state in islands.keys():
                row["INTPTLAT_County"] = islands[state]["INTPTLAT"]
                row["INTPTLONG_County"] = islands[state]["INTPTLONG"]
                st_fixes += 1
                st_total += 1
                continue
            no_match = True
            for county in enrichment[state]:
                if str(county["NAME"]).lower() == str(row["County"]).lower():
                    row["INTPTLAT_County"] = county["INTPTLAT"]
                    row["INTPTLONG_County"] = county["INTPTLONG"]
                    no_match = False
                    st_fixes += 1
                    break
            if no_match:
                row["INTPTLAT_County"] = ""
                row["INTPTLONG_County"] = ""
            base[state][i] = row
            st_total += 1
        tot_fixes += st_fixes
        tot_items += st_total
        percent = round((st_fixes / st_total) * 100)
        if percent >= 90:
            color = "green"
        elif percent >= 70:
            color = "yellow"
        else:
            color = "red"
        print(cu.format(f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.", color))
    tot_per = round((tot_fixes / tot_items) * 100)
    print(f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for all County data.")
    return base

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
                file_dict, file_name = su.read_to_dict(delim=',', file_name='*.csv')
                key_list = list(file_dict.keys())
                if key_list[0] in list(states.keys()):
                    new_dict = {}
                    for key in key_list:
                        new_key = states[key]
                        new_dict[new_key] = file_dict[key]
                    file_dict = new_dict
                    key_list = list(file_dict.keys())
                frames[file_name] = file_dict
            # Read-in Geo Files
            elif choice == "2":
                file_dict, file_name = su.read_to_dict(delim='|', file_name='*.txt')
                key_list = list(file_dict.keys())
                frames[file_name] = file_dict
            elif choice == "3":
                file = cu.select_item_simple(list(frames.keys()), return_index=False)
                key_list = list(frames[file].keys())
                sub_choice = cu.select_item_simple(["Places", "Counties", "Cases"])
                if sub_choice == "0":
                    for key in key_list:
                        frames[file][key] = clean_placenames(frames[file][key])
                elif sub_choice == "1":
                    for key in key_list:
                        frames[file][key] = clean_countynames(frames[file][key], key)
                elif sub_choice == "2":
                    for key in key_list:
                        frames[file][key] = clean_states(frames[file][key])
                    sorted_file = {}
                    state_codes = (states.values())
                    found_states = list(frames[file].keys())
                    for value in state_codes:
                        if value in found_states:
                            sorted_file[value] = frames[file][value]
                    frames[file] = sorted_file
            elif choice == "4":
                print("Select the Places Geo file to enrich with:")
                geo_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                geo_dict = frames[geo_file]
                print("Select the case file to be enriched:")
                case_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                case_dict = frames[case_file]
                frames[case_file] = enrich_places(case_dict, geo_dict)
            elif choice == "5":
                print("Select the Counties Geo file to enrich with:")
                geo_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                geo_dict = frames[geo_file]
                print("Select the case file to be enriched:")
                case_file = cu.select_item_simple(list(frames.keys()), return_index=False)
                case_dict = frames[case_file]
                frames[case_file] = enrich_counties(case_dict, geo_dict)
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
                print("Select the case file to be written:")
                file = cu.select_item_simple(list(frames.keys()), return_index=False)
                file_dict = frames[file]
                su.write_from_dict(file_dict)

            else:
                print("I don't know that command yet.\n")
    
    except cu.UserQuitException:
        print(cu.format(f"\nSee you later!\n", 'blue'))
        # input(cu.format("Press ENTER to exit...", 'cyan'))
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
