"""
Name:       htools.py
Author:     Phil Hansen
Version:    20260227

This tool is currently configured to add geographic data to NamUs database
exported csv files. No alterations are made to the original NamUs data.
"""

# =[ Imports ]=================================================================
import cli_utils as cu
import std_utils as su
from typing import TypeAlias

# =[ Global variables ]========================================================
# The list of options in the main menu while in manual mode.
main_menu = [
    {"name": "Read-in Case Files"},             # 0
    {"name": "Read-in Geo-files"},              # 1
    {"name": "Enrich with GEOIDs"},             # 2
    {"name": "Write-out JSON file"},            # 3
    {"name": "List loaded files"},              # 4
    {"name": "List file header"},               # 5
    {"name": "Write-out CSV file"},             # 6
    {"name": "Combine County-level Datasets"}   # 7
]
# Master dictionary for couty-level data aggregation
county_data_files: dict[str, dict[str, dict[str, list[dict[str, str]]]]] = {
    'census_ll':{},
    'population': {},
    'unemployment': {},
    'poverty': {},
    'education': {}
}
# These names are hardcoded for speed in auto-mode:
place_filename = "2025_Gaz_place_national.txt"
county_filename = "2025_Gaz_counties_national.txt"
subdiv_filename = "2025_Gaz_cousubs_national.txt"
geo_column = "GEOID"
st_column = "USPS"
case_filenames = ["missing_namus.csv", "unid_namus.csv", "unclaim_namus.csv"]
case_column = "State"
# This is used to provide geographic data for small island areas not provided in
# US Census data, they represent centroids of the island or groups of islands.
TERR_COUNTY = {
    "GU": [
        # Guam (single county equivalent)
        {
            "NAME": "Guam",
            "GEOID": "66010",
            "LL": (13.4054, 144.7517),  # approximate center point of Guam
        },
    ],
    "AS": [
        # American Samoa Districts / equivalents
        {
            "NAME": "Eastern District",
            "GEOID": "60010",
            "LL": (-14.2845, -170.6480),  # center of Eastern District
        },
        {
            "NAME": "Manu'a District",
            "GEOID": "60020",
            "LL": (-14.2053, -169.5410),  # center of Manu'a District
        },
        {
            "NAME": "Rose Island (Rose Atoll)",
            "GEOID": "60030",
            "LL": (-14.5833, -168.1500),  # approximate lat/lon (small atoll)
        },
        {
            "NAME": "Swains Island",
            "GEOID": "60040",
            "LL": (-11.0650, -171.0600),  # approximate geographic center
        },
        {
            "NAME": "Western District",
            "GEOID": "60050",
            "LL": (-14.3000, -170.7500),  # approximate middle of western districts
        },
    ],
    "MP": [
        # Northern Mariana Islands municipalities
        {
            "NAME": "Northern Islands Municipality",
            "GEOID": "69085",
            "LL": (16.0000, 145.7500),  # rough central Pacific location (cluster of northern isles)
        },
        {
            "NAME": "Rota Municipality",
            "GEOID": "69100",
            "LL": (14.1522, 145.2018),  # Rota approximate center
        },
        {
            "NAME": "Saipan Municipality",
            "GEOID": "69110",
            "LL": (15.2123, 145.7545),  # Saipan approximate center
        },
        {
            "NAME": "Tinian Municipality",
            "GEOID": "69120",
            "LL": (14.9700, 145.6200),  # approximate center near Tinian island
        },
    ],
    "VI": [
        # U.S. Virgin Islands county equivalents
        {
            "NAME": "St. Croix",
            "GEOID": "78010",
            "LL": (17.7500, -64.7000),  # approximate center of St. Croix
        },
        {
            "NAME": "St. John",
            "GEOID": "78020",
            "LL": (18.3300, -64.7300),  # approximate center of St. John
        },
        {
            "NAME": "St. Thomas",
            "GEOID": "78030",
            "LL": (18.3400, -64.9300),  # approximate center of St. Thomas
        },
    ],
}
"""
demo_cols = ["Rural_Urban_Continuum_Code_2023", "Urban_Influence_2013",
    "Economic_typology_2015", "CENSUS_2020_POP", "POP_ESTIMATE_2023", 
    "N_POP_CHG_2023", "INTERNATIONAL_MIG_2023", "DOMESTIC_MIG_2023",
    "NET_MIG_2023"]
"""
# The suffixes are used to clean the US Census data before matching to the NamUs
# database data.

