""" Script to analyze results and performance of traded players.
    Assumes basic configurations: 1 to 1 player trades and players
    who got traded are known. """
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
season_of_interest = 20212022
player1_of_interest = "Claude Giroux"
player2_of_interest = "Evgeni Malkin"
print(f"Analyzing trade results between: {player1_of_interest} and {player2_of_interest} in {season_of_interest}")

# %%
# Read data
daily_rosters_df = pd.read_csv(daily_rosters_df_path)

# %%
# Filter data for seasons of interest only
season_daily_rosters_df = daily_rosters_df[daily_rosters_df['season'] == season_of_interest]

# %%
# Filter rows where player 1 and player 2 are present on the rosters
player1_roster_df = season_daily_rosters_df[season_daily_rosters_df['fullName'] == player1_of_interest]
player2_roster_df = season_daily_rosters_df[season_daily_rosters_df['fullName'] == player2_of_interest]

# %%
# Ensure roster data is in chronological order
player1_roster_df = player1_roster_df.sort_values(by='scoringPeriodId')
player2_roster_df = player2_roster_df.sort_values(by='scoringPeriodId')

# %%
# Print out stats for player 1 on each owner's team
player1_num_games_total = _get_num_games_played(player1_roster_df)
print(f"{player1_of_interest}'s original owner is {player1_roster_df['owner'].iloc[0]}")
print(f"{player1_of_interest} had {player1_roster_df['appliedTotal'].sum()} total points in {player1_num_games_total} games.")
for owner, player_df in player1_roster_df.groupby('owner'):
    num_games = _get_num_games_played(player_df)
    print(f"{player1_of_interest} playing for {owner} had {player_df['appliedTotal'].sum()} points in {num_games} games.")

# %%
# Print out stats for player 2 on each owner's team
player2_num_games_total = _get_num_games_played(player2_roster_df)
print(f"{player2_of_interest}'s original owner is {player2_roster_df['owner'].iloc[0]}")
print(f"{player2_of_interest} had {player2_roster_df['appliedTotal'].sum()} total points in {player2_num_games_total} games.")
for owner, player_df in player2_roster_df.groupby('owner'):
    num_games = _get_num_games_played(player_df)
    print(f"{player2_of_interest} playing for {owner} had {player_df['appliedTotal'].sum()} points in {num_games} games.")