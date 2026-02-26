"""
This is an importable helper file for working with various data files. It uses 
panda, geopandas, numpy, etc. CLI based.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import std_utils as su

# =[ Global variables ]========================================================
main_menu = [
    {"name": "Read-in Case Files"},         # 0
    {"name": "Read-in Geo-files"},          # 1
    {"name": "Enrich with location data"},  # 2
    {"name": "Combine dataframes"},         # 3
    {"name": "List loaded files"},          # 4
    {"name": "List file header"},           # 5
    {"name": "Write-out File"}              # 6
]
place_filename = "2025_Gaz_place_national.txt"
county_filename = "2025_Gaz_counties_national.txt"
geo_column = "USPS"
case_filenames = ["namus_missing_v2.csv", "namus_unid.csv", "namus_unclaim.csv"]
case_column = "State"
islands = {
    "GU": {"INTPTLAT": "13.3824", "INTPTLONG": "144.6973"},
    "VI": {"INTPTLAT": "18.3358", "INTPTLONG": "-64.8963"},
    "AS": {"INTPTLAT": "-14.2710", "INTPTLONG": "-170.1322"},
    "MP": {"INTPTLAT": "16.70", "INTPTLONG": "145.78"},
    "PR": {"INTPTLAT": "18.2208", "INTPTLONG": "-66.5901"}
}
place_suffixes = ["CDP", "city", "town", "village", "borough", "zona",
                "urbana", "(balance)", "and", "government", "unified",
                "county", "consolidated", "urban", "metro", "comunidad",
                "municipality",]
county_suffixes = ["County", "Parish", "Municipio", "CDP", "city", "town",
                "village", "borough", "zona", "urbana", "(balance)", "and",
                "government", "unified", "county", "consolidated", "urban",
                "metro", "comunidad", "municipality",]
ak_county_suffixes = ["City", "and", "Borough", "Municipality", "Census", "Area"]
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

# =[ Class definitions ]=======================================================
class CaseRecord:
    case_number: str
    state: str
    date_last_contact: str
    last_name: str
    first_name: str
    missing_age: int
    
    pass


# =[ Type definitions ]========================================================
type CaseDict = dict[str, list[CaseRecord]]

# =[ Function definitions ]====================================================
def clean_placenames(place_list: dict[str,list[dict[str, str]]]) -> None:
    for state in place_list:
        while True:
            corrections = 0
            for place in place_list[state]:
                corrected = False
                if "NAME" not in place:
                    raise KeyError("NAME key not found!")
                name_breakout = place['NAME'].split(' ')
                # place_suffixes is a gloabl variable
                for name in place_suffixes:
                    if name == name_breakout[-1]:
                        new_name = ' '.join(name_breakout[:-1])
                        corrected = True
                        break
                if corrected:                
                    place['NAME'] = new_name
                    corrections += 1
            if corrections == 0:
                break

def clean_countynames(county_file: dict[str, list[dict[str, str]]]) -> None:
    for state in county_file:
        if state == "AK":
            # ak_county_suffixes is a global variable
            match_names = ak_county_suffixes
        else:
            # county_suffixes is a global variable
            match_names = county_suffixes
        while True:
            corrections = 0
            for place in county_file[state]:
                corrected = False
                if "NAME" not in place:
                    raise KeyError("NAME key not found!")
                name_breakout = place["NAME"].split(' ')
                for name in match_names:
                    if name == name_breakout[-1]:
                        new_name = ' '.join(name_breakout[:-1])
                        corrected = True
                        break
                if corrected:                
                    place["NAME"] = new_name
                    corrections += 1
            if corrections == 0:
                break
    
def clean_states(case_list: list[dict[str, str]]) -> None:
    """
    Docstring for clean_states
    
    :param case_list: Description
    :type case_list: list[dict[str, str]]
    """
    for case in case_list:
        if case["State"] in states:
            case["State"] = states[case["State"]]

def sort_case(
        case_file: dict[str, list[dict[str, str]]]
    ) -> dict[str, list[dict[str, str]]]:
    first_key = next(iter(case_file))
    if first_key in states:
        norm_dict = {}
        for key in case_file:
            norm_dict[states[key]] = case_file[key]
        case_file = norm_dict
    sorted_dict = {}
    for value in states.values():
        if value in case_file:
            sorted_dict[value] = case_file[value]
    return sorted_dict
        
def enrich_places(
        case_file: dict[str, list[dict[str, str]]],
        enrichment: dict[str, list[dict[str, str]]]
    ) -> None:
    tot_fixes = 0
    tot_items = 0
    for state in case_file:
        st_fixes = 0
        st_total = 0
        for row in case_file[state]:
            st_total += 1
            if state in islands and state != "PR":
                row["INTPTLAT_City"] = islands[state]["INTPTLAT"]
                row["INTPTLONG_City"] = islands[state]["INTPTLONG"]
                st_fixes += 1
                continue
            no_match = True
            city_norm = row['City'].lower()
            for place in enrichment[state]:
                place_norm = str(place['NAME']).lower()
                if place_norm == city_norm or (
                    place_norm in city_norm or city_norm in place_norm):
                    row["INTPTLAT_City"] = place["INTPTLAT"]
                    row["INTPTLONG_City"] = place["INTPTLONG"]
                    no_match = False
                    st_fixes += 1
                    break
            if no_match:
                row["INTPTLAT_City"] = ""
                row["INTPTLONG_City"] = ""
        tot_fixes += st_fixes
        tot_items += st_total
        percent = round((st_fixes / st_total) * 100)
        color = cu.grade_color(percent)
        print(cu.format(
            f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.",
            color
        ))
    tot_per = round((tot_fixes / tot_items) * 100)
    color = cu.grade_color(tot_per)
    print(cu.format(
        f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for all Place data.",
        color
    ))

def enrich_counties(
        case_file: dict[str, list[dict[str, str]]],
        enrichment: dict[str, list[dict[str, str]]]
    ) -> None:
    tot_fixes = 0
    tot_items = 0
    for state in case_file:
        st_fixes = 0
        st_total = 0
        for row in case_file[state]:
            if state in islands:
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
            st_total += 1
        tot_fixes += st_fixes
        tot_items += st_total
        percent = round((st_fixes / st_total) * 100)
        color = cu.grade_color(percent)
        print(cu.format(
            f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.", color
        ))
    tot_per = round((tot_fixes / tot_items) * 100)
    color = cu.grade_color(tot_per)
    print(cu.format(
        f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for all County data.",
        color
    ))

def read_file_auto(
        file_name: str,
        *,
        delim: str = ',',
        key_col: str | None = None
        ) -> dict[str, list[dict[str, str]]]:
    try:
        return su.read_to_grouped_dict(file_name, delim, key_col)
    except ValueError as e:
        print(cu.format(e, "red"))
        key_col = input("Enter the key column name: ")
        return su.read_to_grouped_dict(file_name, delim, key_col)

def combine_case_files(case_file_1: dict[str, list[dict[str, str]]]) -> None:

    pass

def manual_mode() -> None:
    case_files = {}
    place_dict = None
    county_dict = None
    while True:
        choice = cu.select_item(main_menu, return_key="_index_")
        if choice == "0":
            file_name = cu.select_file(file_type='*.csv')
            file_dict = su.read_to_grouped_dict(file_name, key_col='State')
            case_files[file_name] = sort_case(file_dict)
        # Read-in Geo Files
        elif choice == "1":
            print("What type of geo file will you be reading in?")
            sub_choice = cu.select_item_simple(["Places", "Counties"])
            file_name = cu.select_file(file_type='*.txt')
            file_dict = su.read_to_grouped_dict(
                file_name, key_col='USPS', delim='|'
            )
            # Places File
            if sub_choice == "0":
                clean_placenames(file_dict)
                place_dict = file_dict
                place_file_name = file_name
            # Counties File
            elif sub_choice == "1":
                clean_countynames(file_dict)
                county_dict = file_dict
                county_file_name = file_name
        elif choice == "2":
            if not place_dict or not county_dict:
                print(cu.format(
                    "No geo files loaded! Load a places file first!",
                    "red"
                ))
                continue
            print("Select the case file to be enriched:")
            case_file = cu.select_item_simple(case_files, return_index=False)
            enrich_places(case_files[case_file], place_dict)
            input("Places enriched, press ENTER to enrich counties...")
            enrich_counties(case_files[case_file], county_dict)
        elif choice == "3":
            # TODO: dictionary combination function
            pass
        elif choice == "4":
            print("Loaded files list:")
            if place_dict:
                print(f"{place_file_name} loaded as places dictionary")
            if county_dict:
                print(f"{county_file_name} loaded as counties dictionary")
            if case_files:
                print("Case files loaded:")
                for case in case_files:
                    print(case)
        elif choice == "5":
            file = cu.select_item_simple(case_files, return_index=False)
            first_state = next(iter(case_files[file]))
            first_row = case_files[file][first_state][0]
            for key, value in first_row.items():
                print(key, value)
        elif choice == "6":
            print("Select the case file to be written:")
            file = cu.select_item_simple(case_files, return_index=False)
            save_name = input("Enter a name to save the file with: ")
            su.write_csv(case_files[file], save_name)
        else:
            print("I don't know that command yet.\n")

def auto_mode() -> None:
    case_files = {}
    print(cu.format(f"Reading {place_filename}...", 'cyan'), end="", flush=True)
    place_file = read_file_auto(place_filename, delim='|', key_col=geo_column)
    print(cu.format("Done!", 'cyan'))
    print(cu.format(f"Normalizing {place_filename}...", 'cyan'), end="", flush=True)
    clean_placenames(place_file)
    print(cu.format("Done!", 'cyan'))
    print(cu.format(f"Reading {county_filename}...", 'cyan'), end="", flush=True)
    county_file = read_file_auto(county_filename, delim='|', key_col=geo_column)
    print(cu.format("Done!", 'cyan'))
    print(cu.format(f"Normalizing {place_filename}...", 'cyan'), end="", flush=True)
    clean_countynames(county_file)
    print(cu.format("Done!", 'cyan'))
    current_time = cu.dt.today().strftime("%Y%m%d%H%M")
    for file_name in case_filenames:
        print(cu.format(f"Reading {file_name}...", 'cyan'), end="", flush=True)
        case_file = read_file_auto(file_name, key_col=case_column)
        print(cu.format("Done!", 'cyan'))
        print(cu.format(f"Sorting {file_name}...", 'cyan'), end="", flush=True)
        case_file = sort_case(case_file)
        print(cu.format("Done!", 'cyan'))
        print(cu.format(f"Enriching {file_name}...", 'cyan'), flush=True)
        enrich_places(case_file, place_file)
        enrich_counties(case_file, county_file)
        print(cu.format("Done!", 'cyan'))
        name_norm = file_name.split('.')[0]
        save_name = f"{name_norm}_{current_time}.csv"
        print(cu.format(f"Saving {save_name}...", 'cyan'), end="", flush=True)
        su.write_csv(case_file, save_name)
        print(cu.format("Done!", 'cyan'))


# =[ Main Fuction ]============================================================
def main():
    print(cu.format("\nFile Combiner. Good luck.\n", 'cyan'))
    # Try/except block for all user inputs
    try:
        auto_mode()
    except cu.UserQuitException:
        cu.quit()
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
