#!usr/bin/env python
from .draft import Draft
from .utils.matplotlib_pie import MatplotlibPie
from .utils.matplotlib_histogram import MatplotlibHistogram
import os
import pandas as pd

class DraftHeight(Draft):
    """ Class for processing draft and player's height related data. """
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        # Invoke parent class to load required data
        super().__init__(espn_loader, statsapi_loader, out_path)

    def process(self):
        # Output raw dataframe
        self._draft_df.to_csv(os.path.join(self._out_path, "draft_df.csv"), index=False)

        # Set-up plots
        hist = MatplotlibHistogram(self._out_path)

        # League's overall distribution of drafted player's height
        hist.plot_histogram(self._draft_df['Player Height (cm)'], figsize=(8, 6),
                            title=f"League's Overall Distribution of Drafted Player's Height\n{self._season_range_string}",
                            xlabel="Height (cm)", ylabel="% of Picks",
                            image_name="draft_height_league_overall_histogram.png")

        # Each owner's overall distribution of drafted player's height
        input_data_dicts = []
        for owner, df in self._draft_df.groupby('Owner Name'):
            input_data_dicts.append({'sub_title': owner, 'df': df['Player Height (cm)'],
                                     'xlabel': "Height (cm)", 'ylabel': "% of Picks"})
        hist.plot_histograms(input_data_dicts, figsize=(16, 6),
                             title=f"Each Owner's Overall Distribution of Drafted Player's Height\n{self._season_range_string}",
                             image_name="draft_height_owners_overall_histogram.png")

        # Each owner's per-season distribution of drafted player's height
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                input_data_dicts.append({'sub_title': season, 'df': season_df['Player Height (cm)'],
                                         'xlabel': "Height (cm)", 'ylabel': "% of Picks"})
            hist.plot_histograms(input_data_dicts, figsize=(16, 6),
                                 title=f"{owner}'s Per-Season Distribution of Drafted Player's Height",
                                 image_name=f"draft_height_per_season_histogram_{owner}.png")

        # Each season's per-owner distribution of drafted player's height
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                input_data_dicts.append({'sub_title': owner, 'df': owner_df['Player Height (cm)'],
                                         'xlabel': "Height (cm)", 'ylabel': "% of Picks"})
            hist.plot_histograms(input_data_dicts, figsize=(16, 6),
                                 title=f"{season} Per-Owner Distribution of Drafted Player's Height",
                                 image_name=f"draft_height_per_owner_histogram_{season}.png")