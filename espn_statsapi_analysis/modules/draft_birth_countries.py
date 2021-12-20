#!usr/bin/env python
from .draft import Draft
import matplotlib.pyplot as plt
import os

class DraftBirthCountries(Draft):
    """ Class for processing draft and player's birth country related data. """
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        # Invoke parent class to load required data
        super().__init__(espn_loader, statsapi_loader, out_path)

    def process(self):
        """ Process data. """
        # Output raw dataframe
        self._draft_df.to_csv(os.path.join(self._out_path, "draft_df.csv"), index=False)

        # League's overall distribution of drafted player's birth countries
        input_data_dict = [{'sub_title': None, 'df': self._draft_df['Player Birth Country']}]
        self._plot_birth_country_pie(num_plots=1, figsize=(8, 6),
                                     title=f"League Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                                     input_data_dicts=input_data_dict,
                                     image_name="draft_birth_countries_league_overall.png")

        # Each owner's overall distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': owner, 'df': df['Player Birth Country']}
                            for owner, df in self._draft_df.groupby('Owner Name')]
        self._plot_birth_country_pie(num_plots=len(input_data_dicts), figsize=(16, 8),
                                     title=f"Each Owner's Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                                     input_data_dicts=input_data_dicts,
                                     image_name="draft_birth_countries_owners_overall.png")

        # Each season's league distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': season, 'df': df['Player Birth Country']}
                            for season, df in self._draft_df.groupby('Season')]
        self._plot_birth_country_pie(num_plots=len(input_data_dicts), figsize=(16, 8),
                                     title=f"League's Per-Season Distribution of Drafted Player's Birth Countries",
                                     input_data_dicts=input_data_dicts,
                                     image_name=f"draft_birth_countries_per_season_league.png")

        # Each owner's per-season distribution of drafted player's birth countries
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                input_data_dicts.append({'sub_title': season, 'df': season_df['Player Birth Country']})
            self._plot_birth_country_pie(num_plots=len(input_data_dicts), figsize=(16, 8),
                                         title=f"{owner}'s Per-Season Distribution of Drafted Player's Birth Countries",
                                         input_data_dicts=input_data_dicts,
                                         image_name=f"draft_birth_countries_per_season_{owner}.png")

        # Each season's per-owner distribution of drafted player's birth countries
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                input_data_dicts.append({'sub_title': owner, 'df': owner_df['Player Birth Country']})
            self._plot_birth_country_pie(num_plots=len(input_data_dicts), figsize=(16, 8),
                                         title=f"{season} Per-Owner Distribution of Drafted Player's Birth Countries",
                                         input_data_dicts=input_data_dicts,
                                         image_name=f"draft_birth_countries_per_owner_{season}.png")

    def _plot_birth_country_pie(self, num_plots, figsize, title, input_data_dicts, image_name):
        """ Plots and saves country data in a pie graph. input_data_dicts is a
            list of data that must match the length of num_plots. Example:
            [{'sub_title': ..., 'df': ...},
             {'sub_title': ..., 'df': ...}, ...] """
        # Set specific colours for values
        colour_map = {"CAN": "indianred",
                      "USA": "royalblue",
                      "RUS": "snow",
                      "SWE": "gold",
                      "FIN": "navy",
                      "CZE": "lightblue",
                      "CHE": "firebrick",
                      "DEU": "dimgray"}

        # Plot
        fig, ax = plt.subplots(1, num_plots, figsize=figsize)
        for index, data_dict in enumerate(input_data_dicts):
            series = data_dict['df'].value_counts()

            # Show only the top 5 labels on pie chart to not cram text for smaller wedges
            labels = list(series.index[0:5]) + ["" for i in range(5, len(series.index))]

            # Set-up wedge colours
            wedge_colours = [colour_map[country] if country in colour_map else "darkgray" for country in series.index]

            # Set-up legend labels
            total_count = series.sum()
            legend_labels = [f"{country}: {round((series[country] / total_count) * 100, 1)}%" for country in series.index]

            # Generate pie chart
            if num_plots == 1:
                ax.pie(series, labels=labels,
                       wedgeprops={'edgecolor': "white", 'linewidth': 1},
                       textprops={'fontsize': "small"}, colors=wedge_colours)
                ax.set_title(data_dict['sub_title'])
                ax.legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')
            else:
                ax[index].pie(series, labels=labels,
                              wedgeprops={'edgecolor': "white", 'linewidth': 1},
                              textprops={'fontsize': "small"}, colors=wedge_colours)
                ax[index].set_title(data_dict['sub_title'])
                ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

        # Save as image
        plt.suptitle(title)
        plt.tight_layout()
        plt.savefig(os.path.join(self._out_path, image_name))
        plt.close()