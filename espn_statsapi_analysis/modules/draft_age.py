#!usr/bin/env python
from .draft import Draft
from .utils.plot_histogram import PlotHistogram
from .utils.plot_pie import PlotPie
import os
import pandas as pd

PLOT_BACKEND = 'matplotlib'

class DraftAge(Draft):
    """ Class for processing draft and player's age related data. """
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        # Invoke parent class to load required data
        super().__init__(espn_loader, statsapi_loader, out_path)

    def process(self):
        # Output raw dataframe
        self._draft_df.to_csv(os.path.join(self._out_path, "draft_df.csv"), index=False)

        # Age group bins
        age_bins = [17, 22, 27, 32, 37, 100]
        age_bin_labels = ["18-22", "23-27", "28-32", "33-37", "> 37"]

        # Set-up plots
        hist = PlotHistogram(self._out_path, backend=PLOT_BACKEND)
        pie = PlotPie(self._out_path, backend=PLOT_BACKEND, wedge_colour_map={'18-22': "#ff7f0e",
                                                                              '23-27': "#2ca02c",
                                                                              '28-32': "#1f77b4",
                                                                              '33-37': "#d62728",
                                                                              '> 37': "#9467bd"})

        # League's overall distribution of drafted player's age groups (pie)
        # Note: pd.cut function: left interval is exclusive, right is inclusive
        binned_df = pd.cut(self._draft_df['Player Age'], bins=age_bins, labels=age_bin_labels)
        pie.plot_pie(binned_df, fig_w=800, fig_h=600,
                     title=f"League's Overall Distribution of Drafted Player's Age Groups\n{self._season_range_string}",
                     image_name="draft_age_binned_league_overall_pie.png")

        # League's overall distribution of drafted player's age (histogram)
        hist.plot_histogram(self._draft_df['Player Age'], fig_w=800, fig_h=600,
                            title=f"League's Overall Distribution of Drafted Player's Age\n{self._season_range_string}",
                            xlabel="Age", ylabel="% of Picks",
                            image_name="draft_age_league_overall_histogram.png")

        # Each owner's overall distribution of drafted player's age groups (pie)
        input_data_dicts = []
        for owner, df in self._draft_df.groupby('Owner Name'):
            # Note: pd.cut function: left interval is exclusive, right is inclusive
            binned_df = pd.cut(df['Player Age'], bins=age_bins, labels=age_bin_labels)
            input_data_dicts.append({'sub_title': owner, 'df': binned_df})
        pie.plot_pies(input_data_dicts, fig_w=1600, fig_h=600,
                      title=f"Each Owner's Overall Distribution of Drafted Player's Age Groups\n{self._season_range_string}",
                      image_name="draft_age_binned_owners_overall_pie.png")

        # Each owner's overall distribution of drafted player's age (histogram)
        input_data_dicts = []
        for owner, df in self._draft_df.groupby('Owner Name'):
            input_data_dicts.append({'sub_title': owner, 'df': df['Player Age'],
                                     'xlabel': "Age", 'ylabel': "% of Picks"})
        hist.plot_histograms(input_data_dicts, fig_w=1600, fig_h=600,
                            title=f"Each Owner's Overall Distribution of Drafted Player's Age\n{self._season_range_string}",
                            image_name="draft_age_owners_overall_histogram.png")

        # Each owner's per-season distribution of drafted player's age groups (pie)
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                # Note: pd.cut function: left interval is exclusive, right is inclusive
                binned_df = pd.cut(season_df['Player Age'], bins=age_bins, labels=age_bin_labels)
                input_data_dicts.append({'sub_title': season, 'df': binned_df,
                                         'xlabel': "Age", 'ylabel': "% of Picks"})
            pie.plot_pies(input_data_dicts, fig_w=1600, fig_h=600,
                          title=f"{owner}'s Per-Season Distribution of Drafted Player's Age Groups\n{self._season_range_string}",
                          image_name=f"draft_age_binned_per_season_pie_{owner}.png")

        # Each season's per-owner distribution of drafted player's age groups (pie)
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                # Note: pd.cut function: left interval is exclusive, right is inclusive
                binned_df = pd.cut(owner_df['Player Age'], bins=age_bins, labels=age_bin_labels)
                input_data_dicts.append({'sub_title': owner, 'df': binned_df,
                                         'xlabel': "Age", 'ylabel': "% of Picks"})
            pie.plot_pies(input_data_dicts, fig_w=1600, fig_h=600,
                          title=f"{season} Per-Owner Distribution of Drafted Player's Age Groups\n",
                          image_name=f"draft_age_binned_per_owner_pie_{season}.png")

        # Each owner's per-season distribution of drafted player's age (histogram)
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                input_data_dicts.append({'sub_title': season, 'df': season_df['Player Age'],
                                         'xlabel': "Age", 'ylabel': "% of Picks"})
            hist.plot_histograms(input_data_dicts, fig_w=1600, fig_h=600,
                                 title=f"{owner}'s Per-Season Distribution of Drafted Player's Age",
                                 image_name=f"draft_age_per_season_histogram_{owner}.png")

        # Each season's per-owner distribution of drafted player's age (histogram)
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                input_data_dicts.append({'sub_title': owner, 'df': owner_df['Player Age'],
                                         'xlabel': "Age", 'ylabel': "% of Picks"})
            hist.plot_histograms(input_data_dicts, fig_w=1600, fig_h=600,
                                 title=f"{season} Per-Owner Distribution of Drafted Player's Age",
                                 image_name=f"draft_age_per_owner_histogram_{season}.png")