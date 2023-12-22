#!/usr/bin/env python
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class PlayerWithDifferentOwners():
    def __init__(self, espn_fantasy_api_df_csv_path):
        """ Default constructor. """
        self._daily_rosters_df = pd.read_csv(espn_fantasy_api_df_csv_path)
        self._cols_of_interest = ['GP', 'appliedTotal', 'G', 'A', 'PPP', 'SHP', 'GWG', 'HAT', 'W', 'SO']

        # Dataframe of sums
        self._sum_df = self._get_sum_df()

    def get_seasons(self):
        """ Returns list of valid seasons contained in the data. """
        return self._daily_rosters_df['season'].unique()

    def get_table_fig(self, season):
        """ Get a table figure of the stats for the given season. """
        # Filter for season
        season_df = self._sum_df[self._sum_df['season'] == season]

        # Data structure to store information to be used to generate table figures
        # Used later to easily translate to a dataframe table
        # Example:
        # [{'Player': "Player A", 'Owner': "Total",   'GP': 10, ...},
        #  {'Player': "",         'Owner': "Owner A", 'GP': 4,  ...},
        #  {'Player': "",         'Owner': "Owner B", 'GP': 6,  ...}
        #  {'Player': "Player B", 'Owner': "Total",   'GP': 15, ...},
        #  {'Player': "",         'Owner': "Owner C", 'GP': 5,  ...},
        #  {'Player': "",         'Owner': "Owner D", 'GP': 10,  ...}]
        player_data_list = []

        # Find each player that had multiple owners
        for player, player_df in season_df.groupby('fullName'):
            num_owners = len(player_df['owner'].unique())
            if num_owners > 1:
                # Gather totals
                total_gp = player_df['GP'].sum()
                total_pts = round(player_df['appliedTotal'].sum(), 2)
                total_pts_per_game = round(total_pts / total_gp, 1) if total_gp != 0 else 0
                player_data_list.append({'Player': player, 'Owner': "Total", 'GP': total_gp, 'Points': total_pts, 'Points/GP': total_pts_per_game})

                # Gather data for each owner
                for owner, owner_df in player_df.sort_values('GP', ascending=False).groupby('owner', sort=False):
                    gp = owner_df['GP'].iloc[0]
                    pts = round(owner_df['appliedTotal'].iloc[0], 2)
                    pts_per_game = round(pts / gp, 1) if gp != 0 else 0
                    player_data_list.append({'Player': "", 'Owner': owner, 'GP': gp, 'Points': pts, 'Points/GP': pts_per_game})

                # Insert blank row for formatting
                player_data_list.append({'Player': "", 'Owner': "", 'GP': "", 'Points': "", 'Points/GP': ""})

        # No players with multiple owners found, return empty figure
        if len(player_data_list) == 0:
            return go.Figure()

        # Generate table figures for each player
        df = pd.DataFrame(player_data_list)
        fig = go.Figure(data=[go.Table(header={'values': df.columns},
                                       cells={'values': [df[col].to_list() for col in df.columns]})])

        # Attempt to adjust figure height based on number of entries in table
        fig_height = 225 + (20 * len(df))
        fig.update_layout(height=fig_height)
        fig.update_layout(title=f"Players with Different Owners ({season})<br>(Not Including Points Left on Bench/IR)")
        return fig

    def _get_sum_df(self):
        """ Get dataframe of sums derived from original raw dataframe. """
        # Filter out for when players are placed on the bench or IR
        daily_rosters_df = self._daily_rosters_df[(self._daily_rosters_df['lineupSlotId'] != 7) & (self._daily_rosters_df['lineupSlotId'] != 8)]

        sum_df = daily_rosters_df.groupby(['owner', 'fullName', 'season'])[self._cols_of_interest].sum().reset_index()
        return sum_df