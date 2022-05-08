#!/usr/bin/env python
import matplotlib.pyplot as plt
import os
import pandas as pd
from .utils.plot_pie import PlotPie
import sys

SCRIPT_DIR = os.path.join(os.path.abspath(__file__))
PLOT_BACKEND = 'matplotlib'

class Draft():
    """ Base class for loading draft-related data. """
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        self._espn_loader = espn_loader
        self._statsapi_loader = statsapi_loader
        self._out_path = out_path
        os.makedirs(self._out_path, exist_ok=True)

        # Data to operate on and accompanying metadata
        self._draft_df = self._load_draft_df()

        # Assumes min. and max. seasons to be the range of the available data
        self._season_range_string = f"{self._draft_df['Season'].min()} - {self._draft_df['Season'].max()}"

    def process(self):
        """ Process data. """
        # Output raw dataframe
        self._draft_df.to_csv(os.path.join(self._out_path, "draft_df.csv"), index=False)

        # Generate stats
        owner_draft_order(self._draft_df, self._out_path)
        average_player_draft_position(self._draft_df, self._out_path)
        owner_num_times_drafted(self._draft_df, self._out_path)

    def _load_draft_df(self):
        """ Loads and prepares all relevant data into a dataframe. """
        # Initialize
        combined_df = pd.DataFrame()

        # Load draft information for all seasons and combine
        for season_string in self._espn_loader.get_seasons():
            draft_df = self._espn_loader.load_draft_recap_data(season_string)
            if draft_df is None:
                continue

            # Append season information and combine to master dataframe
            draft_df['Season'] = season_string
            combined_df = pd.concat([combined_df, draft_df], ignore_index=True)

        # Append additional "metadata" to the dataframe
        combined_df['Player Birth Country'] = combined_df['Player'].apply(
            lambda player: self._get_player_info(self._statsapi_loader.load_player_dict(player), 'birthCountry'))
        combined_df['Player Age'] = combined_df.apply(
            lambda x: self._get_player_age(self._statsapi_loader.load_player_dict(x['Player']), x['Season']), axis=1)
        combined_df['Player Weight (lbs)'] = combined_df['Player'].apply(
            lambda player: self._get_player_info(self._statsapi_loader.load_player_dict(player), 'weight'))
        combined_df['Player Height (cm)'] = combined_df['Player'].apply(
            lambda player: self._get_player_height_cm(self._statsapi_loader.load_player_dict(player)))

        return combined_df

    def _get_player_info(self, player_dict, key):
        """ Takes in a dictionary from statsapi loaded JSON file and looks
            for data in the given key under the "people" key. This is where
            most of a player's information exists. """
        if player_dict is None:
            return None

        try:
            return player_dict['people'][0][key]
        except KeyError:
            return None

    def _get_player_age(self, player_dict, season_string):
        """ Takes in a dictionary from statsapi loaded JSON file and
            calculates the player's rough age at the current time of the
            given season. Does this by simply taking the difference between
            player's birth year and the start of the season.

            Example: Birth year = 1995-07-23, Season = 20202021
                    Age = 2020 - 1995 = 25
        """
        # String from data dict expected to be in the form "YYYY-MM-DD"
        # Parse for YYYY
        birth_date_string = self._get_player_info(player_dict, 'birthDate')
        if birth_date_string is None:
            return None
        birth_year = int(birth_date_string[0:4])

        # Season string expected to be in the form: "XXXXYYYY"
        # Parse for start of season XXXX
        season = int(season_string[0:4])
        return season - birth_year

    def _get_player_height_cm(self, player_dict):
        """ Takes in a dictionary from statsapi loaded JSON file and converts
            the string of a player's height from feet and inches into an
            integer in units cm. The height string is directly the value that
            comes from the player's height in the JSON file. Note: This
            method's string parsing logic is meant to be super simple.

            Example: '6\' 3"' = 190.5 cm """
        # Height string is expected to be in the form like: '6\' 3"'
        height_string = self._get_player_info(player_dict, 'height')

        # Very basic way to parse for the values
        # First, split the string into sections
        str_list = height_string.split()

        # Next, assume 1st element in list is feet, 2nd element is inches
        # Remove corresponding ' and " charaters
        str_list[0] = str_list[0].replace("\'", "")
        str_list[1] = str_list[1].replace("\"", "")

        # Convert height to inches
        height_in = (int(str_list[0]) * 12) + int(str_list[1])

        # Finally, convert to cm
        return round(height_in * 2.54, 1)

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

