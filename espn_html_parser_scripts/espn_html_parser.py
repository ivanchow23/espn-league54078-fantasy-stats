#!/usr/bin/env python
""" Parser class to wrap various HTML parsers to generate data for all seasons.

    Given a root folder:
      1. Looks for file names in a certain format.
      2. Calls the appropriate ESPN HTML parsing script.
      3. Provides public functionality to retrieve data as a dataframe.

    File names must be in a certain format to be parsed.

    Folder structure is expected to have the form:

    <root_folder>
    - 20192020
      -> <draft_recap>.html
      -> <standings>.html
      ...
    - 20202021
      -> <draft_recap>.html
      -> <standings>.html
      ...
"""
import argparse
from espn_html_parser_league_standings import EspnHtmlParserLeagueStandings
from espn_html_parser_draft_recap import EspnHtmlParserDraftRecap
import os
import pandas as pd
import re

class EspnHtmlParser():
    def __init__(self, espn_html_files_root_path):
        """ Default constructor. """
        self._espn_html_files_root_path = espn_html_files_root_path
        self._seasons_list = self._get_seasons()

    def get_league_standings_points_df(self):
        """ Returns dataframe of league standings points data. """
        combined_df = pd.DataFrame()
        for season in self._seasons_list:
            file_path = self._find_file_in_folder(os.path.join(self._espn_html_files_root_path, season), "League Standings")
            df = EspnHtmlParserLeagueStandings(file_path).get_season_standings_points_df()
            df['Season'] = int(season)
            combined_df = pd.concat([combined_df, df])

        return combined_df

    def get_league_standings_stats_df(self):
        """ Returns dataframe of league standings stats data. """
        combined_df = pd.DataFrame()
        for season in self._seasons_list:
            file_path = self._find_file_in_folder(os.path.join(self._espn_html_files_root_path, season), "League Standings")
            df = EspnHtmlParserLeagueStandings(file_path).get_season_standings_stats_df()
            df['Season'] = int(season)
            combined_df = pd.concat([combined_df, df])

        return combined_df

    def get_draft_df(self):
        """ Returns dataframe of draft data. """
        combined_df = pd.DataFrame()
        for season in self._seasons_list:
            draft_recap_file_path = self._find_file_in_folder(os.path.join(self._espn_html_files_root_path, season), "Draft Recap")
            df = EspnHtmlParserDraftRecap(draft_recap_file_path).get_df()

            # Reach into league standings data because it contains some info about team and owner names
            league_standings_file_path = self._find_file_in_folder(os.path.join(self._espn_html_files_root_path, season), "League Standings")
            if league_standings_file_path is not None:
                team_owner_map_df = EspnHtmlParserLeagueStandings(league_standings_file_path).get_team_owners_df()
                team_owner_map_df = team_owner_map_df.rename(columns={'Team': "Team Name", 'Owner': "Owner Name"})
                df = df.merge(team_owner_map_df, how='left', on="Team Name")
            else:
                df['Owner Name'] = ""

            df['Season'] = int(season)
            combined_df = pd.concat([combined_df, df])

        return combined_df

    def _get_seasons(self):
        """ Returns a list of season folders from the root.
            Folder must be in the form XXXXYYYY. """
        # Regex pattern to find a season string
        #   - ^ used to denote start of string searching
        #   - $ used to denote end of string searching
        #   - + used to denote any repeating numbers between [0-9]
        # Examples:
        #  - "20192020" (ok)
        #  - "aaa20192020" (no)
        #  - "20192020aaa" (no)
        ret_list = []
        season_string_re_pattern = "^[0-9]+$"

        for item in os.listdir(self._espn_html_files_root_path):
            item_path = os.path.join(self._espn_html_files_root_path, item)
            if os.path.isdir(item_path) and re.match(season_string_re_pattern, item):
                ret_list.append(item)

        return ret_list

    def _find_file_in_folder(self, folder_path, str_pattern):
        """ Simple helper function that returns the path of the first file found
            that contains the given string pattern. """
        for item in os.listdir(folder_path):
            if str_pattern in item:
                return os.path.join(folder_path, item)
        return None

if __name__ == "__main__":
    argparser = argparse.ArgumentParser()
    argparser.add_argument("--input_dir", "-i", required=True, help="Input root path to ESPN HTML files for parsing.""")
    args = argparser.parse_args()

    espn_html_parser = EspnHtmlParser(args.input_dir)
    espn_html_parser.get_league_standings_points_df().to_csv("espn_html_parsed_league_standings_points.csv", index=False)
    espn_html_parser.get_league_standings_stats_df().to_csv("espn_html_parsed_league_standings_stats.csv", index=False)
    print("Generated league standings data.")

    espn_html_parser.get_draft_df().to_csv("espn_html_parsed_draft_df.csv", index=False)
    print("Generated draft recap data.")