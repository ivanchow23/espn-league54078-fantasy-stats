#!/usr/bin/env python
""" ESPN fantasy API daily rosters data generator script.
    Generates daily roster data for analysis purposes. """
import argparse
from espn_fantasy_api_loader import EspnFantasyApiLoader
from espn_fantasy_api_scoring_period_parser import EspnFantasyApiScoringPeriodParser
from espn_fantasy_api_scoring_period_util import EspnFantasyApiScoringPeriodUtil
import os
import pandas as pd

class EspnFantasyApiDailyRostersDataGenerator():
    def __init__(self, espn_fantasy_api_downloads_root_path, out_dir):
        """ Constructor. Takes in a root path to ESPN fantasy API downloads and
            output folder where generated data will go. """
        self._root_path = espn_fantasy_api_downloads_root_path
        self._out_dir = out_dir
        self._loader = EspnFantasyApiLoader(self._root_path)

    def generate(self):
        """ Generates data. """
        # Combine all daily roster data into a single large dataframe
        combined_roster_dfs = pd.DataFrame()

        # Loop through each available season's worth of data
        for season_string in self._loader.get_seasons():
            # Get owner ID mappings
            owner_id_map = self._loader.get_members_id_map(season_string)

            # Get scoring period start and ends
            scoring_period_start = self._loader.get_league_info_dict(season_string)['status']['firstScoringPeriod']
            scoring_period_end = min(self._loader.get_league_info_dict(season_string)['status']['latestScoringPeriod'],
                                     self._loader.get_league_info_dict(season_string)['status']['finalScoringPeriod'])

            # Store roster data for each scoring period and owner
            scoring_period_util = EspnFantasyApiScoringPeriodUtil()
            for scoring_period in range(scoring_period_start, scoring_period_end + 1):
                print(f"Processing {season_string} Scoring Period ID {scoring_period}/{scoring_period_end}")
                for owner_id in owner_id_map:
                    # Parse roster dataframe from scoring period data
                    scoring_period_parser = EspnFantasyApiScoringPeriodParser(self._loader.get_scoring_period_dict(season_string, scoring_period))
                    roster_df = scoring_period_parser.get_owner_roster_applied_stats_as_df(owner_id)

                    # Add some more metadata to roster dataframe
                    roster_df['scoringPeriodId'] = scoring_period
                    roster_df['date'] = scoring_period_util.get_scoring_period_date(season_string, scoring_period)
                    roster_df['owner'] = owner_id_map[owner_id]
                    roster_df['season'] = season_string

                    # Combine to overall dataframe
                    combined_roster_dfs = pd.concat([combined_roster_dfs, roster_df])

        combined_roster_dfs.to_csv(os.path.join(self._out_dir, "espn_fantasy_api_daily_rosters_df.csv"), index=False)

if __name__ == "__main__":
    """ Main runner script. """
    argparser = argparse.ArgumentParser()
    argparser.add_argument("-i", required=True, help="Root path of ESPN fantasy API downloaded data.")
    argparser.add_argument("-o", required=True, help="Path to folder where output data will go.")
    args = argparser.parse_args()

    data_generator = EspnFantasyApiDailyRostersDataGenerator(args.i, args.o)
    data_generator.generate()
    print("Done.")