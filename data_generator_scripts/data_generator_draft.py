#!/usr/bin/env python
""" Generates draft data. """
import argparse
import os
import pandas as pd
import timeit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

from espn_html_parser_scripts.espn_html_parser import EspnHtmlParser
from espn_fantasy_api_scripts.espn_fantasy_api_downloads_parser import EspnFantasyApiDownloadsParser

DEFAULT_ESPN_HTML_ROOT_FOLDER = os.path.join(SCRIPT_DIR, "..", "espn_html_files")
DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER = os.path.join(SCRIPT_DIR, "..", "espn_fantasy_api_scripts", "espn_fantasy_api_downloads")
DEFAULT_OUTPUT_DIR = SCRIPT_DIR

US_STATE_CODES = [
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
]

CAN_PROVINCE_CODES = [
    'AB', 'BC', 'MB', 'NB', 'NL', 'NS', 'NT', 'NU', 'ON', 'PE', 'QC', 'SK', 'YT'
]

class DataGeneratorDraft():
    def __init__(self, espn_html_root_folder=DEFAULT_ESPN_HTML_ROOT_FOLDER,
                       espn_fantasy_api_downloads_root_folder=DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER,
                       out_dir_path=DEFAULT_OUTPUT_DIR):
        """ Default constructor. """
        self._espn_html_root_folder = espn_html_root_folder
        self._espn_fantasy_api_downloads_root_folder = espn_fantasy_api_downloads_root_folder
        self._out_dir_path = out_dir_path

    def get_df(self):
        """ Generate dataframe. """
        # ------------------------------------------- Merge data from multiple sources -------------------------------------------
        # Parse draft data from ESPN HTML files
        # This will be the "primary source" for draft data because it's a snapshot of the draft for each season
        espn_html_draft_df = EspnHtmlParser(self._espn_html_root_folder).get_draft_df()

        # Parse draft details data from ESPN fantasy API
        downloads_parser = EspnFantasyApiDownloadsParser(self._espn_fantasy_api_downloads_root_folder)
        espn_fantasy_draft_details_df = downloads_parser.get_draft_details_df()
        espn_fantasy_athletes_info_df = downloads_parser.get_athletes_df()
        espn_fantasy_all_players_info_df = downloads_parser.get_all_players_info_df()

        # Merge ESPN fantasy API draft details into ESPN HTML draft dataframe
        # We only care about the player ID here to get additional player info later
        # This assumes the ESPN HTML draft data is in the same order as ESPN fantasy API draft details
        merged_df = espn_html_draft_df.merge(espn_fantasy_draft_details_df[['Draft Number', 'Round Number', 'Season', 'Player ID']],
                                             how='left', on=['Draft Number', 'Round Number', 'Season'])

        # Merge athlete info into draft dataframe to get additional player details
        espn_fantasy_athletes_info_df = espn_fantasy_athletes_info_df.drop(columns=['Player Name'])
        merged_df = merged_df.merge(espn_fantasy_athletes_info_df, how='left', on='Player ID')

        # Merge all players info into draft dataframe to get season-by-season stats
        espn_fantasy_all_players_info_df = espn_fantasy_all_players_info_df.drop(columns=['Player Name'])
        merged_df = merged_df.merge(espn_fantasy_all_players_info_df, how='left', on=['Player ID', 'Season'])

        # ------------------------------------------- Data cleaning and transformations -------------------------------------------
        # Add column that converts birth place to birth country code
        merged_df['Player Birth Place'] = merged_df['Player Birth Place'].fillna("")
        merged_df.insert(merged_df.columns.get_loc('Player Birth Place') + 1, 'Player Birth Country',
                         merged_df['Player Birth Place'].apply(self._player_birth_place_to_birth_country_code))

        # Replace player height column from feet/inches string to total inches and rename column
        merged_df['Player Height'] = merged_df['Player Height'].fillna("")
        merged_df['Player Height'] = merged_df['Player Height'].apply(self._player_feet_inches_to_total_inches)
        merged_df = merged_df.rename(columns={'Player Height': 'Player Height (in)'})

        # Add column for player age at time of draft season
        merged_df['Player DOB'] = merged_df['Player DOB'].fillna("")
        series = merged_df.apply(lambda x: self._player_dob_string_to_age(x['Player DOB'], str(x['Season'])), axis=1)
        merged_df.insert(merged_df.columns.get_loc('Player DOB') + 1, 'Player Age', series)

        # Strip "lbs" from weight column, convert to numeric, rename column
        merged_df['Player Weight'] = pd.to_numeric(merged_df['Player Weight'].str.replace(' lbs', '', regex=False), errors='coerce')
        merged_df = merged_df.rename(columns={'Player Weight': 'Player Weight (lbs)'})

        return merged_df

    def _player_birth_place_to_birth_country_code(self, birth_place):
        """ ESPN data shows birth "place" which can be a mix of provinces, states,
            and countries. This is a helper function to convert the "place" into
            a country code.

            Example: birth_place = "Winnipeg, MB" -> country_code = "CAN"
            Example: birth_place = "Buffalo, NY" -> country_code = "USA"
            Example: birth_place = "Gavle, SWE" -> country_code = "SWE" """
        if birth_place is None or birth_place == "":
            return ""

        # Split by comma to separate city from province/state/country
        birth_prov_state_country = birth_place.split(",")[-1].strip()

        # Case 1: Check if it is a province (Canada)
        if birth_prov_state_country in CAN_PROVINCE_CODES:
            return "CAN"

        # Case 2: Check if it is a state (USA)
        if birth_prov_state_country in US_STATE_CODES:
            return "USA"

        # Case 3: Return as-is (assumed to be country/country code/unknown)
        return birth_prov_state_country

    def _player_feet_inches_to_total_inches(self, feet_inches):
        """ Convert height in feet and inches (e.g., "6' 2\"") to total inches (e.g., 74). """
        if feet_inches is None or feet_inches == "":
            return float('nan')
        try:
            feet, inches = feet_inches.split("'")
            feet = int(feet.strip())
            inches = int(inches.replace('"', '').strip())
            total_inches = (feet * 12) + inches
            return total_inches
        except Exception:
            return float('nan')

    def  _player_dob_string_to_age(self, dob_string, season_string):
        """ Takes in date of birth string (dd/mm/yyyy) and calculates the player's
            rough age at the current time of the given season. Does this by simply
            taking the difference between player's birth year and the start of the
            season.

            Example: dob_string = 28/3/1991, season_string = 20152016
                     Age = 2015 - 1991 = 24
        """
        if dob_string is None or dob_string == "":
            return float('nan')

        if season_string is None or season_string == "":
            return float('nan')

        try:
            birth_year = int(dob_string.split('/')[-1])
            season = int(season_string[0:4])
            return season - birth_year
        except TypeError:
            return float('nan')

if __name__ == "__main__":
    start_time = timeit.default_timer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--espn_html_root_folder", type=str, default=DEFAULT_ESPN_HTML_ROOT_FOLDER,
                        help="Root folder path containing ESPN HTML files.")
    parser.add_argument("--espn_fantasy_api_downloads_root_folder", type=str, default=DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER,
                        help="Root folder path containing ESPN Fantasy API downloaded files.")
    parser.add_argument("--out_dir_path", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory path to save generated data.")
    args = parser.parse_args()

    print("Generating draft data...")
    data_generator = DataGeneratorDraft(
        espn_html_root_folder=args.espn_html_root_folder,
        espn_fantasy_api_downloads_root_folder=args.espn_fantasy_api_downloads_root_folder,
        out_dir_path=args.out_dir_path
    )

    draft_df = data_generator.get_df()
    draft_df.to_csv(os.path.join(args.out_dir_path, "draft_df.csv"), index=False)
    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")