place_suffixes = ["CDP", "city", "town", "village", "borough", "zona",
                "urbana", "(balance)", "and", "government", "unified",
                "county", "consolidated", "urban", "metro", "comunidad",
                "municipality",]
"""
county_suffixes = ["County", "Parish", "Municipio", "CDP", "city", "town",
                "village", "borough", "zona", "urbana", "(balance)", "and",
                "government", "unified", "county", "consolidated", "urban",
                "metro", "comunidad", "municipality",]
ak_county_suffixes = ["City", "and", "Borough", "Municipality", "Census", "Area"]
"""
# This list of states is used to assist the organization of groups in the
# dictionaries as NamUs data is not consistent with State Names vs Codes.
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
    # Washington DC
    "District of Columbia": "DC",
    # Territories
    "American Samoa": "AS",
    "Guam": "GU",
    "Northern Mariana Islands": "MP",
    "Puerto Rico": "PR",
    "Virgin Islands": "VI"
}


# =[ Class definitions ]=======================================================

# =[ Type definitions ]========================================================
# This type alias has not been implimented yet.

type GroupedDict = dict[str, list[dict[str, str]]]
type DoubleGroupedDict = dict[str, GroupedDict]

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

def clean_subdiv_names(subdiv) -> None:
    pass

def extract_subdiv_geoid(place_geoid: str) -> str:
    """
    Extracts the 5-digit county or county-equivalent FIPS or GEOID from the long
    form 19-digit county subdivision-level GEOID.

    :param place_geoid: The long form GEOID to extract from
    :type place_geoid: str
    :return: The extracted 5-digit GEOID
    :rtype: str
    """
    return place_geoid[-10:-5]

def norm_geoid(geoid: Any) -> str:
    """
    Normalizes the GEOID value to a 5 digit string with leading zeros.

    :param geoid: The input value to be normalized
    :type geoid: Any
    :return: The normalized string.
    :rtype: str
    """
    return str(geoid).strip().zfill(5)
    
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
    """
    Sorts the cases in alphabetical state order. Normalized group keys to two-
    letter state abbreviation i.e. Alabama to AL

    :param case_list: The cases to be sorted and normed.
    :type case_list: dict[str, list[dict[str, str]]]
    :return: The sorted case file dictionary
    :rtype: dict[str, list[dict[str, str]]]
    """
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

def match_county(
    target: str,
    state: dict[str, dict[str, str]]
    ) -> tuple(str, bool, int):
    for county in state:
        candidate = cu.norm_string(county["NAME"])
        if target == candidate or target in candidate:
            # print(cu.format(f"{target} matched to {candidate}!", "green"))
            return norm_geoid(county["GEOID"]), False, 1
    return "NA", True, 0

def match_subdiv(
    target: str,
    state: dict[str, dict[str, str]]
    ) -> tuple(str, bool, int):
    for subdiv in state:
        candidate = cu.norm_string(subdiv["NAME"])
        if target == candidate or target in candidate:
            # print(cu.format(f"Back-up matched {target} to {candidate}!", "yellow"))
            return extract_subdiv_geoid(subdiv["GEOIDFQ"]), False, 1
    return "NA", True, 0

