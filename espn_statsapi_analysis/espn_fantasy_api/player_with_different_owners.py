""" Analyzes if any players had multiple owners (due to trade, FA, etc.)
    every season and calculate the points scored for each owner. """
# %%
# Imports
#!/usr/bin/env python
import json
from pathlib import Path
import pandas as pd

# %%
# Declare helper functions
def _get_num_games_played(season_player_df):
    """ Get number of games played given dataframe of a season. """
    # First, filter out for all n/a entries in applied stats
    df = season_player_df.dropna(subset=['appliedTotal'])

    # Next, filter out entries that have 0 applied total stats but for
    # some reason has n/a entries for every other stat
    df = df[~((df['appliedTotal'] == 0) & (df[['G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']].isna().all(axis=1) == True))]
    return len(df)
# %%
# Configurations
daily_rosters_df_path = "espn_fantasy_api_daily_rosters_df.csv"
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Go through each season and filter for players who was on multiple owner teams
for season, season_df in daily_rosters_df.groupby('season'):
    for player, player_df in season_df.groupby('fullName'):
        # Player was on multiple teams
        num_teams = len(player_df['owner'].unique())
        if num_teams > 1:
            total_gp = _get_num_games_played(player_df)
            total_pts = int(player_df['appliedTotal'].sum())
            total_pts_per_game = round(total_pts / total_gp, 1) if total_gp != 0 else 0
            print(f"{season}: {player} was on {num_teams} teams. {total_pts} total points in {total_gp} games (pts/game={total_pts_per_game}).")

            for owner, df in player_df.groupby('owner'):
                gp = _get_num_games_played(df)
                pts = int(df['appliedTotal'].sum())
                pts_per_game = round(pts / gp, 1) if gp != 0 else 0
                print(f"{player} playing for {owner} had {pts} points in {gp} games (pts/game={pts_per_game}).")

            # Print extra line for formatting
            print()