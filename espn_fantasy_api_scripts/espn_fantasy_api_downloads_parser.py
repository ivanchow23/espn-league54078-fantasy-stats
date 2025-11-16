#!/usr/bin/env python
""" Parser class to wrap various ESPN fantasy API parsers to generate data for all seasons.

    Folder structure is expected to have the form:

    <espn_fantasy_api_downloads_root_folder>
    - 20242025
      -> scoring_periods
      -> 20242025_all_players_info.json
      -> 20242025_draft_details.json
      -> 20242025_league_info.json
      ...
    - 20252026
      -> scoring_periods
      -> 20252026_all_players_info.json
      -> 20252026_draft_details.json
      -> 20252026_league_info.json
      ...

"""
from espn_fantasy_api_scripts.espn_fantasy_api_all_players_info_parser import EspnFantasyApiAllPlayersInfoParser
from espn_fantasy_api_scripts.espn_fantasy_api_draft_details_parser import EspnFantasyApiDraftDetailsParser
from espn_fantasy_api_scripts.espn_fantasy_api_loader import EspnFantasyApiLoader
from espn_fantasy_api_scripts.espn_fantasy_api_scoring_period_parser import EspnFantasyApiScoringPeriodParser
import json
import multiprocessing
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class EspnFantasyApiDownloadsParser():
    def __init__(self, espn_fantasy_api_downloads_root_folder):
        """ Default constructor. """
        self._root_folder = espn_fantasy_api_downloads_root_folder
        self._loader = EspnFantasyApiLoader(espn_fantasy_api_downloads_root_folder)
        self._seasons = self._loader.get_seasons()

    def get_seasons(self):
        """ Returns number of seasons of data available in ESPN fantasy API downloads folder. """
        return self._seasons

    def get_draft_details_df(self):
        """ Returns a dataframe of draft details for all seasons. """
        combined_df = pd.DataFrame()
        for season_string in self._seasons:
            draft_details_dict = self._loader.get_draft_details_dict(season_string)
            if draft_details_dict is not None:
                draft_details_parser = EspnFantasyApiDraftDetailsParser(draft_details_dict)
                df = draft_details_parser.get_draft_details_as_df()
                df['Season'] = int(season_string)
                combined_df = pd.concat([combined_df, df])

        return combined_df

    def get_all_players_info_df(self):
        """ Returns a dataframe of all players info for all seasons. """
        combined_df = pd.DataFrame()
        for season_string in self._seasons:
            all_players_info_dict = self._loader.get_all_players_info_dict(season_string)
            if all_players_info_dict is not None:
                all_players_info_parser = EspnFantasyApiAllPlayersInfoParser(season_string, all_players_info_dict)
                df = all_players_info_parser.get_all_players_info_as_df()
                df['Season'] = int(season_string)
                combined_df = pd.concat([combined_df, df])

        return combined_df

    def get_daily_rosters_df(self, progress_func_handlers=None, multiprocess=True):
        """ Returns a dataframe of all daily rosters for all seasons.
            Provides function handler callbacks for caller to check
            progress. progress_func_handlers must be a dict of handlers
            where each key corresponds to the season being processed
            (use get_seasons() to check available seasons). """
        combined_roster_dfs = pd.DataFrame()

        if not multiprocess:
            # Loop through each available season's worth of data
            for season_string in self._seasons:
                df = self.get_daily_rosters_df_by_season(season_string, progress_func_handlers[season_string])
                combined_roster_dfs = pd.concat([combined_roster_dfs, df])
        else:
            # Use multiprocessing to process each available season's data
            pool = multiprocessing.Pool(processes=len(self._seasons))
            results = []
            for season_string in self._seasons:
                async_result = pool.apply_async(func=self.get_daily_rosters_df_by_season, args=(season_string, progress_func_handlers[season_string]))
                results.append(async_result)

            pool.close()
            pool.join()

            combined_roster_dfs = pd.concat([res.get() for res in results])

        return combined_roster_dfs

    def get_daily_rosters_df_by_season(self, season_string, progress_func_handler):
        """ Returns a dataframe of all daily rosters for a given season.
            Provides a function handler for caller to check progress. """
        combined_roster_dfs = pd.DataFrame()

        # Get owner ID mappings
        owner_id_map = self._loader.get_members_id_map(season_string)

        # Get league info
        league_info_dict = self._loader.get_league_info_dict(season_string)
        if league_info_dict is None:
            return combined_roster_dfs

        # Get scoring period start and ends
        scoring_period_start = league_info_dict['status']['firstScoringPeriod']
        scoring_period_end = min(league_info_dict['status']['latestScoringPeriod'], league_info_dict['status']['finalScoringPeriod'])

        # Store roster data for each scoring period and owner
        for scoring_period in range(scoring_period_start, scoring_period_end + 1):
            for owner_id in owner_id_map:
                # Parse roster dataframe from scoring period data
                scoring_period_dict = self._loader.get_scoring_period_dict(season_string, scoring_period)
                if scoring_period_dict is None:
                    continue

                scoring_period_parser = EspnFantasyApiScoringPeriodParser(scoring_period_dict)
                roster_df = scoring_period_parser.get_owner_roster_applied_stats_as_df(owner_id)

                # Add some more metadata to roster dataframe
                roster_df['scoringPeriodId'] = scoring_period
                roster_df['owner'] = owner_id_map[owner_id]
                roster_df['season'] = season_string

                # Combine to overall dataframe
                combined_roster_dfs = pd.concat([combined_roster_dfs, roster_df])

            # Provide information for progress processing
            if progress_func_handler is not None:
                progress_func_handler(season_string, scoring_period, scoring_period_end)

        return combined_roster_dfs

    def get_athletes_df(self):
        """ Returns a datarame of all downloaded athletes data. """
        athlete_dicts = []
        folder_path = os.path.join(self._root_folder, "athletes")
        for f in os.listdir(folder_path):
            file_path = os.path.join(folder_path, f)
            if not os.path.isfile(file_path):
                continue

            athlete_dict = json.load(open(file_path, 'r')).get('athlete', {})
            if not athlete_dict:
                continue

            athlete_dicts.append({'Player ID': float(athlete_dict.get('id')), # Cast to float in case there is "nan"
                                  'Player Name': athlete_dict.get('fullName'),
                                  'Player Birth Place': athlete_dict.get('displayBirthPlace'),
                                  'Player Height': athlete_dict.get('displayHeight'),
                                  'Player Weight': athlete_dict.get('displayWeight'),
                                  'Player DOB': athlete_dict.get('displayDOB')})

        return pd.DataFrame(athlete_dicts)

if __name__ == "__main__":
    """ Main function for testing and debugging. """
    espn_fantasy_api_downloads_parser = EspnFantasyApiDownloadsParser(os.path.join(SCRIPT_DIR, "espn_fantasy_api_downloads"))

    print("Processing draft details...")
    espn_fantasy_api_downloads_parser.get_draft_details_df().to_csv("draft_details.csv", index=False)
    print("Done.")

    print("Processing all players info...")
    espn_fantasy_api_downloads_parser.get_all_players_info_df().to_csv("all_players_info.csv", index=False)
    print("Done.")

    print("Processing athletes data...")
    espn_fantasy_api_downloads_parser.get_athletes_df().to_csv("athletes.csv", index=False)
    print("Done.")

    print("Processing daily rosters...")
    espn_fantasy_api_downloads_parser.get_daily_rosters_df().to_csv("daily_rosters.csv", index=False)
    print("Done.")