#!/usr/bin/env python
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

SCRIPT_DIR = os.path.join(os.path.abspath(__file__))

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

    num_owners = len(input_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 5))
    colour_map = {"1st": "tab:blue", "2nd": "tab:orange", "3rd": "tab:green",
                  "4th": "tab:red", "5th": "tab:purple", "6th": "tab:cyan",
                  "7th": "tab:pink"}

    for index, (owner, df) in enumerate(input_df.groupby('Owner Name')):
        # Draft number column indicates draft order since we are
        # only counting the first round here
        series = df['Draft Number'].value_counts().sort_index()

        # Change the index to use ordinal numbering
        # Example:
        # Index  Count  ->  Index  Count
        # 1      2          1st    2
        # 2      0          2nd    0
        # 3      1          3rd    1
        # 4      0          4th    0
        series.index = series.index.map(_number_ordinal)

        # Pie chart colour mappings
        wedge_colours = [colour_map[pos] for pos in series.index]

        # Generate pie chart
        ax[index].pie(series, labels=series.index, autopct='%1.1f%%',
                      wedgeprops={'edgecolor': "white", 'linewidth': 0.75},
                      textprops={'fontsize': "small"}, colors=wedge_colours)

        ax[index].set_title(owner)
        legend_labels = [f"{pos}: {series[pos]}/{series.sum()}" for pos in series.index]
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='small')

    plt.suptitle(f"Owner's Draft Order\n{seasons_range_string}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "owner_draft_order.png"))

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