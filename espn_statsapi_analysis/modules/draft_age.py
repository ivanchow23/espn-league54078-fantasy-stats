#!usr/bin/env python
from .draft import Draft
import matplotlib.pyplot as plt
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

        # Common variables
        num_owners = len(self._draft_df['Owner Name'].unique())

        # Pie chart of each owner's draft pick's age groups
        age_bins = [17, 22, 27, 32, 37, 100]
        age_bin_labels = ["18-22", "23-27", "28-32", "33-37", "> 37"]
        fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
        for index, (owner, df) in enumerate(self._draft_df.groupby('Owner Name')):
            # Note: pd.cut function: left interval is exclusive, right is inclusive
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

        plt.suptitle(f"Each Owner's Overall Distribution of Drafted Player's Age Groups\n{self._season_range_string}")
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, "draft_age_owners_overall_pie.png"))

        # Histogram of each owner's draft pick's ages
        fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
        for index, (owner, df) in enumerate(self._draft_df.groupby('Owner Name')):
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

        plt.suptitle(f"Each Owner's Overall Distribution of Drafted Player's Age\n{self._season_range_string}")
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, "draft_age_owners_overall_histogram.png"))