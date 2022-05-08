#!usr/bin/env python
from .draft import Draft
from .utils.plot_pie import PlotPie
import os
import sys

PLOT_BACKEND = 'matplotlib'

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

        # Set-up plots
        pie = PlotPie(self._out_path, backend=PLOT_BACKEND, wedge_colour_map={"CAN": '#cd5c5c',
                                                                              "USA": '#4169e1',
                                                                              "RUS": '#fffafa',
                                                                              "SWE": '#ffd700',
                                                                              "FIN": '#000080',
                                                                              "CZE": '#add8e6',
                                                                              "CHE": '#b22222',
                                                                              "DEU": '#696969'})

        # League's overall distribution of drafted player's birth countries
        pie.plot_pie(df=self._draft_df['Player Birth Country'], fig_w=800, fig_h=600,
                     title=f"League Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                     image_name="draft_birth_countries_league_overall.png")

        # Each owner's overall distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': owner, 'df': df['Player Birth Country']}
                            for owner, df in self._draft_df.groupby('Owner Name')]
        pie.plot_pies(input_data_dicts=input_data_dicts, fig_w=1600, fig_h=800,
                      title=f"Each Owner's Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                      image_name="draft_birth_countries_owners_overall.png")

        # Each season's league distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': season, 'df': df['Player Birth Country']}
                            for season, df in self._draft_df.groupby('Season')]
        pie.plot_pies(input_data_dicts=input_data_dicts, fig_w=1600, fig_h=800,
                      title=f"League's Per-Season Distribution of Drafted Player's Birth Countries",
                      image_name=f"draft_birth_countries_per_season_league.png")

        # Each owner's per-season distribution of drafted player's birth countries
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                input_data_dicts.append({'sub_title': season, 'df': season_df['Player Birth Country']})
            pie.plot_pies(input_data_dicts=input_data_dicts, fig_w=1600, fig_h=800,
                          title=f"{owner}'s Per-Season Distribution of Drafted Player's Birth Countries",
                          image_name=f"draft_birth_countries_per_season_{owner}.png")

        # Each season's per-owner distribution of drafted player's birth countries
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                input_data_dicts.append({'sub_title': owner, 'df': owner_df['Player Birth Country']})
            pie.plot_pies(input_data_dicts=input_data_dicts, fig_w=1600, fig_h=800,
                          title=f"{season} Per-Owner Distribution of Drafted Player's Birth Countries",
                          image_name=f"draft_birth_countries_per_owner_{season}.png")