#!/usr/bin/env python
""" Script used to validate player names from ESPN outputs to be used as
    reference for statsapi. The purpose of this script is to ensure all
    data is unified to conform to statsapi naming conventions between
    ESPN and statsapi files. This validation step ensures all inputs are
    corrected "early" in the toolchain so data going into later stages
    are as clean as possible.

    General workflow when using this script:
      1. Script takes all relevant outputs from ESPN parsed data to create
         a "master list" of players for all years.
      2. Check each player against the team and year they played for with
         statsapi team roster data. Note: This depends on all required team
         roster data to be downloaded from statsapi locally.
      3. If player entry exists - ok.
      4. If player entry does not exist, flag a warning/error.
      5. All warnings and errors must be addressed or manually corrected in
         the ESPN parsing layer.
"""
import argparse
import json
import pandas as pd
import os
import re
import sys

SCRIPT_NAME = os.path.basename(__file__)
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
from espn_html_parser_loader import EspnHtmlParserLoader
from statsapi_loader import StatsapiLoader

# Regex pattern to find a season string
#   - ^ used to denote start of string searching
#   - $ used to denote end of string searching
#   - + used to denote any repeating numbers between [0-9]
# Examples:
#  - "20192020" (ok)
#  - "aaa20192020" (no)
#  - "20192020aaa" (no)
SEASON_STRING_RE_PATTERN = "^[0-9]+$"

class ErrorLogger():
    """ Error logging class used to output messages to a log file for validation. """
    def __init__(self, folder_path, file_name):
        """ Constructor. """
        self._file_path = os.path.join(folder_path, file_name)
        self._msg_buffer = []

    def log(self, msg):
        """ Adds a string message to buffer to be later written to file. """
        self._msg_buffer.append(msg)

    def write_file(self):
        """ Writes message in buffer to file. Writes a custom message if no messages
            are present in buffer (implies no problems). Call this when script is about
            to finish running. """
        num_errors = len(self._msg_buffer)
        with open(self._file_path, 'w') as f:
            f.write(f"{SCRIPT_NAME} found {num_errors} errors.\n\n")
            if len(self._msg_buffer) == 0:
                f.write("No further corrections or fixes needed.")
            else:
                for msg in self._msg_buffer:
                    f.write(f"{msg}\n")

def main(espn_path, statsapi_path, out_path):
    """ Runs the main validation function. Outputs a "master list" of players and
        any warnings/errors that need to be corrected.
            - espn_path: Root path of parsed ESPN data from ESPN scripts.
            - statsapi_path: Root path of statsapi data cache from statsapi downloader.
            - out_path: Path to folder where outputs of this script will go.

        Expected folder structures for ESPN and statsapi data are the same, where each
        folder represents the season:
            - 20142015
            - 20152016
            - etc.
    """
    print(f"Running {SCRIPT_NAME}...")

    # Exit if any of the input paths or output path is invalid
    if not _check_paths(espn_path, statsapi_path, out_path):
        print("Exiting...")
        exit(-1)

    # Error file logging class
    err = ErrorLogger(out_path, "errors.log")

    # Validating ESPN data is compatible with statsapi data
    # So look for season folders from ESPN data
    season_folders = [d for d in os.listdir(espn_path)
                      if os.path.isdir(os.path.join(espn_path, d)) and re.match(SEASON_STRING_RE_PATTERN, d)]

    # Process each season data into a master list
    master_players_list = []
    for season_string in season_folders:
        # Check season folders exist for ESPN and statsapi
        if not _check_season_paths(espn_path, statsapi_path, season_string):
            print(f"Skipping validation for season: {season_string}")
            err.log(f"Unable to validate season: {season_string}. Check data paths exist.")
            continue

        # Check statsapi team roster data exists
        statsapi_team_roster_path = os.path.join(statsapi_path, season_string, "team_rosters")
        if not os.path.exists(statsapi_team_roster_path):
            print(f"Cannot find statsapi team roster data for season: {season_string}. Skipping...")
            err.log(f"Unable to validate season: {season_string}. Missing statsapi team roster data.")
            continue

        # Load ESPN data
        espn_html_parser_loader = EspnHtmlParserLoader(espn_path)
        espn_draft_recap_df = espn_html_parser_loader.load_draft_recap_data(season_string)
        espn_clubhouses_list = espn_html_parser_loader.load_clubhouses_data(season_string)

        # Combine all clubhouses into single dataframe
        espn_clubhouses_df = pd.DataFrame()
        for team_dict in espn_clubhouses_list:
            # Multi-index dataframes
            skaters_df = team_dict['skaters_df']['Skaters']
            goalies_df = team_dict['goalies_df']['Goalies']
            espn_clubhouses_df = pd.concat([espn_clubhouses_df, skaters_df, goalies_df], ignore_index=True)

        # Combine into master list of dictionaries
        master_players_list += _combine_dfs_to_dicts(espn_draft_recap_df, espn_clubhouses_df, season_string)

        # Remove empty entries
        master_players_list = [d for d in master_players_list if d['Player'] != "" and d['Team'] != ""]

    # Process and validate each entry in master list
    statsapi_loader = StatsapiLoader(statsapi_path)
    for entry in master_players_list:
        # Look for valid player mapping in the master list to the statsapi data
        player = entry['Player']
        team = entry['Team']
        season = entry['Season']
        player_id = statsapi_loader.get_player_id(player, team, season)

        # Player doesn't exist given inputs
        if player_id == -1:
            err_string = f"Cannot find statsapi entry: {player:<20} {team:<5} {season:<10} "

            # Attempt to search in other teams and provide a suggestion in the error output
            candidates = _search_for_player_in_teams(statsapi_path, player, season)
            if len(candidates) > 0:
                err_string += "Suggestion(s): "
                for c in candidates:
                    err_string += f"[{c['player']} {c['team']} {c['season']}] "
            err.log(err_string)

    # Finish
    err.write_file()
    print(f"Validation tool finished. Review outputs: {out_path}")

