#!/usr/bin/env python
""" Finds "performance" of each owner in each season. """
import argparse
from matplotlib import pyplot as plt
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

    # Get standings for each season
    combined_df = pd.DataFrame()
    for season_string in os.listdir(espn_root_path):
        season_standings_df = espn_loader.load_league_standings_data(season_string)

        # Add season column to identify this dataframe section
        season_standings_df['Season'] = season_string

        # Calculate stats for each owner
        season_standings_df['% Average'] = round(season_standings_df['Points'] / season_standings_df['Points'].mean(), 3)
        season_standings_df['% From First'] = round(season_standings_df['Points'] / season_standings_df['Points'].max(), 3)
        combined_df = pd.concat([combined_df, season_standings_df], ignore_index=True)

    # Create new column multi-indexed dataframe with owners at the "top level"
    owners_performance_df = pd.DataFrame()
    for owner_name, df in combined_df.groupby('Owner Name'):
        # First, drop redudant owner column
        df = df.drop(columns='Owner Name')

        # Next, set season column as the index
        df = df.set_index('Season')

        # Next, create a column multi-index dataframe using owner name as the top-level
        owner_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner_name], df.columns]))
        owner_df[owner_name] = df
        owners_performance_df = pd.concat([owners_performance_df, owner_df], axis=1)

    # Output raw data
    owners_performance_df.to_csv(os.path.join(SCRIPT_DIR, "season_standings_performance.csv"))

    # Plot % points stats vs. season for each owner
    fig, ax = plt.subplots(2, 1, figsize=(16, 9))
    for owner in owners_performance_df.columns.unique(level=0):
        owner_df = owners_performance_df[owner]

        avg = round(owner_df['% Average'].mean(), 2)
        min = round(owner_df['% Average'].min(), 2)
        max = round(owner_df['% Average'].max(), 2)
        std = round(owner_df['% Average'].std(), 3)
        ax[0].plot(owner_df.index, owner_df['% Average'], '-o', label=f"{owner} (Avg: {avg}, Min: {min}, Max: {max}, Std: {std})")

        avg = round(owner_df['% From First'].mean(), 2)
        min = round(owner_df['% From First'].min(), 2)
        max = round(owner_df['% From First'].max(), 2)
        std = round(owner_df['% From First'].std(), 3)
        ax[1].plot(owner_df.index, owner_df['% From First'], '-o', label=f"{owner} (Avg: {avg}, Min: {min}, Max: {max}, Std: {std})")

    ax[0].set_title("% Average vs. Season")
    ax[0].set_xlabel("Season")
    ax[0].set_ylabel("% Average")
    ax[0].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax[0].grid()

    ax[1].set_title("% From First vs. Season")
    ax[1].set_xlabel("Season")
    ax[1].set_ylabel("% From First")
    ax[1].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax[1].grid()

    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "season_standing_performance_%plots.png"))

    # Plot pie chart of distribution of ranks for each owner
    num_owners = len(owners_performance_df.columns.unique(level=0))
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 5))
    for index, owner in enumerate(owners_performance_df.columns.unique(level=0)):
        # Get counts of ranks
        owner_df = owners_performance_df[owner]
        rank_counts_series = owner_df['Rank'].value_counts().sort_index()

        # # Change the index to use ordinal numbering
        # # Example:
        # # Index  Count  ->  Index  Count
        # # 1      2          1st    2
        # # 2      0          2nd    0
        # # 3      1          3rd    1
        # # 4      0          4th    0
        rank_counts_series.index = rank_counts_series.index.map(_number_ordinal)

        # Pie chart colour mappings
        rank_colour_map = {'1st': "gold", '2nd': "lightsteelblue", '3rd': "tan"}
        wedge_colours = [rank_colour_map[rank] if rank in rank_colour_map else "darkgray" for rank in rank_counts_series.index]

        # Generate pie chart
        ax[index].pie(rank_counts_series, labels=rank_counts_series.index, autopct='%1.1f%%',
                      wedgeprops={'edgecolor': "white", 'linewidth': 0.75}, textprops={'fontsize': "small"}, colors=wedge_colours)

        # Generate labels for legend that displays number of times an owner achieved a rank
        total_times = rank_counts_series.sum()
        legend_labels = [f"{rank}: {rank_counts_series[rank]}/{total_times} times" for rank in rank_counts_series.index]
        ax[index].set_title(owner)
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='small')

    plt.suptitle("Rank Distributions\n(% of an Owner's Placement in Standings When in the League)")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "season_standing_performance_rank_distributions.png"))