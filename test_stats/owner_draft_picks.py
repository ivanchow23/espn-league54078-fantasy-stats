#!/usr/bin/env python
""" Test stat that finds each owner's draft information. """
import argparse
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
from espn_loader import EspnLoader

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--espn', required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    args = arg_parser.parse_args()
    espn_root_path = args.espn

    # Initialize
    espn_loader = EspnLoader(espn_root_path)

    # Get all seasons in root folder and combine into single dataframe
    combined_df = pd.DataFrame()
    for season_string in os.listdir(espn_root_path):
        # Load draft information
        draft_df = espn_loader.load_draft_recap_data(season_string)
        if draft_df is None:
            continue

        # Append season information and combine to master dataframe
        draft_df['Season'] = season_string
        combined_df = pd.concat([combined_df, draft_df], ignore_index=True)

    combined_df.to_csv(os.path.join(SCRIPT_DIR, "combined.csv"))

    # Get number of times same owner drafted same player
    # Note: value_counts returns a series
    owner_player_counts_df = combined_df.value_counts(subset=['Owner Name', 'Player']).to_frame().reset_index()
    owner_player_counts_df = owner_player_counts_df.rename(columns={0: '# Times Drafted'})
    multi_df = pd.DataFrame()
    for owner, df in owner_player_counts_df.groupby('Owner Name'):
        df = df.drop(columns='Owner Name').reset_index(drop=True)
        new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], df.columns]))
        new_df[owner] = df
        multi_df = pd.concat([multi_df, new_df], axis=1)
    multi_df.to_csv(os.path.join(SCRIPT_DIR, "owner_player_draft_picks.csv"), index=False)

    # Get number of times owner drafted someone from same team
    # Note: Function value_counts returns a series
    owner_team_counts_df = combined_df.value_counts(subset=['Owner Name', 'Team']).to_frame().reset_index()
    owner_team_counts_df = owner_team_counts_df.rename(columns={0: '# Times Drafted'})
    multi_df = pd.DataFrame()
    for owner, df in owner_team_counts_df.groupby('Owner Name'):
        df = df.drop(columns='Owner Name').reset_index(drop=True)
        new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], df.columns]))
        new_df[owner] = df
        multi_df = pd.concat([multi_df, new_df], axis=1)
    multi_df.to_csv(os.path.join(SCRIPT_DIR, "owner_team_draft_picks.csv"), index=False)