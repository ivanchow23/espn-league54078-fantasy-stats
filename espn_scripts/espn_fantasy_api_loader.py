#!/usr/bin/env python
from espn_fantasy_api_utils import STATS_MAP
import json
import os

class EspnFantasyApiLoader():
    """ Holds a reference to the root ESPN fantasy API data folder and provides APIs
    to load data from it. Assumes the following general structure in data folder:

        root_folder
          20192020
            - league_info.json
            - scoring_periods
              -> 20192020_scoring_period1.json
              -> 20192020_scoring_period2.json
              -> ...
            - realtime_stats
            - ...
          20202021
            - league_info.json
            - scoring_periods
              -> 20202021_scoring_period1.json
              -> 20202021_scoring_period2.json
              -> ...
            - realtime_stats
            - ...
    """
    def __init__(self, root_folder_path):
        """ Constructor. Takes in path to root data folder. """
        self._root_folder_path = root_folder_path

    def get_members_id_map(self, season_string):
        """ Returns a dictionary mapping of IDs to members for given season.
            Dictionary has the form: {'<id1>': <name>, '<id2>': <name> .. } """
        league_info_dict = self._load_json(season_string, f"{season_string}_league_info.json")
        if league_info_dict is None:
            return None

        return {m['id']: f"{m['firstName']} {m['lastName']}" for m in league_info_dict['members']}

    def get_applied_stats_map(self, season_string):
        """ Returns a dictionary mapping of stats IDs to stats for the stats kept track
            of a given season. """
        league_info_dict = self._load_json(season_string, f"{season_string}_league_info.json")
        if league_info_dict is None:
            return None

        stats_map = {}
        for s in league_info_dict['settings']['scoringSettings']['scoringItems']:
            stats_map[s['statId']] = {'stat': STATS_MAP[s['statId']], 'points': s['points']}

        return stats_map

    def get_league_info_dict(self, season_string):
        """ Returns a dictionary of the league information for the given season. """
        return self._load_json(season_string, f"{season_string}_league_info.json")

    def get_scoring_period_dict(self, season_string, id):
        """ Returns a dictionary for the given scoring period of a season. """
        return self._load_json(season_string, "scoring_periods", f"{season_string}_scoring_period{id}.json")

    def _load_json(self, season_string, *args):
        """ Reads a JSON file as dictionary from given season and arguments.
            Example: self._load_json(20202021, "20202021_league_info.json")
            Example: self._load_json(20202021, "scoring_periods", "20202021_scoring_period1.json") """
        file_path = os.path.join(self._root_folder_path, season_string, *args)
        if not os.path.exists(file_path):
            return None

        # Handle special case of data in different format for older seasons
        if int(season_string) < 2018:
            return json.load(open(file_path, 'r'))[0]
        else:
            return json.load(open(file_path, 'r'))