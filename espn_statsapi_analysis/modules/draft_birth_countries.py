#!usr/bin/env python
from .draft import Draft
from .utils.matplotlib_pie import MatplotlibPie
import os
import sys

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
        pie = MatplotlibPie(self._out_path, wedge_colour_map={"CAN": "indianred",
                                                              "USA": "royalblue",
                                                              "RUS": "snow",
                                                              "SWE": "gold",
                                                              "FIN": "navy",
                                                              "CZE": "lightblue",
                                                              "CHE": "firebrick",
                                                              "DEU": "dimgray"})

        # League's overall distribution of drafted player's birth countries
        pie.plot_pie(df=self._draft_df['Player Birth Country'], figsize=(8, 6),
                     title=f"League Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                     image_name="draft_birth_countries_league_overall.png")

        # Each owner's overall distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': owner, 'df': df['Player Birth Country']}
                            for owner, df in self._draft_df.groupby('Owner Name')]
        pie.plot_pies(input_data_dicts=input_data_dicts, figsize=(16, 8),
                      title=f"Each Owner's Overall Distribution of Drafted Player's Birth Countries\n{self._season_range_string}",
                      image_name="draft_birth_countries_owners_overall.png")

        # Each season's league distribution of drafted player's birth countries
        input_data_dicts = [{'sub_title': season, 'df': df['Player Birth Country']}
                            for season, df in self._draft_df.groupby('Season')]
        pie.plot_pies(input_data_dicts=input_data_dicts, figsize=(16, 8),
                      title=f"League's Per-Season Distribution of Drafted Player's Birth Countries",
                      image_name=f"draft_birth_countries_per_season_league.png")

        # Each owner's per-season distribution of drafted player's birth countries
        for owner, owner_df in self._draft_df.groupby('Owner Name'):
            input_data_dicts = []
            for season, season_df in owner_df.groupby('Season'):
                input_data_dicts.append({'sub_title': season, 'df': season_df['Player Birth Country']})
            pie.plot_pies(input_data_dicts=input_data_dicts, figsize=(16, 8),
                          title=f"{owner}'s Per-Season Distribution of Drafted Player's Birth Countries",
                          image_name=f"draft_birth_countries_per_season_{owner}.png")

        # Each season's per-owner distribution of drafted player's birth countries
        for season, season_df in self._draft_df.groupby('Season'):
            input_data_dicts = []
            for owner, owner_df in season_df.groupby('Owner Name'):
                input_data_dicts.append({'sub_title': owner, 'df': owner_df['Player Birth Country']})
            pie.plot_pies(input_data_dicts=input_data_dicts, figsize=(16, 8),
                          title=f"{season} Per-Owner Distribution of Drafted Player's Birth Countries",
                          image_name=f"draft_birth_countries_per_owner_{season}.png")