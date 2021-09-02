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
import csv # TODO: Used for loading and reading CSV map files - could go into utility
import json # TODO: Used for loading JSON file from statsapi data cache - could go into utility
import pandas as pd
import pickle # TODO: Required for loading ESPN files - could go into utility
import os
import re

SCRIPT_NAME = os.path.basename(__file__)

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
      espn_draft_recap_df = _load_espn_draft_recap(espn_path, season_string)
      espn_clubhouses_df = _load_espn_clubhouses(espn_path, season_string)

      # Combine into master list of dictionaries
      master_players_list += _combine_dfs_to_dicts(espn_draft_recap_df, espn_clubhouses_df, season_string)

      # Remove empty entries
      master_players_list = [d for d in master_players_list if d['Player'] != "" and d['Team'] != ""]

   # Process and validate each entry in master list
   for entry in master_players_list:
      # Each entry should now have enough information to find the player in statsapi team roster
      # Retrieve the player's statsapi endpoint link given the information and add to dictionary
      player = entry['Player']
      team = entry['Team']
      season = entry['Season']
      entry['statsapi_endpoint'] = _get_statsapi_player_endpoint(statsapi_path, player, team, season)

      # Player doesn't exist in team roster for given inputs
      if entry['statsapi_endpoint'] == "":
         err_string = f"Cannot find statsapi entry: {player:<20} {team:<5} {season:<10} "

         # Attempt to search in other teams and provide a suggestion in the error output
         candidates = _search_for_player_in_teams(statsapi_path, player, season)
         if len(candidates) > 0:
            err_string += "Suggestion(s): "
            for c in candidates:
               err_string += f"[{c['player']} {c['team']} {c['season']}] "

         err.log(err_string)

   # Finish
   master_players_df = pd.DataFrame(master_players_list)
   master_players_df.to_csv(os.path.join(out_path, "master_players_list.csv"), index=False)
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

def _load_espn_draft_recap(espn_path, season_string):
   """ Finds and loads the ESPN draft recap file.
       Returns None if file doesn't exist or on error.
       TODO: This could be ported to an ESPN loading utility. """
   pickle_data_df = None

   # Look for draft recap files
   season_path = os.path.join(espn_path, season_string)
   draft_recap_pickle_path = None
   for root, _, files in os.walk(season_path):
      for f in files:
         if "Draft Recap" in f and f.endswith(".pickle"):
            draft_recap_pickle_path = os.path.join(root, f)

   # Read data if available
   if draft_recap_pickle_path:
      with open(draft_recap_pickle_path, 'rb') as pickle_path:
         # Read pickle data and convert dataframe to list of dicts
         pickle_data_df = pickle.load(pickle_path)

   return pickle_data_df

def _load_espn_clubhouses(espn_path, season_string):
   """ Finds and loads the ESPN clubhouses file. Concat team rosters into a
       list before returning. Returns None if file doesn't exist or on error.
       TODO: This could be ported to an ESPN loading utility. """
   pickle_data_df = None

   # Look for draft recap files
   season_path = os.path.join(espn_path, season_string)
   clubhouses_pickle_path = None
   for root, _, files in os.walk(season_path):
      for f in files:
         if "Clubhouses" in f and f.endswith(".pickle"):
            clubhouses_pickle_path = os.path.join(root, f)

   # Read data if available
   if clubhouses_pickle_path:
      with open(clubhouses_pickle_path, 'rb') as pickle_path:
         # Read pickle data
         pickle_data = pickle.load(pickle_path)
         pickle_data_df = pd.DataFrame()

         # Pickle data contains list of dictionaries
         for team_dict in pickle_data:
            # Multi-index dataframes
            skaters_df = team_dict['skaters_df']['Skaters']
            goalies_df = team_dict['goalies_df']['Goalies']
            pickle_data_df = pd.concat([pickle_data_df, skaters_df, goalies_df], axis=0, ignore_index=True)

   return pickle_data_df

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

def _get_statsapi_player_endpoint(statsapi_path, player_name, team, season_string):
   """ Retrieves the statsapi player endpoint link given the input information.
       Looks at the team roster data to find the player. Returns a statsapi
       endpoint link if player is found. Returns an empty string otherwise. """
   # TODO: This could be ported to a loader utility to abstract teams to ID mapping
   # TODO: Is this also inefficient since we're re-reading the entire file everytime?
   # Get the team ID given the team name
   team_id = None
   with open(os.path.join(statsapi_path, "teams_id_map.csv")) as f:
      dict_reader = csv.DictReader(f)
      teams_id_map_list = list(dict_reader)
      team_id = next((d['id'] for d in teams_id_map_list if d['abbreviation'] == team), None)

   # Return early if team mapping not found
   if team_id is None:
      return ""

   # Use ID to open team roster file for the given season
   team_roster_path = os.path.join(statsapi_path, season_string, "team_rosters", f"{season_string}_team{team_id}_roster.json")
   if not os.path.exists(team_roster_path):
      return ""

   # Read file and look for the player in the roster
   with open(team_roster_path, 'r') as f:
      data_dict = json.load(f)
      for player_dict in data_dict['teams'][0]['roster']['roster']:
         # At this point, we found a match for the player name and team for a given season
         # Note: There is an edge case where same player name could exist on the same team in the same season
         if player_dict['person']['fullName'] == player_name:
            return player_dict['person']['link']

   return ""

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