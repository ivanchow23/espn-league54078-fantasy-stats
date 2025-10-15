#!/usr/bin/env python
""" Loads dictionary that's from the json that contains all players data. """
from espn_fantasy_api_utils import STATS_MAP
import pandas as pd

class EspnFantasyApiAllPlayersInfoParser():
    def __init__(self, season_string, all_players_info_dict):
        """ Constructor. Takes in already-loaded dictionary from all players info JSON file """
        self._season_year = str(season_string[4:])
        self._data_dict = all_players_info_dict

    def get_all_players_info_as_dicts(self):
        """ Return all players with some additional data as a list of dictionaries """
        all_players_dicts = []
        player_stat = {}
        for player in self._data_dict['players']:
            try:
                for stat in player['player']['stats']:
                    if stat['id'] == f"00{self._season_year}":
                        player_stat = stat
                        continue
            except KeyError:
                 continue

            all_players_dict = {'fullName': player['player']['fullName'],
                               'totalPoints': player_stat.get('appliedTotal')}

            all_players_dict.update(self._map_stats_index_to_names(player_stat.get('stats', {})))
            all_players_dicts.append(all_players_dict)

        return all_players_dicts

    def get_all_players_info_as_df(self):
        """ Return all players with some additional data as a dataframe"""
        return pd.DataFrame(self.get_all_players_info_as_dicts())

    def _map_stats_index_to_names(self, stats_dict):
        """ Converts each stat from a generic number to the actual stat name.
            Example: If 0 = "G", 1 = "A", 2 = "PTS"
                     {0: x, 1: y, 2: z} -> {'G': x, 'A': y, 'PTS': z} """
        return {STATS_MAP[int(key)]: val for key, val in stats_dict.items()}