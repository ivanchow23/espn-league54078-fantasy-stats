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

def download_teams_data(root_path, overwrite=False):
    """ Download teams data into its own folder within the specified output path. 
        Downloaded file names have the form: "team<id>.json" 
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

    # Iterate through each team and download files
    for index, team_dict in enumerate(teams_dict['teams']):
        output_file_path = os.path.join(output_folder_path, f"team{team_dict['id']}.json")
        url = statsapi_utils.get_full_url(team_dict['link'])
        info_str = _save_file(url, output_file_path, overwrite, curr_file_idx=index, total_files=total_team_dicts)
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

def _save_file(url, output_file_path, overwrite, curr_file_idx=0, total_files=0):
    """ Helper function that saves data from the given URL to the output file path.
        Does not access and save data if overwrite flag is false. 
        
        Also returns a string for download progress. This is returned so the original
        caller can make logger output "more correctly" show which function is actually
        downloading the data (rather than this one). """
    # Build string for logger
    info_string = ""
    if total_files != 0:
        info_string += f"[{curr_file_idx + 1}/{total_files}] "

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
    download_teams_data("statsapi_data")