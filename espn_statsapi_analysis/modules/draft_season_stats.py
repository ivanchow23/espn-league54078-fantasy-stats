#!usr/bin/env python
from .draft import Draft
import os
import sys

class DraftSeasonStats(Draft):
    """ Class for processing draft and player's season stats. """
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        # Invoke parent class to load required data
        super().__init__(espn_loader, statsapi_loader, out_path)

        # Data to operate on and accompanying metadata
        self._df = self._load_df()

    def process(self):
        """ Process data. """
        # Output raw dataframe
        self._df.to_csv(os.path.join(self._out_path, "draft_season_stats_df.csv"), index=False)

    def _load_df(self):
        """ Loads and prepares all relevant data into a dataframe. """
        combined_df = self._draft_df

        # Load player season stats data for all entries for all seasons
        combined_df['GP'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'games'), axis=1)

        combined_df['G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'goals'), axis=1)

        combined_df['A'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'assists'), axis=1)

        combined_df['PTS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'points'), axis=1)

        combined_df['+/-'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'plusMinus'), axis=1)

        combined_df['PIM'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'pim'), axis=1)

        combined_df['HITS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'hits'), axis=1)

        combined_df['W'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'wins'), axis=1)

        combined_df['L'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'losses'), axis=1)

        combined_df['SO'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shutouts'), axis=1)

        return combined_df

    def _get_player_season_stat(self, player_season_stats_dict, key):
        """ Returns the value given a dictionary of the player's season stats
            and the key corresponding to the stat. Note: Error handling is
            extremely basic. Meant simple usage to get basic stat keys. Does
            not differentiate between skaters and goalies (can technically
            try accessing goalie wins stats on a skater). """
        if player_season_stats_dict is None:
            return None

        try:
            return player_season_stats_dict['stats'][0]['splits'][0]['stat'][key]
        except KeyError:
            return None
        except IndexError:
            return None