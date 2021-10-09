#!/usr/bin/env python
""" Test stat that gets draft order information for each season. """
import argparse
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
from espn_loader import EspnLoader

def _number_ordinal(val):
    """ Simple function to convert an integer to a "numerical ordinal" string.
        Example: 1, 2, 3, 4 -> 1st, 2nd, 3rd, 4th. """
    if val == 1:
        return "1st"
    elif val == 2:
        return "2nd"
    elif val == 3:
        return "3rd"
    else:
        return f"{val}th"

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--espn', required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    args = arg_parser.parse_args()
    espn_root_path = args.espn

    # Initialize
    espn_loader = EspnLoader(espn_root_path)

    # Get all seasons in root folder and combine into single dataframe
    combined_df = pd.DataFrame()
    combined_first_place_df = pd.DataFrame()
    for season_string in os.listdir(espn_root_path):
        # Load draft information
        draft_df = espn_loader.load_draft_recap_data(season_string)
        if draft_df is None:
            continue

        # Load league standings
        standings_dict = espn_loader.load_league_standings_data(season_string)
        if standings_dict is None:
            continue

        # Only need first place team
        standings_df = standings_dict['season_points']
        standings_df = standings_df['Team Info']
        standings_df = standings_df.rename(columns={'Owner': 'Owner Name'})
        standings_df['Season'] = season_string
        combined_first_place_df = pd.concat([combined_first_place_df, standings_df[standings_df['RK'] == 1]], ignore_index=True)

        # Only need first round information to determine draft order
        first_round_df = draft_df[draft_df['Round Number'] == 1]
        first_round_df['Season'] = season_string
        combined_df = pd.concat([combined_df, first_round_df], ignore_index=True)

    # Get draft position of each year the player has won
    winners_draft_pos_df = combined_first_place_df.merge(combined_df, on=['Owner Name', 'Season'], how='inner')
    winners_draft_pos_df = winners_draft_pos_df[['Team Name', 'Owner Name', 'Season', 'Draft Number', 'Player', 'Team_y']]
    winners_draft_pos_df.to_csv("winner_draft_pos_df.csv", index=False)

    # Plot pie chart of each owner's draft positions over the years
    combined_df.to_csv("test.csv")
    num_owners = len(combined_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 5))
    colour_map = {"1st": "tab:blue", "2nd": "tab:orange", "3rd": "tab:green",
                  "4th": "tab:red", "5th": "tab:purple", "6th": "tab:cyan",
                  "7th": "tab:pink"}
    for index, (owner, df) in enumerate(combined_df.groupby('Owner Name')):
        # Draft number column indicates draft order since we are
        # only counting the first round here
        series = df['Draft Number'].value_counts().sort_index()

        # Change the index to use ordinal numbering
        # Example:
        # Index  Count  ->  Index  Count
        # 1      2          1st    2
        # 2      0          2nd    0
        # 3      1          3rd    1
        # 4      0          4th    0
        series.index = series.index.map(_number_ordinal)

        # Pie chart colour mappings
        wedge_colours = [colour_map[pos] for pos in series.index]

        # Generate pie chart
        ax[index].pie(series, labels=series.index, autopct='%1.1f%%',
                      wedgeprops={'edgecolor': "white", 'linewidth': 0.75},
                      textprops={'fontsize': "small"}, colors=wedge_colours)

        ax[index].set_title(owner)
        legend_labels = [f"{pos}: {series[pos]}/{series.sum()}" for pos in series.index]
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='small')

    plt.suptitle("Owner's Draft Position (2015 - 2020)")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "draft_order_positions.png"))