def enrich_geoid(
    case_file: GroupedDict,
    enrichment: GroupedDict,
    backup_enrichment: GroupedDict | None = None
    ) -> None:
    """
    Adds the 5-digit FIPS GEOID value for the county or territory of the case
    for quick data lookups.

    :param case_file: The loaded casefile to be enriched.
    :type case_file: GroupedDict
    :param enrichment: The loaded US Census county locations file.
    :param enrichment: GroupedDict
    """
    tot_fixes = 0
    tot_items = 0
    for state in case_file:
        # This confusing little bit is to ensure the state abbreviation is used
        # as one of the NamUs dataset uses full state names for some reason. 
        if state in states:
            state = states[state]
        st_fixes = 0
        st_total = 0
        for row in case_file[state]:
            no_match = True
            target_norm = cu.norm_string(row["County"])
            if state in TERR_COUNTY:
                if state == "GU":
                    row["GEOID"] = TERR_COUNTY[state][0]["GEOID"]
                    no_match = False
                    st_fixes += 1
                else:
                    row["GEOID"], no_match, add = match_county(target_norm, TERR_COUNTY[state])
                    st_fixes += add
            else:
                row["GEOID"], no_match, add = match_county(target_norm, enrichment[state])
                st_fixes += add
                
            if no_match:
                if state in TERR_COUNTY:
                    pass
                else:
                    target_norm_bkup = cu.norm_string(row["City"])
                    row["GEOID"], no_match, add = match_subdiv(target_norm_bkup, backup_enrichment[state])
                    st_fixes += add
            if no_match:
                if target_norm_bkup:
                    text = f" or {target_norm_bkup}"
                print(cu.format(f"No match found for {target_norm}{text} in {state}!", "red"))
            st_total += 1
        tot_fixes += st_fixes
        tot_items += st_total
        percent = round((st_fixes / st_total) * 100)
        color = cu.grade_color(percent)
        print(cu.format(
            f"{st_fixes}/{st_total} ({percent}%) enriched for {state}.", color
        ))
        # input("press any key to continue")
    tot_per = round((tot_fixes / tot_items) * 100)
    color = cu.grade_color(tot_per)
    print(cu.format(
        f"{tot_fixes}/{tot_items} ({tot_per}%) enriched for all County data.",
        color
    ))

def enrich_county_ll(
        case_file: dict[str, list[dict[str, str]]],
        enrichment: dict[str, list[dict[str, str]]]
    ) -> None:
    tot_fixes = 0
    tot_items = 0
    for state in case_file:
        # This confusing little bit is to ensure the state abbreviation is used
        # as one of the NamUs dataset uses full state names for some reason. 
        if state in states:
            state = states[state]
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
            target_norm = str(row["County"]).lower()
            for county in enrichment[state]:
                cnty_norm = str(county["NAME"]).lower()
                if target_norm == cnty_norm or target_norm in cnty_norm:
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

def enrich_county_demo(
        case_file: dict[str, list[dict[str, str]]],
        enrichment: dict[str, dict[str, list[dict[str, str]]]]
    ) -> None:
    pass
    # TODO: Write function to add USDA demographic data.
    tot_fixes = 0
    tot_items = 0
    for state in case_file:
        # This confusing little bit is to ensure the state abbreviation is used
        # as one of the NamUs dataset uses full state names for some reason. 
        if state in states:
            state = states[state]
        st_fixes = 0
        st_total = 0
        for row in case_file[state]:
            if state in islands and state != "PR":
                # TODO: Figure out how to handle demo info for non-PR islands.
                st_fixes += 1
                st_total += 1
                continue
            no_match = True
            target_norm = str(row["County"]).lower()
            for county in enrichment[state]:
                cnty_norm = str(county).lower()
                if target_norm == cnty_norm or target_norm in cnty_norm:
                    for item in enrichment[state][county]:
                        if item['Attribute'] in demo_cols:
                            row[item['Attribute']] = item['Value']
                    no_match = False
                    st_fixes += 1
                    break
            if no_match:
                for item in demo_cols:
                    row[item] = ""
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
        encoding: str = 'utf-8',
        key_col: str | None = None
        ) -> dict[str, list[dict[str, str]]]:
    try:
        return su.read_to_grouped_dict(file_name, delim=delim, key_col=key_col)
    except ValueError as e:
        print(cu.format(e, "red"))
        key_col = input("Enter the key column name: ")
        return su.read_to_grouped_dict(file_name, delim, key_col)

