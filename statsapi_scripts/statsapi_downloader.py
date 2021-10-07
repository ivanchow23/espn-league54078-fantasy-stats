#!/usr/bin/env python
""" Contains functionality to download data from statsapi to local machine.
    Downloaded data has folder structure:

    statsapi_data_root_folder
    - teams
        -> team<id1>.json
        -> team<id2>.json
        -> ...
    - players
        -> player<id1>.json
        -> player<id2>.json
        -> ...
    - 20192020
      - team_rosters
        -> 20192020_team<id1>_roster.json
        -> 20192020_team<id2>_roster.json
      - player_gamelogs
        -> 20192020_player<id1>_gamelog.json
        -> 20192020_player<id2>_gamelog.json
        -> ...
      - player_season_stats
        -> 20192020_player<id1>_season_stats.json
        -> 20192020_player<id2>_season_stats.json
        -> ...
      - etc.

    - 20202021
      - team_rosters
        -> 20202021_team<id1>_roster.json
        -> 20202021_team<id2>_roster.json
      - player_gamelogs
        -> 20202021_player<id1>_gamelog.json
        -> 20202021_player<id2>_gamelog.json
        -> ...
      - player_season_stats
        -> 20202021_player<id1>_season_stats.json
        -> 20202021_player<id2>_season_stats.json
        -> ...
      - etc.
"""
import argparse
import csv
import pandas as pd
import os
import re
import statsapi_logger
import statsapi_utils
logger = statsapi_logger.logger()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

# Limit to prevent trying to access season data before this year
# Based on founding year: https://en.wikipedia.org/wiki/History_of_the_National_Hockey_League_(1917%E2%80%931942)
SEASON_START_YEAR_LIMIT = 1917

def download_teams_data(root_path, overwrite=False):
    """ Download all teams data into its own folder within the specified
        output path. Downloaded file names have the form: "team<id>.json".
        Also generates a map file in the root directory to map teams to
        their unique ID. Returns True on success. False otherwise. """
    # Output folder
    output_folder_path = _create_dir_if_not_exist(root_path, "teams")
    if not output_folder_path:
        logger.warning(f"Invalid path: {output_folder_path}. Skipping download.")
        return False

    # Get data of current teams from server
    teams_url = statsapi_utils.get_full_url("/api/v1/teams/")
    teams_dict = statsapi_utils.load_json_from_url(teams_url)
    total_team_dicts = len(teams_dict['teams'])

    # Iterate through each team and download
    teams_id_map = []
    for index, team_dict in enumerate(teams_dict['teams']):
        # Keep track of team IDs to generate map file
        teams_id_map.append({'id': team_dict['id'], 'name': team_dict['name'], 'abbreviation': team_dict['abbreviation']})

        # Download file
        output_file_path = os.path.join(output_folder_path, f"team{team_dict['id']}.json")
        url = statsapi_utils.get_full_url(team_dict['link'])
        info_str = _save_file(url, output_file_path, overwrite, file_counter=index + 1, total_files=total_team_dicts)
        logger.info(info_str)

    # Generate map file in root folder
    teams_id_map_df = pd.DataFrame(teams_id_map)
    teams_id_map_df.to_csv(os.path.join(root_path, "teams_id_map.csv"), index=False)
    return True

def download_players_data(root_path, in_file_path, overwrite=False):
    """ Download all players data into its own folder within the specified
        output path. Accepts an input CSV file with player information and
        statsapi endpoints used to access data from the server. Downloaded
        file names have the form: "player<id>.json". Also generates a map
        file in the root directory to map players to their unique ID. Returns
        True on success. False otherwise. """
    # Output folder
    output_folder_path = _create_dir_if_not_exist(root_path, "players")
    if not output_folder_path:
        logger.warning(f"Invalid path: {output_folder_path}. Skipping download.")
        return False

    # Check input file
    if not isinstance(in_file_path, str) or not os.path.exists(in_file_path) or not in_file_path.lower().endswith(".csv"):
        logger.warning(f"Invalid input file: {in_file_path}. Skipping download.")
        return False

    # Read file
    players_data_dict_list = _read_csv(in_file_path)
    if not players_data_dict_list:
        logger.warning("Invalid CSV input. Skipping download.")
        return False

    # Iterate through each endpoint and download
    total_players = len(players_data_dict_list)
    for index, player_dict in enumerate(players_data_dict_list):
        # Add new key for ID mapping
        player_dict['id'] = ""

        # Check endpoint pattern matches
        endpoint = player_dict['statsapi_endpoint']
        if not isinstance(endpoint, str) or not re.match(f"{statsapi_utils.API_ENDPOINT_PREFIX}/people/[0-9]+", endpoint):
            logger.warning(f"Invalid endpoint ({endpoint}). Skipping download.")
            continue

        # Parse ID from endpoint string
        id = re.findall(f"[0-9]+", endpoint)[-1]
        player_dict['id'] = id

        # Download file
        output_file_path = os.path.join(output_folder_path, f"player{id}.json")
        url = statsapi_utils.get_full_url(endpoint)
        info_str = _save_file(url, output_file_path, overwrite, file_counter=index + 1, total_files=total_players)
        logger.info(info_str)

    # Generate map file in root folder
    players_id_map_df = pd.DataFrame(players_data_dict_list)
    players_id_map_df.to_csv(os.path.join(root_path, "players_id_map.csv"), index=False)
    return True

