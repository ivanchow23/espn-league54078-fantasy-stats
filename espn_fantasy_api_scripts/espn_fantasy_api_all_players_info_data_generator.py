#!/usr/bin/env python
""" ESPN fantasy API all players data generator script.
    Generates current players data for analysis purposes. """
import argparse
from espn_fantasy_api_scripts.espn_fantasy_api_loader import EspnFantasyApiLoader
from espn_fantasy_api_scripts.espn_fantasy_api_all_players_info_parser import EspnFantasyApiAllPlayersInfoParser
import os
import pandas as pd

class EspnFantasyApiAllPlayersInfoDataGenerator():
    def __init__(self, espn_fantasy_api_downloads_root_path, out_dir):
        """ Constructor. Takes in a root path to ESPN fantasy API downloads and
            output folder where generated data will go. """
        self._root_path = espn_fantasy_api_downloads_root_path
        self._out_dir = out_dir
        self._loader = EspnFantasyApiLoader(self._root_path)

    def generate(self):
        """ Generates all players data. """
        # Combine all daily roster data into a single large dataframe
        all_seasons_players_dfs = pd.DataFrame()

        # Loop through each available season's worth of data
        for season_string in self._loader.get_seasons():
            print(f"Processing {season_string} Player Data")
            all_players_parser = EspnFantasyApiAllPlayersInfoParser(season_string, self._loader.get_all_players_info_dict(season_string))
            all_players_df = all_players_parser.get_all_players_info_as_df()

            # Add some more metadata to roster dataframe
            all_players_df['season'] = season_string

            # Combine to overall dataframe
            all_seasons_players_dfs = pd.concat([all_seasons_players_dfs, all_players_df])

        all_seasons_players_dfs.to_csv(os.path.join(self._out_dir, "espn_fantasy_api_all_players_info_df.csv"), index=False)

if __name__ == "__main__":
    """ Main runner script. """
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", required=True, help="Root path of ESPN fantasy API downloaded data.")
    argparser.add_argument("-o", required=True, help="Path to folder where output data will go.")
    args = argparser.parse_args()

    data_generator = EspnFantasyApiAllPlayersInfoDataGenerator(args.i, args.o)
    data_generator.generate()
    print("Done.")