def combine_case_files(case_file_1: dict[str, list[dict[str, str]]]) -> None:

    pass

def combine_county_data_files(county_files: dict[str, dict[str, list[dict[str, str]]]]):
    pass

def manual_mode() -> None:
    case_files = {}
    place_dict = None
    county_dict = None
    usda_dict = None
    while True:
        choice = cu.select_item(main_menu, return_key="_index_")
        if choice == "0":
            file_name = cu.select_file(file_type='*.csv')
            file_dict = su.read_to_grouped_dict(file_name, key_col='State')
            case_files[file_name] = sort_case(file_dict)
        # Read-in Geo Files
        elif choice == "1":
            print("What type of geo file will you be reading in?")
            sub_choice = cu.select_item_simple(["Places", "County Lat/Lons", "County Demographics"])
            file_name = cu.select_file()
            # Places File
            if sub_choice == "0":
                file_dict = su.read_to_grouped_dict(
                    file_name, key_col='USPS', delim='|'
                )
                clean_placenames(file_dict)
                place_dict = file_dict
                place_file_name = file_name
            # Counties File
            elif sub_choice == "1":
                file_dict = su.read_to_grouped_dict(
                    file_name, key_col='USPS', delim='|'
                )
                # clean_countynames(file_dict)
                county_dict = file_dict
                county_file_name = file_name
            elif sub_choice == "2":
                file_dict = su.read_to_double_grouped_dict(
                    file_name, encoding='latin-1', key_col='State', sec_col='Area_Name'
                )
                usda_dict = file_dict
                usda_file_name = file_name
        elif choice == "2":
            if not usda_dict or not county_dict:
                print(cu.format(
                    "No geo files loaded! Load a places file first!",
                    "red"
                ))
                continue
            print("Select the case file to be enriched:")
            case_file = cu.select_item_simple(case_files, return_index=False)
            # enrich_places(case_files[case_file], place_dict)
            # input("Places enriched, press ENTER to enrich counties...")
            enrich_county_ll(case_files[case_file], county_dict)
            enrich_county_demo(case_files[case_file], usda_dict)
        elif choice == "3":
            file = cu.select_item_simple(case_files, return_index=False)
            save_name = input(f"\nEnter a name to save {file} as: ")
            su.write_json(case_files[file], save_name)
        elif choice == "4":
            print("Loaded files list:")
            if place_dict:
                print(f"{place_file_name} loaded as places dictionary")
            if county_dict:
                print(f"{county_file_name} loaded as county lat/lon dictionary")
            if usda_dict:
                print(f"{usda_file_name} loaded as county demographic dictionary")
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

def auto_mode_old() -> None:
    # This is the previous auto_mode functions before the GEIOD rewrite.
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


def auto_mode() -> None:
    # GEOID Auto Mode function.
    # case_files = {}
    print(cu.format(f"Reading {county_filename}...", 'cyan'), end="", flush=True)
    county_file = read_file_auto(f"./base/{county_filename}", delim='|', key_col=st_column)
    print(cu.format("Done!", 'cyan'))
    print(cu.format(f"Reading {subdiv_filename}...", 'cyan'), end="", flush=True)
    subdiv_file = read_file_auto(f"./base/{subdiv_filename}", delim='|', key_col=st_column)
    print(cu.format("Done!", 'cyan'))
    current_time = cu.dt.today().strftime("%Y%m%d%H%M")
    file_name = "missing_namus.csv"
    for file_name in case_filenames:
        print(cu.format(f"Reading {file_name}...", 'cyan'), end="", flush=True)
        case_file = read_file_auto(f"./base/{file_name}", key_col=case_column)
        print(cu.format("Done!", 'cyan'))
        print(cu.format(f"Sorting {file_name}...", 'cyan'), end="", flush=True)
        case_file = sort_case(case_file)
        print(cu.format("Done!", 'cyan'))
        print(cu.format(f"Enriching {file_name}...", 'cyan'), flush=True)
        enrich_geoid(case_file, county_file, subdiv_file)
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
        # manual_mode()
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