def download_team_rosters_data(root_path, start_year, end_year, overwrite=False):
    """ Download all team rosters data into each year's folder within the specified
        output path for all seasons between the specified years. Downloaded files have
        the form: "XXXXYYYY_team<id>_roster.json" where XXXXYYYY is the season. Returns
        True on success. False otherwise.

        Example: start_year = 2018 end_year = 2020 will try and download data for the
        seasons: 20182019, 20192020, 20202021.

        Note: Depends on teams data to be present locally within the root path! Call
        download_teams_data() first. """
    # Error check
    if not _check_year_range(start_year, end_year):
        logger.warning(f"Invalid start/end year: start={repr(start_year)} end={repr(end_year)}. Skipping download.")
        return False

    # This function depends on teams data to be present locally
    # Check for prescence of teams folder and data
    teams_data_folder_path = os.path.join(root_path, "teams")
    if not os.path.exists(teams_data_folder_path):
        logger.warning(f"Cannot find teams data in {root_path}")
        logger.warning("Run the 'download_teams_data()' function first.")
        logger.warning("Skipping download.")
        return False

    # Look for files within teams folder and get list of all team IDs
    # File names are in a known format, so simply parse out ID from names rather than opening the file
    # Example: ["team1.json", "team10.json", "team23.json"] -> [1, 10, 23]
    # Reference: https://stackoverflow.com/a/4289557
    file_list = os.listdir(teams_data_folder_path)
    team_id_list = [int("".join(filter(str.isdigit, f))) for f in file_list]

    # Download progress counters
    file_counter = 0
    num_files = len(team_id_list) * (end_year + 1 - start_year)

    # Process each year
    for year in range(start_year, end_year + 1):
        # Current season is the current year + the next year
        # Example: The season for year 2018 is 2018-2019
        curr_season_string = f"{year}{year + 1}"

        # Output folder
        output_folder_path = _create_dir_if_not_exist(root_path, curr_season_string, "team_rosters")
        if not output_folder_path:
            logger.warning(f"Invalid path: {output_folder_path}. Skipping download.")
            return False

        # Iterate through each team and download
        # Example link: https://statsapi.web.nhl.com/api/v1/teams/20?expand=team.roster&season=20122013
        for id in team_id_list:
            file_counter += 1
            url = statsapi_utils.get_full_url(f"/api/v1/teams/{id}?expand=team.roster&season={curr_season_string}")
            output_file_path = os.path.join(output_folder_path, f"{curr_season_string}_team{id}_roster.json")
            info_str = _save_file(url, output_file_path, overwrite, file_counter=file_counter, total_files=num_files)
            logger.info(info_str)

    return True

def download_players_season_stats_data(root_path, overwrite=False):
    """ Read player mapping file generated from function:
        "download_players_data()" and downloads all player data into
        each season folder within the root path. Downloaded files have
        the form: "XXXXYYYY_player<id>_season_stats.json" where XXXXYYYY
        is the season. Returns True on success. False otherwise.
    """
    # Check if map file exists
    if not os.path.exists(os.path.join(root_path, "players_id_map.csv")):
        logger.warning(f"Cannot find players ID map file in: {root_path}. Skipping download.")
        return False

    # Read file
    players_data_dict_list = _read_csv(os.path.join(root_path, "players_id_map.csv"))
    if not players_data_dict_list:
        logger.warning("Invalid CSV input. Skipping download.")
        return False

    # Download progress counters
    file_counter = 0
    num_files = len(players_data_dict_list)

    # Process each player in list
    for player_dict in players_data_dict_list:
        # Read season, which is where folder of downloaded data goes
        season_string = ""
        try:
            season_string = player_dict['Season']
        except KeyError:
            logger.warning("Key error in file. Skipping download.")
            return False

        output_folder_path = _create_dir_if_not_exist(root_path, season_string, "season_stats")
        if not output_folder_path:
            logger.warning(f"Invalid path: {output_folder_path}. Skipping download.")
            return False

        # Example link: https://statsapi.web.nhl.com/api/v1/people/8478402/stats?stats=statsSingleSeason&season=20192020
        file_counter += 1
        id = player_dict['id']
        endpoint = player_dict['statsapi_endpoint']
        output_file_path = os.path.join(output_folder_path, f"{season_string}_player{id}_season_stats.json")
        url = f"{statsapi_utils.get_full_url(endpoint)}/stats?stats=statsSingleSeason&season={season_string}"
        info_str = _save_file(url, output_file_path, overwrite, file_counter=file_counter, total_files=num_files)
        logger.info(info_str)

    return True

