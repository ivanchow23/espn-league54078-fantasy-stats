#!/usr/bin/env python
""" Parser for ESPN clubhouse files. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd

import espn_logger
logger = espn_logger.logger()

NUM_EXPECTED_HTML_TABLES = 6

class EspnHtmlParserClubhouse():
    """ Class for ESPN clubhouse file parsing. """
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
        self._rosters_dict = self._parse_roster()
        self._team_owners_dict = self._parse_team_owners()

    def get_rosters_dict(self):
        """ Returns dictionary containing rosters dataframes. """
        return self._rosters_dict

    def get_team_owners_dict(self):
        """ Returns dictionary containing team owner information. """
        return self._team_owners_dict

    def _parse_roster(self):
        """ Parses HTML page. Returns parsed clubhouse roster tables on success. """
        # Initialize
        return_dict = {'skaters_df': None, 'goalies_df': None}

        # Invalid check
        if not self.valid:
            return return_dict

        # Read HTML file for all tables/data
        try:
            html_dfs = pd.read_html(self._html_path)
        # Intentional except-all
        except:
            logger.warning("Cannot parse input HTML.")
            self.valid = False
            return return_dict

        # Check if HTML page contains at least expected number of tables
        if len(html_dfs) < NUM_EXPECTED_HTML_TABLES:
            logger.warning(f"Found {len(html_dfs)} tables (expected {NUM_EXPECTED_HTML_TABLES}).")
            return return_dict

        # Half the dataframes are used to parse for skater data and the other half for goalie data
        # Assumes first half of dataframes are for skater data, second half for goalie data
        return_dict['skaters_df'] = self._get_combined_df(html_dfs[0: int(len(html_dfs) / 2)])
        return_dict['goalies_df'] = self._get_combined_df(html_dfs[int(len(html_dfs) / 2):])
        return return_dict

    def _parse_team_owners(self):
        """ Parses HTML page. Returns parsed team owner information on success. """
        # Initialize
        return_dict = {'Team Name': "", 'Owner Name': ""}

        # Invalid check
        if not self.valid:
            return return_dict

        # Read and parse HTML for various tags
        soup = BeautifulSoup(open(self._html_path, 'r', encoding='utf-8'), 'html.parser')

        # Parse for team name from file name
        # Must follow expected naming format: "<team_name> Clubhouse - <...>.html"
        file_name = os.path.splitext(os.path.basename(self._html_path))[0]
        if len(file_name.split(" Clubhouse")) > 1:
            return_dict['Team Name'] = file_name.split(" Clubhouse")[0]

        # Parse for league and owner name, which can be found under secondary team detail as an anchor link
        team_details_sec_span_tags = soup.find_all('span', class_='team-details-secondary')
        for tag in team_details_sec_span_tags:
            owner_name_search = tag.find('span', class_='owner-name')
            if owner_name_search:
                return_dict['Owner Name'] = owner_name_search.text

        return return_dict

    def _get_combined_df(self, df_list):
        """ Returns a combined dataframe of player, season stats, and fantasy points.
            List of input dataframes are assumed to be in specific formats. """
        # First dataframe contains player information
        # This dataframe has information we want to clean/modify before combining
        combined_df = self._get_modified_player_df(df_list[0])

        # Second dataframe contains each player's season stats
        combined_df = combined_df.merge(df_list[1], left_index=True, right_index=True)

        # Third dataframe contains each player's fantasy points stats
        combined_df = combined_df.merge(df_list[2], left_index=True, right_index=True)

        # Clean-up and finish
        combined_df = combined_df.replace(to_replace="--", value="")
        return combined_df

    def _get_modified_player_df(self, df):
        """ Takes in a dataframe containing player information and outputs a
            new dataframe with modified and additional columns of information. """
        player_df = df.copy(deep=True)

        # Check if dataframe contain skater or goalie information
        if 'Skaters' in player_df.columns:
            index_key = 'Skaters'
        elif 'Goalies' in player_df.columns:
            index_key = 'Goalies'
        else:
            logger.error("Unknown key to access player information dataframe. Exiting...")
            exit(-1)

        # Parse for additional metadata embedded in the player strings
        player_metadata_dict_list = []
        for player in player_df[index_key, 'Player']:
            player_metadata_dict_list.append(espn_utils.parse_metadata_from_player_str(player))

        # Convert list of dictionaries to dataframe
        player_metadata_df = pd.DataFrame(player_metadata_dict_list)

        # Drop original player column and append new parsed information
        player_df = player_df.drop((index_key, 'Player'), axis=1)
        for col in player_metadata_df.columns:
            player_df[index_key, col] = player_metadata_df[col]

        return player_df

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--input_file', '-i', required=False, help="Input HTML file.")
    args = arg_parse.parse_args()

    # Paths
    file_path = args.input_file
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)

    # Parse
    espn_clubhouse = EspnHtmlParserClubhouse(file_path)
    rosters_dict = espn_clubhouse.get_rosters_dict()
    if rosters_dict is not None:
        rosters_dict['skaters_df'].to_csv(os.path.join(folder_path, f"{file_basename} - Skaters.csv"), index=False)
        rosters_dict['goalies_df'].to_csv(os.path.join(folder_path, f"{file_basename} - Goalies.csv"), index=False)

    team_owners_dict = espn_clubhouse.get_team_owners_dict()
    if team_owners_dict is not None:
        pd.DataFrame([team_owners_dict]).to_csv(os.path.join(folder_path, f"{file_basename} - Team Owners.csv"), index=False)