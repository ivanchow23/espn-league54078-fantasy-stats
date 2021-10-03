#!/usr/bin/env python
""" Test stat that finds each owner's draft information. """
import argparse
from matplotlib import pyplot as plt
import os
import pandas as pd
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
from espn_loader import EspnLoader
from statsapi_loader import StatsapiLoader

def _get_player_info(player_dict, key):
    """ Takes in a dictionary from statsapi loaded JSON file and looks
        for data in the given key under the "people" key. This is where
        most of a player's information exists. """
    if player_dict is None:
        return None

    try:
        return player_dict['people'][0][key]
    except KeyError:
        return None

def _get_player_age(player_dict, season_string):
    """ Takes in a dictionary from statsapi loaded JSON file and
        calculates the player's rough age at the current time of the
        given season. Does this by simply taking the difference between
        player's birth year and the start of the season.

        Example: Birth year = 1995-07-23, Season = 20202021
                 Age = 2020 - 1995 = 25
    """
    # String from data dict expected to be in the form "YYYY-MM-DD"
    # Parse for YYYY
    birth_date_string = _get_player_info(player_dict, 'birthDate')
    if birth_date_string is None:
        return None
    birth_year = int(birth_date_string[0:4])

    # Season string expected to be in the form: "XXXXYYYY"
    # Parse for start of season XXXX
    season = int(season_string[0:4])

    return season - birth_year

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('--espn', required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    arg_parser.add_argument('--statsapi', required=True, help="Root path of downloaded statsapi data.")
    args = arg_parser.parse_args()
    espn_root_path = args.espn
    statsapi_root_path = args.statsapi

    # Initialize
    espn_loader = EspnLoader(espn_root_path)
    statsapi_loader = StatsapiLoader(statsapi_root_path)

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

    # Add additional player information to dataframe
    combined_df['Player Birth Country'] = combined_df['Player'].apply(lambda player: _get_player_info(statsapi_loader.load_player_dict(player), 'birthCountry'))
    combined_df['Player Age'] = combined_df.apply(lambda x: _get_player_age(statsapi_loader.load_player_dict(x['Player']), x['Season']), axis=1)
    combined_df.to_csv(os.path.join(SCRIPT_DIR, "owner_draft_picks_combined_df.csv"))

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

    # Generate pie chart of each owner's draft pick's birth countries
    num_owners = len(combined_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
    colour_map = {"CAN": "indianred", "USA": "royalblue", "RUS": "snow",
                  "SWE": "gold", "FIN": "navy", "CZE": "lightblue",
                  "CHE": "firebrick", "DEU": "dimgray"}
    for index, (owner, df) in enumerate(combined_df.groupby('Owner Name')):
        series = df['Player Birth Country'].value_counts()
        wedge_colours = [colour_map[country] if country in colour_map else "darkgray" for country in series.index]

        # Show only the top 5 labels on pie chart to not cram text for smaller wedges
        labels = list(series.index[0:5]) + ["" for i in range(5, len(series.index))]

        # Generate pie chart
        ax[index].pie(series, labels=labels,
                      wedgeprops={'edgecolor': "white", 'linewidth': 1},
                      textprops={'fontsize': "small"}, colors=wedge_colours)

        # Generate legend and titles
        total_count = series.sum()
        legend_labels = [f"{country}: {round((series[country] / total_count) * 100, 1)}%" for country in series.index]
        ax[index].set_title(owner)
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

    plt.suptitle("Owner \"Portfolio\" of Drafted Player's Birth Country")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "owners_drafted_players_birth_country.png"))

    # Total pie chart of nationality
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    series = combined_df['Player Birth Country'].value_counts()
    total_count = series.sum()

    # Show only the top 5 labels on pie chart to not cram text for smaller wedges
    labels = list(series.index[0:5]) + ["" for i in range(5, len(series.index))]
    wedge_colours = [colour_map[country] if country in colour_map else "darkgray" for country in series.index]
    ax.pie(series, labels=labels,
           wedgeprops={'edgecolor': "white", 'linewidth': 1},
           textprops={'fontsize': "small"}, colors=wedge_colours)
    legend_labels = [f"{country}: {round((series[country] / total_count) * 100, 1)}%" for country in series.index]
    ax.legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

    plt.suptitle("Total \"Portfolio\" of All Drafted Player's Birth Country\n")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "all_drafted_players_birth_country.png"))

    # Generate pie chart of each owner's draft pick's age groups
    # Note: pd.cut function: left interval is exclusive, right is inclusive
    age_bins = [17, 22, 27, 32, 37, 100]
    age_bin_labels = ["18-22", "23-27", "28-32", "33-37", "> 37"]
    num_owners = len(combined_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 4))
    for index, (owner, df) in enumerate(combined_df.groupby('Owner Name')):
        binned_data = pd.cut(df['Player Age'], bins=age_bins, labels=age_bin_labels)
        series = binned_data.value_counts().sort_index()

        # Generate pie chart
        ax[index].pie(series, labels=series.index,
                      wedgeprops={'edgecolor': "white", 'linewidth': 1},
                      textprops={'fontsize': "small"})

        # Generate legend and titles
        total_count = series.sum()
        legend_labels = [f"{age_bin}: {round((series[age_bin] / total_count) * 100, 1)}%" for age_bin in series.index]
        ax[index].set_title(owner)
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='small')

    plt.suptitle("Owner \"Portfolio\" of Drafted Player's Age Groups")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "owners_drafted_players_age_groups.png"))

    # Generate histogram of each owner's draft pick's ages
    num_owners = len(combined_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
    for index, (owner, df) in enumerate(combined_df.groupby('Owner Name')):
        # Histogram stats
        mean = round(df['Player Age'].mean(), 1)
        min = int(df['Player Age'].min())
        max = int(df['Player Age'].max())

        ax[index].hist(df['Player Age'], density=True)
        ax[index].set_title(owner)
        ax[index].set_xlim([16, 45])
        ax[index].set_ylim([0, 0.2])
        ax[index].set_xlabel("Age")
        ax[index].set_ylabel("% of Draft Picks")
        ax[index].minorticks_on()
        ax[index].grid()

        legend_labels = [f"Min: {min}\nAvg: {mean}\nMax: {max}"]
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, -0.1), fontsize='small')

    plt.suptitle("Owner Drafted Player's Age Histograms")
    plt.tight_layout()
    plt.savefig(os.path.join(SCRIPT_DIR, "owners_drafted_players_age_histogram.png"))