def _create_dir_if_not_exist(root_path, *dirs):
    """ Helper function that creates "nested" directories within the root. Handles if
        directory already exists and other basic errors. Returns a path if directory
        already exists or if it is successfully created. Returns None otherwise.

        Examples:
          _create_dir_if_not_exist("root", "folder") -> "root/folder"
          _create_dir_if_not_exist("root", "dir1", "dir2") -> "root/dir1/dir2"
          _create_dir_if_not_exist("root", "dir1", "dir2", "dir3") -> "root/dir1/dir2/dir3" """
    if not root_path:
        return None

    try:
        output_folder_path = os.path.join(root_path, *dirs)
        os.makedirs(output_folder_path, exist_ok=True)
        return output_folder_path
    except(OSError, TypeError):
        return None

def _read_csv(file_path):
    """ Helper function to read a CSV file. Returns list of dictionaries
        data structure on success. None otherwise. """
    # Required headers to be present in the input file
    required_headers = ["Player", "statsapi_endpoint"]

    # Read file and return list of dictionaries
    players_data_dict_list = []
    with open(file_path, 'r', encoding='utf-8') as csv_file:
        dict_reader = csv.DictReader(csv_file)
        file_headers = dict_reader.fieldnames
        if not file_headers or not set(required_headers).issubset(set(file_headers)):
            logger.warning(f"Input file does not contain required headers. Requires: {required_headers}.")
            return None

        return list(dict_reader)

def _check_year_range(start_year, end_year):
    """ Helper function to check the start and end year ranges for seasons.
        Returns True if inputs and range are valid. False otherwise. """
    # Error check
    if not isinstance(start_year, int) or not isinstance(end_year, int) or start_year > end_year:
        logger.debug(f"Invalid start/end year: start={repr(start_year)} end={repr(end_year)}.")
        return False

    # Limit access attempt before a certain year
    if start_year < SEASON_START_YEAR_LIMIT:
        logger.warning(f"Start year ({start_year}) must be >= {SEASON_START_YEAR_LIMIT}")
        return False

    return True

def _save_file(url, output_file_path, overwrite, file_counter=0, total_files=0):
    """ Helper function that saves data from the given URL to the output file path.
        Does not access and save data if overwrite flag is false.

        Also returns a string for download progress. This is returned so the original
        caller can make logger output "more correctly" show which function is actually
        downloading the data (rather than this one). """
    # Build string for logger
    info_string = ""
    if total_files != 0:
        info_string += f"[{file_counter}/{total_files}] "

    # If file already exists locally, skip
    if not overwrite:
        if os.path.exists(output_file_path):
            info_string += f"{output_file_path} exists. Skipping."
            return info_string

    # Save team data
    if statsapi_utils.save_json_from_url(url, output_file_path):
        info_string += f"Downloaded to: {output_file_path}"
        return info_string
    else:
        # Generic error message - relying on utility logger messages
        info_string += "Cannot download data."
        return info_string

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("-o", required=True, help="Root directory for all downloaded data.")
    arg_parser.add_argument("--start_year", required=False, type=int, help="Starting year used for downloading season data.")
    arg_parser.add_argument("--end_year", required=False, type=int, help="Ending year used for downloading season data.")
    arg_parser.add_argument("--players_file", required=False, help="CSV file path to list of players with statsapi endpoints for downloading player data.")
    arg_parser.add_argument("--overwrite", required=False, action='store_true', help="Flag to overwrite all existing files when downloading.")
    args = arg_parser.parse_args()

    # Store arguments
    root_data_folder = args.o
    start_year = args.start_year
    end_year = args.end_year
    players_file_path = args.players_file
    ow = args.overwrite

    # Download data
    download_teams_data(root_data_folder, overwrite=ow)
    download_players_data(root_data_folder, players_file_path, overwrite=ow)
    download_team_rosters_data(root_data_folder, start_year=start_year, end_year=end_year, overwrite=ow)
    download_players_season_stats_data(root_data_folder, overwrite=ow)