#!/usr/bin/env python
""" Test stat that finds a list of number of players drafted that remained on the final team/roster. """
import argparse
import os
import pandas as pd
import re

LEAGUE_ROSTER_FILE_NAME_RE = r"League Rosters - [\W\w]+ - All Players.csv"

if __name__ == "__main__":
    """ Usage: Enter folder containing folders of data from each season. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', required=True, help="Input directory containing folders of data of each season.")
    args = arg_parser.parse_args()
    root_folder_path = args.d

    # Find all folders in root
    season_folders = [d for d in os.listdir(root_folder_path) if os.path.isdir(os.path.join(root_folder_path, d))]

    # Large dataframe of all players
    players_df = pd.DataFrame()

    # Iterate over all folders
    for season_folder in season_folders:
        # Full path of folder
        full_season_path = os.path.join(root_folder_path, season_folder)

        # Find files in folder path
        league_roster_file_path = None
        for f in os.listdir(full_season_path):
            if re.match(LEAGUE_ROSTER_FILE_NAME_RE, f):
                league_roster_file_path = os.path.join(full_season_path, f)

        # Check file exists
        if not os.path.exists(league_roster_file_path):
            print("Cannot find: {}. Skipping...".format(league_roster_file_path))
            continue

        # Read file
        league_roster_df = pd.read_csv(league_roster_file_path)

        # Drop rows where players were not drafted
        try:
            league_roster_df = league_roster_df[league_roster_df['ACQ'] == "Draft"]
        # Some files don't have this column (legacy caveman drafting)
        except KeyError:
            # Intentional pass - Assume all players are drafted if acquisition data is not available
            pass

        # Append to player list dataframe
        players_df = pd.concat([players_df, league_roster_df[['Player', 'Position']]], axis=0)

    # Count number of unique players drafted
    player_counts_df = players_df.value_counts().reset_index()
    player_counts_df.rename(columns={0: 'Counts'}, inplace=True)

    # Sort counts by player name alphabetically - Note: Important that "Counts" column comes first
    player_counts_df = player_counts_df.sort_values(['Counts', 'Position', 'Player'], ascending=[False, True, True])
    player_counts_df.to_csv("player_counts.csv", index=False)