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
import json
import os
import pandas as pd
import statsapi_logger
import sys
import timeit

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "utils"))
from requests_util import RequestsUtil

logger = statsapi_logger.logger()

class StatsapiDownloader():
    def __init__(self, root_output_folder, overwrite):
        """ Constructor. """
        self.TEAMS_MAPFILE_NAME = "teams_id_map.csv"
        self.PLAYERS_MAPFILE_NAME = "players_id_map.csv"

        self._root_output_folder = root_output_folder
        self._overwrite = overwrite
        self._teams_mapfile_path = os.path.join(self._root_output_folder, self.TEAMS_MAPFILE_NAME)
        self._players_mapfile_path = os.path.join(self._root_output_folder, self.PLAYERS_MAPFILE_NAME)

        self._req = RequestsUtil("https://statsapi.web.nhl.com")

        # Create root output folder where downloaded data be output
        os.makedirs(self._root_output_folder, exist_ok=True)

    @property
    def overwrite(self):
        """ Overwrite property and getter. """
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite):
        """ Overwrite setter. """
        self._overwrite = overwrite

    def download_teams_data(self):
        """ Download all teams data. This provides us with each team's ID.
            Downloaded file names have the form: "team<id>.json". Also
            generates a map file in the root directory to map teams to their
            unique ID. """
        # Output folder
        output_folder_path = os.path.join(self._root_output_folder, "teams")
        os.makedirs(output_folder_path, exist_ok=True)

        # Get data of current teams from server
        teams_dict = self._req.load_json_from_endpoint("/api/v1/teams")

        # Prepare links and output paths for download
        download_dict_list = [{'endpoint': d['link'],
                               'out_file_path': os.path.join(output_folder_path, f"team{d['id']}.json")}
                               for d in teams_dict['teams']]
        download_dict_list = self._check_download_dict_list(download_dict_list)

        # Download
        logger.info(f"Downloading to: {output_folder_path}")
        start_time = timeit.default_timer()
        num_saved = self._req.save_jsons_from_endpoints_async(download_dict_list)
        logger.info(f"Downloaded {num_saved} files in {round(timeit.default_timer() - start_time, 1)}s.")

        # Generate map file
        teams_id_map = [{'id': d['id'],
                         'name': d['name'],
                         'abbreviation': d['abbreviation']}
                         for d in teams_dict['teams']]

        teams_id_map_df = pd.DataFrame(teams_id_map)
        teams_id_map_df.to_csv(self._teams_mapfile_path, index=False)

    def download_team_rosters_data(self, season_string):
        """ Download all team rosters data for the given season. Downloaded
            files have the form: "XXXXYYYY_team<id>_roster.json", where
            XXXXYYYY is the season. Also generates a map file in the root
            directory to map players to their unique ID. This is done after
            the download step by gathering relevant data of all players from
            each rosters of the given season.

            Note: Depends on the teams ID map file to be present. Therefore,
            ensure download_teams_data() is called first. """
        # Output folder
        output_folder_path = os.path.join(self._root_output_folder, season_string, "team_rosters")
        os.makedirs(output_folder_path, exist_ok=True)

        # Read teams map file to retrieve IDs of interest
        teams_mapfile_df = pd.read_csv(self._teams_mapfile_path)
        team_id_list = list(teams_mapfile_df['id'])

        # Prepare links and output paths for download
        # Example link: https://statsapi.web.nhl.com/api/v1/teams/20?expand=team.roster&season=20122013
        download_dict_list = [{'endpoint': f"/api/v1/teams/{id}?expand=team.roster&season={season_string}",
                               'out_file_path': os.path.join(output_folder_path, f"{season_string}_team{id}_roster.json")}
                               for id in team_id_list]
        download_dict_list = self._check_download_dict_list(download_dict_list)

        # Download
        logger.info(f"Downloading to: {output_folder_path}")
        start_time = timeit.default_timer()
        num_saved = self._req.save_jsons_from_endpoints_async(download_dict_list)
        logger.info(f"Downloaded {num_saved} files in {round(timeit.default_timer() - start_time, 1)}s.")

        # Gather players data from each roster by reading back the downloaded rosters
        player_mapfile_dicts = []
        for f in os.listdir(output_folder_path):
            json_dict = json.load(open(os.path.join(output_folder_path, f), 'r'))

            try:
                for player in json_dict['teams'][0]['roster']['roster']:
                    player_mapfile_dicts.append({'id': player['person']['id'],
                                                  'Player': player['person']['fullName'],
                                                  'Team': json_dict['teams'][0]['abbreviation'],
                                                  # Convert season string to int to match how pandas
                                                  # read-back this column from CSV below
                                                  'Season': int(season_string),
                                                  'statsapi_endpoint': player['person']['link']})
            except KeyError:
                continue

        # Update/generate mapfile
        players_mapfile_df = pd.DataFrame()
        if os.path.exists(self._players_mapfile_path):
            players_mapfile_df = pd.read_csv(self._players_mapfile_path)

        # Append to dataframe, drop any duplicate entries (possible if downloading data
        # from the year and rosters already in mapfile), and output to CSV
        players_mapfile_df = pd.concat([players_mapfile_df, pd.DataFrame(player_mapfile_dicts)])
        players_mapfile_df = players_mapfile_df.drop_duplicates()
        players_mapfile_df.to_csv(self._players_mapfile_path, index=False)

    def download_players_data(self, season_string):
        """ Download players data for those on a roster for a given season.
            Downloaded files have the form: "player<id>.json".

            Note: Depends on the players ID map file to be present. Therefore,
            ensure download_team_rosters_data() is called first. """
        # Output folder
        output_folder_path = os.path.join(self._root_output_folder, "players")
        os.makedirs(output_folder_path, exist_ok=True)

        # Read players map file to retrieve mappings for given season
        players_mapfile_df = pd.read_csv(self._players_mapfile_path)
        players_id_list = list(players_mapfile_df[players_mapfile_df['Season'] == int(season_string)]['id'])

        # Prepare links and output paths for download
        # Example link: https://statsapi.web.nhl.com/api/v1/people/8478402
        download_dict_list = [{'endpoint': f"/api/v1/people/{id}",
                               'out_file_path': os.path.join(output_folder_path, f"player{id}.json")}
                               for id in players_id_list]
        download_dict_list = self._check_download_dict_list(download_dict_list)

        # Download
        logger.info(f"Downloading to: {output_folder_path}")
        start_time = timeit.default_timer()
        num_saved = self._req.save_jsons_from_endpoints_async(download_dict_list)
        logger.info(f"Downloaded {num_saved} files in {round(timeit.default_timer() - start_time, 1)}s.")

    def download_players_season_stats_data(self, season_string):
        """ Download players season stats data for a given season. Downloaded
            files have the form: "XXXXYYYY_player<id>_season_stats.json" where
            XXXXYYYY is the season.

            Note: Depends on the players ID map file to be present. Therefore,
            ensure download_team_rosters_data() is called first. """
        # Output folder
        output_folder_path = os.path.join(self._root_output_folder, season_string, "season_stats")
        os.makedirs(output_folder_path, exist_ok=True)

        # Read players map file to retrieve mappings for given season
        players_mapfile_df = pd.read_csv(self._players_mapfile_path)
        players_id_list = list(players_mapfile_df[players_mapfile_df['Season'] == int(season_string)]['id'])

        # Prepare links and output paths for download
        # Example link: https://statsapi.web.nhl.com/api/v1/people/8478402/stats?stats=statsSingleSeason&season=20192020
        download_dict_list = [{'endpoint': f"/api/v1/people/{id}/stats?stats=statsSingleSeason&season={season_string}",
                               'out_file_path': os.path.join(output_folder_path, f"{season_string}_player{id}_season_stats.json")}
                               for id in players_id_list]
        download_dict_list = self._check_download_dict_list(download_dict_list)

        # Download
        logger.info(f"Downloading to: {output_folder_path}")
        start_time = timeit.default_timer()
        num_saved = self._req.save_jsons_from_endpoints_async(download_dict_list)
        logger.info(f"Downloaded {num_saved} files in {round(timeit.default_timer() - start_time, 1)}s.")

    def _check_download_dict_list(self, download_dict_list):
        """ Checks the list of dictionaries consisting of URLs and output
            file paths. Removes duplicate URL links from the list. Returns
            a modified list of dictionaries if items were modified. Returns
            the original list back otherwise. """
        ret_list = []

        # First, remove duplicate dictionaries from the list
        # A duplicate is when the entire dictionary's contents are identical
        # Do this first so entries still exist to check in the return list
        for d in download_dict_list:
            if d not in ret_list:
                ret_list.append(d)

        # Check for entries we don't want to download if file already exists
        if not self._overwrite:
            ret_list = [d for d in ret_list if not os.path.exists(d['out_file_path'])]

        return ret_list

if __name__ == "__main__":
    """ Main function. """
    start_timer = timeit.default_timer()

    # Read arguments
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--start_year", "-s", required=True, type=int, help="Starting season of data to download.")
    arg_parse.add_argument("--end_year", "-e", required=True, type=int, help="End season of data to download.")
    arg_parse.add_argument("--output_path", "-o", required=True, type=str, help="Output path of where downloaded data will go.")

    args = arg_parse.parse_args()
    start_year = args.start_year
    end_year = args.end_year
    output_path = args.output_path

    # Instantiate
    statsapi_downloader = StatsapiDownloader(output_path, overwrite=False)

    # Download most up-to-date teams data
    statsapi_downloader.overwrite = True
    statsapi_downloader.download_teams_data()

    # Download relevant data for each season
    statsapi_downloader.overwrite = False
    for season in range(start_year, end_year + 1):
        # Example: The 2020 season will be "20202021"
        season_string = f"{season}{season + 1}"
        statsapi_downloader.download_team_rosters_data(season_string)
        statsapi_downloader.download_players_data(season_string)
        statsapi_downloader.download_players_season_stats_data(season_string)

    print(f"Finished in {round(timeit.default_timer() - start_timer, 1)}s.")