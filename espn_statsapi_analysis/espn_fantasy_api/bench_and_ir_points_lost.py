""" Finds the points lost per owner per season due to leaving a player
    on IR or the bench. """
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
# Calculate points lost leaving player on IR/bench per season for each owner
for season, season_df in daily_rosters_df.groupby('season'):
    for owner, owner_df in season_df.groupby('owner'):
        # Filter for bench slots, which seems to be ID = 7
        bench_df = owner_df[owner_df['lineupSlotId'] == 7]
        bench_pts = int(bench_df['appliedTotal'].sum())

        # Filter for IR slots, which seems to be ID = 8
        ir_df = owner_df[owner_df['lineupSlotId'] == 8]
        ir_pts = int(ir_df['appliedTotal'].sum())

        # Print totals
        print(f"{season}: {owner} left {bench_pts + ir_pts} points on the bench/IR (bench: {bench_pts} IR: {ir_pts})")

        # Break down bench points
        bench_pts = []
        for player, player_df in bench_df.groupby('fullName'):
            bench_pts.append({'player': player,
                              'gp': _get_num_games_played(player_df),
                              'pts': int(player_df['appliedTotal'].sum())})

        # Sort by descending points for printing purposes
        bench_pts = sorted(bench_pts, key=lambda d: d['pts'], reverse=True)
        for pts in bench_pts:
            if pts['pts'] != 0:
                print(f"{pts['player']}: {pts['pts']} points in {pts['gp']} games ({round(pts['pts'] / pts['gp'], 2)} pts/game) (bench)")

        # Break down IR points
        ir_pts = []
        for player, player_df in ir_df.groupby('fullName'):
            ir_pts.append({'player': player,
                           'gp': _get_num_games_played(player_df),
                           'pts': int(player_df['appliedTotal'].sum())})

        # Sort by descending points for printing purposes
        ir_pts = sorted(ir_pts, key=lambda d: d['pts'], reverse=True)
        for pts in ir_pts:
            if pts['pts'] != 0:
                print(f"{pts['player']}: {pts['pts']} points in {pts['gp']} games ({round(pts['pts'] / pts['gp'], 2)} pts/game) (IR)")

        # Formatting purposes
        print()