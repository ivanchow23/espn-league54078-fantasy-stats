#!/usr/bin/env python
""" Test stat that finds average draft position of each player drafted. """
import argparse
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
        combined_df = pd.concat([combined_df, draft_df], ignore_index=True)

    # Operate on data
    grouped_df = combined_df.groupby(['Player'])['Draft Number'].agg(['mean', 'min', 'max', 'count']).round(0)
    grouped_df = grouped_df.rename(columns={'mean': 'Average Draft Position',
                                            'min': 'Highest Position',
                                            'max': 'Lowest Position',
                                            'count': '# Times Drafted'})

    grouped_df = grouped_df.sort_values(by='Average Draft Position')
    grouped_df.to_csv("avg_draft_pos.csv")