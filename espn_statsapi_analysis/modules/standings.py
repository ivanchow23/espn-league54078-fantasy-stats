#!/usr/bin/env python
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
from .utils.plot_pie import PlotPie

SCRIPT_DIR = os.path.join(os.path.abspath(__file__))
PLOT_BACKEND = 'matplotlib'

# Suppress verbose logger messages from matplotlib
plt.set_loglevel('WARNING')

class Standings():
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        self._espn_loader = espn_loader
        self._statsapi_loader = statsapi_loader
        self._out_path = out_path
        os.makedirs(self._out_path, exist_ok=True)

        self._standings_dict = self._load_standings_dict()
        self._standings_points_df = self._load_standings_points_df()
        self._standings_stats_df = self._load_standings_stats_df()

    def process(self):
        """ Process data. """
        # Output raw dataframes
        self._standings_points_df.to_csv(os.path.join(self._out_path, "standings_points_df.csv"), index=False)
        self._standings_stats_df.to_csv(os.path.join(self._out_path, "standings_stats_df.csv"), index=False)

        # Generate stats
        season_standings_performance(self._standings_points_df, self._out_path)
        owner_standings_placement(self._standings_points_df, self._out_path)

    def _load_standings_dict(self):
        """ Loads and prepares all relevant data into dictionary of
            dataframes. Each season's league standings data are in a
            slightly different format, so organize based on seasons.

            Example return:
            { '20182019': {'season_points': df, 'season_stats': df},
              '20192020': {'season_points': df, 'season_stats': df},
              '20202021': {'season_points': df, 'season_stats': df}
            }

            This is to load all the data as close to the rawest form
            as possible without losing specific columns from certain
            seasons. Another method may be required to filter and
            combine only the necessary data as needed.
        """
        # Initialize
        standings_dict = {}

        # Load standings information and combine into respective dataframes
        for season_string in self._espn_loader.get_seasons():
            standings_dict[season_string] = {}

            league_standings_dict = self._espn_loader.load_league_standings_data(season_string)
            if league_standings_dict is None or len(league_standings_dict) == 0:
                continue

            standings_dict[season_string]['season_points'] = league_standings_dict['season_points']
            standings_dict[season_string]['season_stats'] = league_standings_dict['season_stats']

        return standings_dict

    def _load_standings_points_df(self):
        """ Load season standings points as a dataframe. Combines all
            seasons into a single dataframe. Assumes standings
            dictionary is already loaded to operate on. """
        combined_df = pd.DataFrame()
        for season_string in self._standings_dict.keys():
            if self._standings_dict[season_string] == {}:
                continue

            # Dataframes are multi-index columns
            # Drop the top level before combining
            df = self._standings_dict[season_string]['season_points']
            df.columns = df.columns.droplevel(0)

            # Insert column of season information
            df.insert(0, 'Season', season_string)

            # Combine dataframe
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        return combined_df

    def _load_standings_stats_df(self):
        """ Load season standings stats as a dataframe. Combines all
            seasons into a single dataframe. Assumes standings
            dictionary is already loaded to operate on. """
        combined_df = pd.DataFrame()
        for season_string in self._standings_dict.keys():
            if self._standings_dict[season_string] == {}:
                continue

            # Dataframes are multi-index columns
            # Drop the top level before combining
            df = self._standings_dict[season_string]['season_stats']
            df.columns = df.columns.droplevel(0)

            # Insert column of season information
            df.insert(0, 'Season', season_string)

            # Combine dataframe
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        return combined_df

def _number_ordinal(val):
    """ Simple function to convert an integer to a "numerical ordinal"
        string. Example: 1, 2, 3, 4 -> 1st, 2nd, 3rd, 4th. """
    if val == 1:
        return "1st"
    elif val == 2:
        return "2nd"
    elif val == 3:
        return "3rd"
    else:
        return f"{val}th"

def season_standings_performance(input_df, out_path):
    """ Plots each owner's season performance based on % away from
        average and % away from first place. """
    # First, normalize points for each season
    norm_df = pd.DataFrame()
    for season_string, season_df in input_df.groupby('Season'):
        season_norm_df = season_df

        # Normalize by average and highest points
        season_norm_df['Normalized By Average'] = round(season_norm_df['TOT'] / season_norm_df['TOT'].mean(), 3)
        season_norm_df['Normalized By Max'] = round(season_norm_df['TOT'] / season_norm_df['TOT'].max(), 3)

        # Combine normalized dataframe
        norm_df = pd.concat([norm_df, season_norm_df], ignore_index=True)

    # Plot
    fig, ax = plt.subplots(2, 1, figsize=(16, 9))
    for owner, owner_df in norm_df.groupby('Owner'):
        avg = round(owner_df['Normalized By Average'].mean(), 2)
        min = round(owner_df['Normalized By Average'].min(), 2)
        max = round(owner_df['Normalized By Average'].max(), 2)
        std = round(owner_df['Normalized By Average'].std(), 3)
        ax[0].plot(owner_df['Season'], owner_df['Normalized By Average'], '-o', label=f"{owner} (Avg: {avg}, Min: {min}, Max: {max}, Std: {std})")

        avg = round(owner_df['Normalized By Max'].mean(), 2)
        min = round(owner_df['Normalized By Max'].min(), 2)
        max = round(owner_df['Normalized By Max'].max(), 2)
        std = round(owner_df['Normalized By Max'].std(), 3)
        ax[1].plot(owner_df['Season'], owner_df['Normalized By Max'], '-o', label=f"{owner} (Avg: {avg}, Min: {min}, Max: {max}, Std: {std})")

    ax[0].set_title("Normalized by Average vs. Season")
    ax[0].set_xlabel("Season")
    ax[0].set_ylabel("% Average (1 = Average, Units = Decimal)")
    ax[0].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax[0].grid()

    ax[1].set_title("Normalized by First vs. Season")
    ax[1].set_xlabel("Season")
    ax[1].set_ylabel("% From First (1 = First Place, Units = Decimal)")
    ax[1].legend(loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')
    ax[1].grid()

    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "season_standing_performance_normalized_plots.png"))

def owner_standings_placement(input_df, out_path):
    """ Pie charts showing distribution of each owner's placement in the
        standings over the years. """
    # Assumes min. and max. seasons to be the range of the available data
    seasons_range_string = f"{input_df['Season'].min()} - {input_df['Season'].max()}"

    # Set-up pie plots
    colour_map = {"1st": '#ffd700',
                  "2nd": '#b0c4de',
                  "3rd": '#d2b48c'}
    pie = PlotPie(out_path, backend=PLOT_BACKEND, wedge_colour_map=colour_map)

    # Number of times each owner had a certain draft position
    input_data_dicts = []
    for owner, df in input_df.groupby('Owner'):
        input_data_dicts.append({'sub_title': owner, 'df': df['RK'].apply(_number_ordinal)})

    pie.plot_pies(input_data_dicts, fig_w=1600, fig_h=500, title=f"Standings Placements\n{seasons_range_string}",
                  image_name="owner_standings_placement_pie.png")