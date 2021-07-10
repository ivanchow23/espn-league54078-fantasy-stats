#!/usr/bin/env python
""" This script is an "interface" between ESPN outputs and statsapi input for players.
    The idea is to scrape for all players of interest from ESPN rosters into a CSV that
    is compatible as input for the statsapi_db module. This input CSV will be used to
    populate the statsapi_db database to access player data from the statsapi server."""
import argparse
import os
import pandas as pd
import pickle
import re

# ESPN to statsapi player name mapping
ESPN_STATSAPI_PLAYER_NAME_MAPPING_TABLE = { "Ana": "ANA", "Ari": "ARI", "Bos": "BOS", "Buf": "BUF", "Cgy": "CGY", "Car": "CAR",
                                            "Chi": "CHI", "Col": "COL", "Cls": "CBJ", "Dal": "DAL", "Det": "DET", "Edm": "EDM",
                                            "Fla": "FLA", "LA":  "LAK", "Min": "MIN", "Mon": "MTL", "Nsh": "NSH", "NJ":  "NJD",
                                            "NYI": "NYI", "NYR": "NYR", "Ott": "OTT", "Phi": "PHI", "Pit": "PIT", "SJ":  "SJS",
                                            "StL": "STL", "TB":  "TBL", "Tor": "TOR", "Van": "VAN", "Vgs": "VGK", "Wsh": "WSH",
                                            "Wpg": "WPG" }

# ESPN to statsapi team abbreviation mapping
ESPN_STATSAPI_TEAM_ABBREV_MAPPING_TABLE = {}

def generate_players_list(in_dirs, out_csv_path):
    """ Given directory of ESPN season data, generate CSV file to use as input for statsapi_db.py """
    # First, find all folders with the season string (e.g.: 20192020)
    season_string_re_pattern = "^[0-9]{8}$"
    season_path_dicts = []
    for root, dir, _ in os.walk(in_dirs):
        for d in dir:
            if re.match(season_string_re_pattern, d):
                # List of dictionaries containing path and season string
                # Example: [{'path': "<path_to>\20182019", 'season_str': "20182019"} ...]
                season_path_dicts.append({'path': os.path.join(root, d), 'season_str': d})

    # List of dictionaries to keep track of all players we can find
    master_players_list = []

    # Iterate through each path
    for season_path_dict in season_path_dicts:
        season_str = season_path_dict['season_str']
        season_path = season_path_dict['path']

        # Look for draft recap and team roster files
        draft_recap_pickle_path = None
        league_rosters_pickle_path = None
        for root, _, files in os.walk(season_path):
            for f in files:
                if "Draft Recap" in f and f.endswith(".pickle"):
                    draft_recap_pickle_path = os.path.join(root, f)
                elif "League Rosters" in f and f.endswith(".pickle"):
                    league_rosters_pickle_path = os.path.join(root, f)

        # Load draft recap file
        if draft_recap_pickle_path:
            with open(draft_recap_pickle_path, 'rb') as pickle_path:
                # Read pickle data and convert dataframe to list of dicts
                pickle_data = pickle.load(pickle_path)
                pickle_dict_list = pickle_data[0]['df'].to_dict('records')

                # Update entry for each player in master list
                for player_dict in pickle_dict_list:
                    _add_or_update_player_entry(master_players_list, player_dict['Player'], player_dict['NHL Team'], season_str)

        # Load league roster file
        if league_rosters_pickle_path:
            with open(league_rosters_pickle_path, 'rb') as pickle_path:
                # Read pickle data
                pickle_data = pickle.load(pickle_path)
                team_rosters_dict = pickle_data[0]

                # For each team roster, convert roster dataframe into list of dicts
                for team in team_rosters_dict['team_rosters']:
                    team_roster_df = team_rosters_dict['team_rosters'][team]['roster_df']
                    team_roster_dict_list = team_roster_df.to_dict('records')

                    # Update entry for each player in master list
                    for player_dict in team_roster_dict_list:
                        _add_or_update_player_entry(master_players_list, player_dict['Player'], player_dict['Team'], season_str)

    # Output master players list to CSV
    master_players_list_df = pd.DataFrame(master_players_list)
    master_players_list_df.to_csv(out_csv_path, index=False)

def _add_or_update_player_entry(master_dict_list, player_name, team_str, year_str):
    """ Helper function to add a player entry into the master list of dictionaries.
        Applies any naming corrections as needed to convert between ESPN and statsapi
        name strings or abbreviations. If player already exists, skip.

        TODO: Does not handle players with the same names yet!
    """
    # First apply corrections to this player if needed
    corrected_player_name = _get_corrected_player_name(player_name)
    corrected_team_abbrev = _get_corrected_team_abbrev(team_str)

    # If player doesn't exist in master list, add entry
    # TODO: Does not currently handle players with the same name.
    player_dict = next((p_dict for p_dict in master_dict_list if p_dict['Player Name'] == corrected_player_name), None)
    if not player_dict:
        if corrected_player_name != player_name or corrected_team_abbrev != team_str:
            print(f"Applied Correction: {player_name} {team_str} -> {corrected_player_name} {corrected_team_abbrev}")
        print(f"Adding to master list: {corrected_player_name} {corrected_team_abbrev} {year_str}")

        # Dictionary keys follow same column names as file headers required for statsapi_db entry
        master_dict_list.append({'Player Name': corrected_player_name, 'Team': corrected_team_abbrev, 'Year': year_str})

def _get_corrected_player_name(player_name):
    """ Takes player name (likely from ESPN scripts) and corrects it to match statsapi name.
        If no valid correction exists, then simply return the original name. """
    try:
        ret = ESPN_STATSAPI_TEAM_ABBREV_MAPPING_TABLE[player_name]
        #print(f"Applying player correction {player_name} -> {ret}")
        return ret
    except KeyError:
        return player_name

def _get_corrected_team_abbrev(team_abbrev):
    """ Takes team abbreviation (likely from ESPN scripts) and corrects it to match statsapi
        team abbreviation. If no valid correction exists, then simply return the original name. """
    try:
        ret = ESPN_STATSAPI_PLAYER_NAME_MAPPING_TABLE[team_abbrev]
        #print(f"Applying team correction {team_abbrev} -> {ret}")
        return ret
    except KeyError:
        return team_abbrev

if __name__ == "__main__":
    # Input of this script is simply a directory containing season folders of ESPN data
    # Expected example folder structure:
    # input_directory:
    #   - 20182019
    #       -> Team roster data
    #       -> Draft recap data
    #   - 20192020
    #       -> Team roster data
    #       -> Draft recap data
    #   ...
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('-d', required=True, help="Input directory containing folders of ESPN season data.")
    arg_parse.add_argument('-o', required=True, help="Output CSV file containing a list of player data used for statsapi_db input.")
    args = arg_parse.parse_args()
    generate_players_list(args.d, args.o)