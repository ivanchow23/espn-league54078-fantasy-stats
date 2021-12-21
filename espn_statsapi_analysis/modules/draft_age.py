#!usr/bin/env python
from .draft import Draft
from .utils.matplotlib_pie import MatplotlibPie
from .utils.matplotlib_histogram import MatplotlibHistogram
import os
import pandas as pd

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

        # Set-up plots
        hist = MatplotlibHistogram(self._out_path)
        pie = MatplotlibPie(self._out_path, wedge_colour_map={'18-22': "tab:orange",
                                                              '23-27': "tab:green",
                                                              '28-32': "tab:blue",
                                                              '33-37': "tab:red",
                                                              '> 37': "tab:purple"})

        # Each owner's overall distribution of drafted player's age groups (pie)
        age_bins = [17, 22, 27, 32, 37, 100]
        age_bin_labels = ["18-22", "23-27", "28-32", "33-37", "> 37"]
        input_data_dicts = []
        for index, (owner, df) in enumerate(self._draft_df.groupby('Owner Name')):
            # Note: pd.cut function: left interval is exclusive, right is inclusive
            binned_df = pd.cut(df['Player Age'], bins=age_bins, labels=age_bin_labels)
            input_data_dicts.append({'sub_title': owner, 'df': binned_df})
        pie.plot_pies(input_data_dicts, figsize=(16, 6),
                      title=f"Each Owner's Overall Distribution of Drafted Player's Age Groups\n{self._season_range_string}",
                      image_name="draft_age_owners_overall_pie.png")

        # Each owner's overall distribution of drafted player's age (histogram)
        input_data_dicts = []
        for index, (owner, df) in enumerate(self._draft_df.groupby('Owner Name')):
            input_data_dicts.append({'sub_title': owner, 'df': df['Player Age'],
                                     'xlabel': "Age", 'ylabel': "% of Picks"})
        hist.plot_histograms(input_data_dicts, figsize=(16, 6),
                            title=f"Each Owner's Overall Distribution of Drafted Player's Age\n{self._season_range_string}",
                            image_name="draft_age_owners_overall_histogram.png")