#!/usr/bin/env python
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys

SCRIPT_DIR = os.path.join(os.path.abspath(__file__))

class Draft():
    def __init__(self, espn_loader, statsapi_loader, out_path):
        """ Constructor. Takes in data loader objects and a path
            where this class can output any data to. """
        self._espn_loader = espn_loader
        self._statsapi_loader = statsapi_loader
        self._out_path = out_path
        os.makedirs(self._out_path, exist_ok=True)

        self._draft_df = self._load_draft_df()

    def process(self):
        """ Process data. """
        # Output raw dataframe
        self._draft_df.to_csv(os.path.join(self._out_path, "draft_df.csv"), index=False)

        # Generate stats
        owner_draft_order(self._draft_df, self._out_path)
        average_player_draft_position(self._draft_df, self._out_path)
        owner_num_times_drafted(self._draft_df, self._out_path)
        drafted_players_birth_countries_overall(self._draft_df, self._out_path)
        drafted_players_age_overall(self._draft_df, self._out_path)

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

def drafted_players_birth_countries_overall(input_df, out_path):
    """ Plots for each owner and drafted player's birth countries for all
        seasons. """
    # ----- Common variables -----
    colour_map = {"CAN": "indianred", "USA": "royalblue", "RUS": "snow",
                  "SWE": "gold", "FIN": "navy", "CZE": "lightblue",
                  "CHE": "firebrick", "DEU": "dimgray"}

    # Assumes min. and max. seasons to be the range of the available data
    seasons_range_string = f"{input_df['Season'].min()} - {input_df['Season'].max()}"

    # ----- Pie chart of entire league's distribution of drafted player's birth countries for all years -----
    fig, ax = plt.subplots(1, 1, figsize=(8, 6))
    series = input_df['Player Birth Country'].value_counts()
    total_count = series.sum()

    # Show only the top 5 labels on pie chart to not cram text for smaller wedges
    labels = list(series.index[0:5]) + ["" for i in range(5, len(series.index))]

    # Set-up wedge colours
    wedge_colours = [colour_map[country] if country in colour_map else "darkgray" for country in series.index]

    # Generate pie chart
    ax.pie(series, labels=labels,
           wedgeprops={'edgecolor': "white", 'linewidth': 1},
           textprops={'fontsize': "small"}, colors=wedge_colours)

    # Generate legend
    legend_labels = [f"{country}: {round((series[country] / total_count) * 100, 1)}%" for country in series.index]
    ax.legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

    # Save as image
    plt.suptitle(f"Drafted Player's Birth Countries of Entire League\n{seasons_range_string}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "drafted_players_birth_countries_league.png"))

    # ----- Pie chart of each owner's drafted player's birth countries distribution for all years -----
    num_owners = len(input_df['Owner Name'].unique())
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
    for index, (owner, df) in enumerate(input_df.groupby('Owner Name')):
        series = df['Player Birth Country'].value_counts()

        # Show only the top 5 labels on pie chart to not cram text for smaller wedges
        labels = list(series.index[0:5]) + ["" for i in range(5, len(series.index))]

        # Set-up wedge colours
        wedge_colours = [colour_map[country] if country in colour_map else "darkgray" for country in series.index]

        # Generate pie chart
        ax[index].pie(series, labels=labels,
                      wedgeprops={'edgecolor': "white", 'linewidth': 1},
                      textprops={'fontsize': "small"}, colors=wedge_colours)

        # Generate legend and titles
        total_count = series.sum()
        legend_labels = [f"{country}: {round((series[country] / total_count) * 100, 1)}%" for country in series.index]
        ax[index].set_title(owner)
        ax[index].legend(labels=legend_labels, loc='upper center', bbox_to_anchor=(0.5, 0), fontsize='x-small')

    # Save as image
    plt.suptitle(f"Drafted Player's Birth Countries for Each Owner\n{seasons_range_string}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "drafted_players_birth_countries_owner.png"))

def drafted_players_age_overall(input_df, out_path):
    """ Plots for each owner and drafted player's age for all seasons. """
    # ----- Common variables -----
    num_owners = len(input_df['Owner Name'].unique())

    # Assumes min. and max. seasons to be the range of the available data
    seasons_range_string = f"{input_df['Season'].min()} - {input_df['Season'].max()}"

    # ----- Pie chart of each owner's draft pick's age groups -----
    age_bins = [17, 22, 27, 32, 37, 100]
    age_bin_labels = ["18-22", "23-27", "28-32", "33-37", "> 37"]
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
    for index, (owner, df) in enumerate(input_df.groupby('Owner Name')):
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

    plt.suptitle(f"Drafted Player's Age Groups for Each Owner\n{seasons_range_string}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "drafted_players_age_owner_pie.png"))

    # Generate histogram of each owner's draft pick's ages
    fig, ax = plt.subplots(1, num_owners, figsize=(16, 6))
    for index, (owner, df) in enumerate(input_df.groupby('Owner Name')):
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

    plt.suptitle(f"Drafted Player's Age for Each Owner\n{seasons_range_string}")
    plt.tight_layout()
    plt.savefig(os.path.join(out_path, "drafted_players_age_owner_histogram.png"))