def _check_paths(espn_path, statsapi_path, out_path):
    """ Helper function to abstract path checking for input and outputs. """
    ret = True
    if not os.path.exists(espn_path):
        print(f"Invalid input path: {espn_path}")
        ret = False

    if not os.path.exists(statsapi_path):
        print(f"Invalid input path: {statsapi_path}")
        ret = False

    try:
        os.makedirs(out_path, exist_ok=True)
    except OSError:
        print(f"Invalid output path: {out_path}")
        ret = False

    return ret

def _check_season_paths(espn_path, statsapi_path, season_string):
    """ Helper function to abstract path checking for season input paths. """
    ret = True

    espn_season_path = os.path.join(espn_path, season_string)
    if not os.path.exists(espn_season_path):
        print(f"Cannot find: {espn_season_path}")
        print("Has ESPN data been parsed and processed?")
        ret = False

    statsapi_season_path = os.path.join(statsapi_path, season_string)
    if not os.path.exists(statsapi_season_path):
        print(f"Cannot find: {statsapi_season_path}")
        print(f"Has statsapi data been downloaded?")
        ret = False

    return ret

def _combine_dfs_to_dicts(espn_draft_recap_df, espn_clubhouses_df, season_string):
    """ Helper function to combine dataframes together. Handles duplicate
        player entries. Returns a list of dictionaries."""
    # Handle empty cases
    if espn_draft_recap_df is None and espn_clubhouses_df is None:
        return []

    # Combine dataframes together, then:
    # - Only keep columns relevant to what we need
    # - Drop duplicate entries
    # - Add season column to dataframe
    combined_df = pd.concat([espn_draft_recap_df, espn_clubhouses_df], axis=0, ignore_index=True)
    combined_df = combined_df[['Player', 'Team']]
    combined_df = combined_df.drop_duplicates()
    combined_df['Season'] = season_string

    return combined_df.to_dict('records')

def _search_for_player_in_teams(statsapi_path, player_name, season_string):
    """ Function that tries to search for a player on a team in a given season.
        This function is meant to be crude but hopefully helps automate this
        search process without having to manually look it up as a user. Searches
        through statsapi team roster data for a given season. Returns a list of
        candiadtes found (typically will just be one team, but this helps handle
        the edge case of a player with the same name or if they were part of
        multiple teams in a season). Returns empty list otherwise.

        Note: This function is not meant to help automatically fix any incorrect
        players/teams. Use this to help suggest corrections instead. """
    candidate_teams = []

    # Iterate through each team roster file for the given season
    team_rosters_season_path = os.path.join(statsapi_path, season_string, "team_rosters")
    for file in os.listdir(team_rosters_season_path):

        # Not a file in format we expect
        if not re.match(f"{season_string}_team[0-9]+_roster.json", file):
            continue

        # Read file and look for the player in the roster
        team_roster_path = os.path.join(team_rosters_season_path, file)
        with open(team_roster_path, 'r') as f:
            data_dict = json.load(f)

            # If found, save this team as a potential candidate to be correct
            for player_dict in data_dict['teams'][0]['roster']['roster']:
                # No modifications to player name
                if player_dict['person']['fullName'] == player_name:
                    candidate_teams.append({'player': player_name,
                                            'team': data_dict['teams'][0]['abbreviation'],
                                            'season': season_string})

                # Check the edge-case where player's name is abbreviated
                # Strip out all periods in the name if any (example: P.K. -> PK)
                elif player_dict['person']['fullName'] == player_name.replace(".", ""):
                    candidate_teams.append({'player': player_name.replace(".", ""),
                                            'team': data_dict['teams'][0]['abbreviation'],
                                            'season': season_string})
    return candidate_teams

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--espn", required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    arg_parser.add_argument("--statsapi", required=True, help="Root path of statsapi data cache from statsapi downloader.")
    arg_parser.add_argument("--outdir", required=True, help="Path to folder where outputs of this script will go.")
    args = arg_parser.parse_args()

    espn_path = args.espn
    statsapi_path = args.statsapi
    out_path = args.outdir
    main(espn_path, statsapi_path, out_path)