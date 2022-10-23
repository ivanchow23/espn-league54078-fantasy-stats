#!/usr/bin/env python
""" Parser to extract information for a given scoring_period.json file. """
from espn_fantasy_api_utils import STATS_MAP
import pandas as pd

class EspnFantasyApiScoringPeriodParser():
    def __init__(self, scoring_period_dict):
        """ Constructor. Takes in already-loaded dictionary from scoring period JSON file. """
        self._data_dict = scoring_period_dict
        self._scoring_period_id = self._data_dict['scoringPeriodId']

    def get_owner_roster_applied_stats_as_dicts(self, owner_id):
        """ For a given owner ID, return the current roster with some additional data
            as a list of dictionaries. Assumes one owner per team. """
        roster_dicts = []
        for team_roster in self._data_dict['teams']:
            if team_roster['owners'][0] != owner_id:
                continue

            # Append various information to list of dictionaries
            for roster_entry in team_roster['roster']['entries']:
                roster_dict = {'fullName': roster_entry['playerPoolEntry']['player']['fullName'],
                               'lineupSlotId': roster_entry['lineupSlotId'],
                               #'injuryStatus': roster_entry['injuryStatus'],
                               #'injured': roster_entry['playerPoolEntry']['player']['injured'],
                               #'player_injuryStatus': roster_entry['playerPoolEntry']['player']['injuryStatus']
                              }

                # First, get dictionary from list of stats that correspond to this scoring period ID
                applied_stats_dict = self._get_scoring_period_applied_stats_dict(roster_entry['playerPoolEntry']['player']['stats'])

                # Then, map applied stat indicies to actual names
                if applied_stats_dict is not None:
                    roster_dict.update(self._map_stats_index_to_names(applied_stats_dict['appliedStats']))
                    roster_dict['appliedTotal'] = applied_stats_dict['appliedTotal']

                roster_dicts.append(roster_dict)
        return roster_dicts

    def get_owner_roster_applied_stats_as_df(self, owner_id):
        """ For a given owner ID, return the current roster with some additional data
            as a dataframe. Assumes one owner per team. """
        return pd.DataFrame(self.get_owner_roster_applied_stats_as_dicts(owner_id))

    def _get_scoring_period_applied_stats_dict(self, stats_list):
        """ Given a list of stat dictionaries, retrieve just the dictionary
            that corresponds to the scoring period. """
        for stat in stats_list:
            if stat['scoringPeriodId'] == self._scoring_period_id:
                return stat
        return None

    def _map_stats_index_to_names(self, stats_dict):
        """ Converts each stat from a generic number to the actual stat name.
            Example: If 0 = "G", 1 = "A", 2 = "PTS"
                     {0: x, 1: y, 2: z} -> {'G': x, 'A': y, 'PTS': z} """
        return {STATS_MAP[int(key)]: val for key, val in stats_dict.items()}