#!/usr/bin/env python
""" Utility to load statsapi downloaded data. """
import csv
import json
import os
import statsapi_logger

logger = statsapi_logger.logger()

class StatsapiLoader():
    """ Holds a reference to the root statsapi data folder and provides
        APIs to load data from it. This is a counterpart to the statsapi
        downloader script. Assumes the general data folder structure:

        root_folder
          players
          teams
          players_id_map
          teams_id_map
          20192020
            - team_rosters
            - etc.
          20202021
            - team_rosters
            - etc.
    """
    def __init__(self, root_folder_path):
        """ Constructor. Takes in path to root data folder. """
        self._root_folder_path = root_folder_path
        self._players_map_dicts = self._read_csv_as_dicts(os.path.join(root_folder_path, "players_id_map.csv"))
        self._teams_map_dicts = self._read_csv_as_dicts(os.path.join(root_folder_path, "teams_id_map.csv"))

    def load_player_dict(self, player_name, team=None, season_string=None):
        """ Loads data about the given player as a dictionary.
            Optional parameters are to be more specific in the search
            in case there are multiple players with the same name. """
        id = self._get_player_id(player_name, team, season_string)
        if id == -1:
            return None

        return self._load_json(os.path.join(self._root_folder_path, "players", f"player{id}.json"))

    def load_player_season_stats_dict(self, player_name, season_string, team=None):
        """ Loads season stats for a given player and season as a
            dictionary. Optional parameters are to be more specific in
            the search in case there are multiple players with the same
            name. """
        id = self._get_player_id(player_name, team, season_string)
        if id == -1:
            return None

        return self._load_json(os.path.join(self._root_folder_path, season_string, "season_stats",
                               f"{season_string}_player{id}_season_stats.json"))

    def _load_json(self, file_path):
        """ Helper function to load a JSON file.
            Returns None on failure. """
        if not os.path.exists(file_path):
            logger.warning(f"Cannot load from {file_path}")
            return None

        return json.load(open(file_path))

    def _get_player_id(self, player_name, team=None, season_string=None):
        """ Returns the player ID from the player map file. """
        if self._players_map_dicts is None:
            return -1

        for d in self._players_map_dicts:
            ret = False
            if d['Player'] == player_name:
                if team is None and season_string is None:
                    return int(d['id'])
                elif team is not None and season_string is None:
                    if d['Team'] == team:
                        return int(d['id'])
                elif team is None and season_string is not None:
                    if d['Season'] == season_string:
                        return int(d['id'])
                else:
                    if d['Team'] == team and d['Season'] == season_string:
                        return int(d['id'])
        return -1

    def _read_csv_as_dicts(self, file_path):
        """ Reads a CSV file as a list of dictionaries.
            Returns None on failure. """
        if not self._check_path(file_path):
            logger.warning(f"Cannot open: {file_path}")
            return None

        with open(file_path, 'r', encoding='utf-8') as csv_file:
            dict_reader = csv.DictReader(csv_file)
            return list(dict_reader)

    def _check_path(self, path):
        """ Helper function to test if a path is valid or exists. """
        if not isinstance(path, str) or not os.path.exists(path):
            return False
        return True

