#!/usr/bin/env python
""" Parser for ESPN league standings files. """
import argparse
import espn_utils
import os
import pandas as pd

import espn_logger
logger = espn_logger.logger()

NUM_EXPECTED_HTML_TABLES = 6
class EspnHtmlParserLeagueStandings():
    """ Class for ESPN league standings file parsing. """
    def __init__(self, html_path):
        """ Constructor. Accepts HTML input file path. """
        # Valid flag used publicly and internally to check if instance is valid
        self.valid = True

        # Input check
        if not espn_utils.check_html(html_path):
            logger.warning(f"Invalid input: {html_path}. Skipping...")
            self.valid = False

        # Private variables
        self._html_path = html_path
        self._html_dfs = self._read_html_dfs()
        self._team_owners_df = self._parse_team_owners()

        # Difference between the two types of dataframes
        # Season points is a table of actual points accumulated per stat
        # Season stats is a table of raw points (i.e.: Goals, Assists, Goalie Wins, etc.)
        self._season_standings_points_df = self._parse_season_standings_points()
        self._season_standings_stats_df = self._parse_season_standings_stats()

    def get_season_standings_points_df(self):
        """ Returns dataframe of season standings in points. """
        return self._season_standings_points_df

    def get_season_standings_stats_df(self):
        """ Returns dataframe of season standings in raw points/stats. """
        return self._season_standings_stats_df

    def get_standings_dict(self):
        """ Returns dictionary of standings information. """
        return {'season_points': self._season_standings_points_df, 'season_stats': self._season_standings_stats_df}

    def _parse_team_owners(self):
        """ Helper function that parses a specific table in the HTML page, all for the purpose
            of extracting team and owner name out of it. """
        # Initialize
        team_owners_df = pd.DataFrame()

        # Invalid check
        if not self.valid:
            return team_owners_df

        # The 4th dataframe in the list contains a column where team and owner names are embedded into a string
        df = self._html_dfs[3]

        # The strings have the form "Team Name (Owner Name)" - extract these into a dictionary
        # Not by design to iterate through a rows of a dataframe, but its quick and simple to implement
        team_owner_dicts = []
        for index, row in df.iterrows():
            # Attempt to extract strings
            s = row['Team']
            d = {'Team': s[0:s.find(" (")], 'Owner': s[s.find("(") + 1: s.find(")")]}
            team_owner_dicts.append(d)

        return pd.DataFrame(team_owner_dicts)

    def _parse_season_standings_points(self):
        """ Parses HTML page. Returns parsed season points standings tables on success. """
        # Initialize
        combined_df = pd.DataFrame()

        # Invalid check
        if not self.valid:
            return combined_df

        # First dataframe contains rank and team information
        # Merge owner names to it and convert to a multi-index column to match other dataframes to concatenate
        combined_df = self._html_dfs[0]
        combined_df = combined_df.merge(self._team_owners_df, on='Team', how='left')
        combined_df.columns = pd.MultiIndex.from_product([['Team Info'], list(combined_df.columns)])

        # 2nd dataframe is a table of total skater/goalie points
        combined_df = pd.concat([combined_df, self._html_dfs[1]], axis=1)

        # 3rd dataframe is a table of total points
        combined_df = pd.concat([combined_df, self._html_dfs[2]], axis=1)
        return combined_df

    def _parse_season_standings_stats(self):
        """ Parses HTML page. Returns parsed season points standings stats on success. """
        # Initialize
        combined_df = pd.DataFrame()

        # Invalid check
        if not self.valid:
            return combined_df

        # 4th dataframe contains rank and team information
        # The team column contains team and owner names embedded into a string
        # First, extract the string to only keep the team name in the column
        # Then, add the owner names as a separate column
        # Finally, convert to multi-index column to match other dataframes to concatenate
        combined_df = self._html_dfs[3]
        combined_df['Team'] = combined_df['Team'].apply(lambda s: s[0:s.find(" (")])
        combined_df = combined_df.merge(self._team_owners_df, on='Team', how='left')
        combined_df.columns = pd.MultiIndex.from_product([['Team Info'], list(combined_df.columns)])

        # 5th dataframe is a table of total skater/goalie raw stats
        combined_df = pd.concat([combined_df, self._html_dfs[4]], axis=1)

        # 6th dataframe is a single column of number of moves made
        # For some reason, this gets incorrectly parsed
        # First, the column name of this is actually a valid row entry
        # Then, change the column name to something more descriptive
        # Finally, convert to multi-index column to match other dataframes to concatenate
        df = self._html_dfs[5]
        df = pd.concat([pd.DataFrame([{df.columns[0]: df.columns[0]}]), df], ignore_index=True)
        df.columns = pd.MultiIndex.from_product([['Moves'], ['Moves']])
        combined_df = pd.concat([combined_df, df], axis=1)
        return combined_df

    def _read_html_dfs(self):
        """ Reads HTML file and returns list of dataframes. """
        dfs = []

        # Invalid check
        if not self.valid:
            return dfs

        try:
            dfs = pd.read_html(self._html_path)
        # Intentional catch all
        except:
            logger.warning("Unable to read HTML.")
            self.valid = False
            return dfs

        # Must contain enough dataframes for parsing
        # Flip valid bit if unexpected number of tables found
        if len(dfs) != NUM_EXPECTED_HTML_TABLES:
            self.valid = False

        return dfs

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--input_file', '-i', required=False, help="Input HTML file.")
    args = arg_parse.parse_args()

    # Paths
    file_path = args.input_file
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)

    # Parse
    espn_league_standings = EspnHtmlParserLeagueStandings(file_path)
    espn_league_standings.get_season_standings_points_df().to_csv(os.path.join(folder_path, f"{file_basename} - Points.csv"), index=False)
    espn_league_standings.get_season_standings_stats_df().to_csv(os.path.join(folder_path, f"{file_basename} - Stats.csv"), index=False)
