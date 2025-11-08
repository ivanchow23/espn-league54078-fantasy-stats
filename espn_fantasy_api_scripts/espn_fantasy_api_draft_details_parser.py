#!/usr/bin/env python
""" Loads dictionary that's from the json that contains draft details. """
from espn_fantasy_api_utils import STATS_MAP
from espn_fantasy_api_loader import EspnFantasyApiLoader
import pandas as pd

class EspnFantasyApiDraftDetailsParser():
    def __init__(self, draft_details_dict):
        """ Constructor. Takes in already-loaded dictionary from draft details JSON file """
        self._data_dict = draft_details_dict

    def get_draft_details_as_dicts(self):
        """ Return draft details as a list of dictionaries """
        draft_details_dict = []
        for picks in self._data_dict['draftDetail']['picks']:
            draft_details_dict.append({
                'Draft Number': picks['overallPickNumber'],
                'Round Pick Number': picks['roundPickNumber'],
                'Round Number': picks['roundId'],
                'Owner ID': picks['teamId'],
                'Player ID': picks['playerId'],
            })

        return draft_details_dict

    def get_draft_details_as_df(self):
        """ Return draft details as a dataframe """
        return pd.DataFrame(self.get_draft_details_as_dicts())