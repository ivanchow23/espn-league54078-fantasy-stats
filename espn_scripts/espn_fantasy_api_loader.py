#!/usr/bin/env python
import json
import os

# Scoring stats map (Reference: https://github.com/cwendt94/espn-api)
STATS_MAP = {
    0: 'GS',
    1: 'W',
    2: 'L',
    3: 'SA',
    4: 'GA',
    5: '5',
    6: 'SV',
    7: 'SO',
    8: 'MIN ?',
    9: 'OTL',
    10: 'GAA',
    11: 'SV%',
    12: '12',
    13: 'G',
    14: 'A',
    15: '+/-',
    16: '16',
    17: 'PIM',
    18: 'PPG',
    19: '19',
    20: 'SHG',
    21: 'SHA',
    22: 'GWG',
    23: 'FOW',
    24: 'FOL',
    25: '25',
    26: 'TTOI ?',
    27: 'ATOI',
    28: 'HAT',
    29: 'SOG',
    30: '30',
    31: 'HIT',
    32: 'BLK',
    33: 'DEF',
    34: 'GP',
    35: '35',
    36: '36',
    37: '37',
    38: 'PPP',
    39: 'SHP',
    40: '40',
    41: '41',
    42: '42',
    43: '43',
    44: '44',
    45: '45',
    99: '99'
    }

class EspnFantasyApiLoader():
    """ Holds a reference to the root ESPN fantasy API data folder and provides APIs
    to load data from it. Assumes the following general structure in data folder:

        root_folder
          2019
            - league_info.json
            - scoring_periods
              -> 2019_scoring_period1.json
              -> 2019_scoring_period2.json
              -> ...
            - realtime_stats
            - ...
          2020
            - league_info.json
            - scoring_periods
              -> 2020_scoring_period1.json
              -> 2020_scoring_period2.json
              -> ...
            - realtime_stats
            - ...
    """
    def __init__(self, root_folder_path):
        """ Constructor. Takes in path to root data folder. """
        self._root_folder_path = root_folder_path

    def get_members_id_map(self, year_string):
        """ Returns a dictionary mapping of IDs to members for given year.
            Dictionary has the form: {'<id1>': <name>, '<id2>': <name> .. } """
        league_info_dict = self._load_json(year_string, f"{year_string}_league_info.json")
        if league_info_dict is None:
            return None

        return {m['id']: f"{m['firstName']} {m['lastName']}" for m in league_info_dict['members']}

    def get_applied_stats_map(self, year_string):
        """ Returns a dictionary mapping of stats IDs to stats for the stats kept track
            of a given year. """
        league_info_dict = self._load_json(year_string, f"{year_string}_league_info.json")
        if league_info_dict is None:
            return None

        stats_map = {}
        for s in league_info_dict['settings']['scoringSettings']['scoringItems']:
            stats_map[s['statId']] = {'stat': STATS_MAP[s['statId']], 'points': s['points']}

        return stats_map

    def get_league_info_dict(self, year_string):
        """ Returns a dictionary of the league information for the given year. """
        return self._load_json(year_string, f"{year_string}_league_info.json")

    def get_scoring_period_dict(self, year_string, id):
        """ Returns a dictionary for the given scoring period of a year. """
        return self._load_json(year_string, "scoring_periods", f"{year_string}_scoring_period{id}.json")

    def _load_json(self, year_string, *args):
        """ Reads a JSON file as dictionary from given year and arguments.
            Example: self._load_json(2020, "2020_league_info.json")
            Example: self._load_json(2020, "scoring_periods", "2020_scoring_period1.json") """
        file_path = os.path.join(self._root_folder_path, year_string, *args)
        if not os.path.exists(file_path):
            return None

        # Handle special case of data in different format for older seasons
        if int(year_string) < 2018:
            return json.load(open(file_path, 'r'))[0]
        else:
            return json.load(open(file_path, 'r'))