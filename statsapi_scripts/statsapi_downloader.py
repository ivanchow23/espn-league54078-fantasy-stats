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
import os
import statsapi_logger
import statsapi_utils
logger = statsapi_logger.logger()

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_ROOT_DATA_FOLDER = os.path.join(SCRIPT_DIR, "statsapi_data")

# Limit to prevent trying to access season data before this year
# Based on founding year: https://en.wikipedia.org/wiki/History_of_the_National_Hockey_League_(1917%E2%80%931942) 
SEASON_START_YEAR_LIMIT = 1917

def download_teams_data(root_path, overwrite=False):
    """ Download all teams data into its own folder within the specified 
        output path. Downloaded file names have the form: "team<id>.json" 
        Returns True on success. False otherwise. """
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
    for index, team_dict in enumerate(teams_dict['teams']):
        output_file_path = os.path.join(output_folder_path, f"team{team_dict['id']}.json")
        url = statsapi_utils.get_full_url(team_dict['link'])
        info_str = _save_file(url, output_file_path, overwrite, file_counter=index + 1, total_files=total_team_dicts)
        logger.info(info_str)
    
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
        info_string = f"Error downloading data."
        return info_string

if __name__ == "__main__":
    """ Main function. """
    download_teams_data(DEFAULT_ROOT_DATA_FOLDER)
    download_team_rosters_data(DEFAULT_ROOT_DATA_FOLDER, start_year=2015, end_year=2016)