def owner_draft_order(input_df, out_path):
    """ Stats for each owner's draft order throughout years of the league. """
    # First, filter dataframe for only first rounds of the draft since that
    # is what will determine the order for each year
    input_df = input_df[input_df['Round Number'] == 1]

    # Assumes min. and max. seasons to be the range of the available data
    seasons_range_string = f"{input_df['Season'].min()} - {input_df['Season'].max()}"

    # Set-up pie plots
    colour_map = {"1st": '#1f77b4',
                  "2nd": '#ff7f0e',
                  "3rd": '#2ca02c',
                  "4th": '#d62728',
                  "5th": '#9467bd',
                  "6th": '#17becf',
                  "7th": '#e377c2'}
    pie = PlotPie(out_path, backend=PLOT_BACKEND, wedge_colour_map=colour_map)

    # Number of times each owner had a certain draft position
    input_data_dicts = []
    for owner, df in input_df.groupby('Owner Name'):
        input_data_dicts.append({'sub_title': owner, 'df': df['Draft Number'].apply(_number_ordinal)})

    pie.plot_pies(input_data_dicts, fig_w=1600, fig_h=500, title=f"Owner's Draft Order\n{seasons_range_string}",
                  image_name="owner_draft_order.png")

def average_player_draft_position(input_df, out_path):
    """ Stats for each player's average drafted position. """
    grouped_df = input_df.groupby(['Player'])['Draft Number'].agg(['mean', 'min', 'max', 'count']).round(0)
    grouped_df = grouped_df.rename(columns={'mean': 'Average Draft Position',
                                            'min': 'Highest Position',
                                            'max': 'Lowest Position',
                                            'count': '# Times Drafted'})

    grouped_df = grouped_df.sort_values(by='Average Draft Position')
    grouped_df.to_csv(os.path.join(out_path, "average_player_draft_position.csv"))

def owner_num_times_drafted(input_df, out_path):
    """ Stats for number of times an owner drafted a player or team. """
    # ----- CSV output of number of times same owner drafted same player -----
    # Note: value_counts returns a series
    owner_player_counts_df = input_df.value_counts(subset=['Owner Name', 'Player']).to_frame().reset_index()
    owner_player_counts_df = owner_player_counts_df.rename(columns={0: '# Times Drafted'})
    multi_df = pd.DataFrame()
    for owner, df in owner_player_counts_df.groupby('Owner Name'):
        df = df.drop(columns='Owner Name').reset_index(drop=True)
        new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], df.columns]))
        new_df[owner] = df
        multi_df = pd.concat([multi_df, new_df], axis=1)
    multi_df.to_csv(os.path.join(out_path, "owner_num_times_drafted_players.csv"), index=False)

    # ----- CSV output of number of times owner drafted someone from same team -----
    # Note: value_counts returns a series
    owner_team_counts_df = input_df.value_counts(subset=['Owner Name', 'Team']).to_frame().reset_index()
    owner_team_counts_df = owner_team_counts_df.rename(columns={0: '# Times Drafted'})
    multi_df = pd.DataFrame()
    for owner, df in owner_team_counts_df.groupby('Owner Name'):
        df = df.drop(columns='Owner Name').reset_index(drop=True)
        new_df = pd.DataFrame(columns=pd.MultiIndex.from_product([[owner], df.columns]))
        new_df[owner] = df
        multi_df = pd.concat([multi_df, new_df], axis=1)
    multi_df.to_csv(os.path.join(out_path, "owner_num_times_drafted_teams.csv"), index=False)