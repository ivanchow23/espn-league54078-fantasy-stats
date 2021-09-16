#!/usr/bin/env python
""" Parser for ESPN league rosters files. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import re

import espn_logger
logger = espn_logger.logger()

class EspnHtmlParserLeagueRosters():
    """ Class for ESPN league rosters file parsing. """
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
        self._html_soup = self._read_html_soup()
        self._html_dfs = self._read_html_dfs()
        self._rosters_list = self._parse_rosters_list()
        self._standings_df = self._parse_team_standings_df()

    def get_rosters_list(self):
        """ Returns a list of rosters. """
        return self._rosters_list

    def get_standings_df(self):
        """ Returns dataframe of team standings. """
        return self._standings_df

    def _parse_rosters_list(self):
        """ Parses HTML file. Returns list of dictionaries for each team's roster. """
        # Initialize
        rosters_list = []

        # Invalid check
        if not self.valid:
            return rosters_list

        # First, parse for list of team names (and replace special characters to stay consistent with file names)
        team_names_list = []
        for span_tag in self._html_soup.find_all('span', class_='teamName'):
            team_names_list.append(espn_utils.sub_special_chars(span_tag['title']))

        # Error check
        if len(self._html_dfs) != len(team_names_list):
            logger.warning("Length of title tags don't match length of HTML dataframes.")
            return rosters_list

        # Build dictionary of each roster and add to list
        for team_name, df in zip(team_names_list, self._html_dfs):
            rosters_list.append({'team_name': team_name, 'roster_df': self._get_modified_player_df(df)})

        return rosters_list

    def _parse_team_standings_df(self):
        """ Parses HTML file. Returns dataframe of teams and points. """
        # Initialize
        standings_df = pd.DataFrame()

        # Invalid check
        if not self.valid:
            return standings_df

        # Parse for team name and number of points and add to list
        standings_dicts = []
        for rank, (team_name_span_tag, pts_span_tag) in enumerate(zip(self._html_soup.find_all('span', class_='teamName'),
                                                                      self._html_soup.find_all('span', class_='pl2'))):
            standings_dicts.append({'Rank': rank + 1,
                                    'Team Name': team_name_span_tag['title'],
                                    'Points': int(re.findall(r"\d+", pts_span_tag.text)[0])})

        # Convert to dataframe
        standings_df = pd.DataFrame(standings_dicts)

        # Replace special characters in the team name to stay consistent with file names
        if 'Team Name' in standings_df.columns:
            standings_df['Team Name'] = standings_df['Team Name'].apply(espn_utils.sub_special_chars)

        return standings_df

    def _get_modified_player_df(self, df):
        """ Takes in a dataframe containing player information and outputs a
            new dataframe with modified and additional columns of information. """
        player_df = df

        # Parse for additional metadata embedded in the player strings
        player_metadata_dict_list = []
        for player in player_df['PLAYER']:
            player_metadata_dict_list.append(espn_utils.parse_metadata_from_player_str(player))

        # Convert list of dictionaries to dataframe
        player_metadata_df = pd.DataFrame(player_metadata_dict_list)

        # Drop original player column and append new parsed information
        player_df = player_df.drop(columns='PLAYER')
        for col in player_metadata_df.columns:
            player_df[col] = player_metadata_df[col]

        return player_df

    def _read_html_soup(self):
        """ Reads HTML file and returns a soup object for parsing. """
        # Invalid check
        if not self.valid:
            return None

        # Read HTML file for various information
        return BeautifulSoup(open(self._html_path, 'r'), 'html.parser')

    def _read_html_dfs(self):
        """ Reads HTML file and returns list of dataframes. """
        # Invalid check
        if not self.valid:
            return []

        try:
            return pd.read_html(self._html_path)
        # Intentional catch all
        except:
            logger.warning("Unable to read HTML.")
            return []

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--input_file', '-i', required=False, help="Input HTML file.")
    args = arg_parse.parse_args()

    # Paths
    file_path = args.input_file
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)

    # Parse
    espn_league_rosters = EspnHtmlParserLeagueRosters(file_path)

    # Rosters
    rosters_list = espn_league_rosters.get_rosters_list()
    rosters_multi_df = pd.DataFrame()
    for roster in rosters_list:
        team_name = roster['team_name']
        df = roster['roster_df']

        roster_df = pd.DataFrame(columns=pd.MultiIndex.from_tuples([(team_name, col) for col in df.columns]))
        roster_df[team_name] = df
        rosters_multi_df = pd.concat([rosters_multi_df, roster_df], axis=1)
    rosters_multi_df.to_csv(os.path.join(folder_path, f"{file_basename}.csv"), index=False)

    # Standings
    espn_league_rosters.get_standings_df().to_csv(os.path.join(folder_path, f"{file_basename} - Standings.csv"), index=False)

