#!/usr/bin/env python
""" Generates data from ESPN HTML and NHLAPI data sources. """
import argparse
from espn_nhlapi_utils import ESPN_NHLAPI_TEAM_ABBREV_MAP, espn_to_nhlapi_team_abbrev, player_name_is_close_match
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "nhlapi_scripts"))
from espn_html_parser import EspnHtmlParser
from nhlapi_data_generator import NhlapiDataGenerator

class DraftDataGenerator():
    def __init__(self, espn_html_root_folder, nhlapi_downloads_root_folder, out_dir_path):
        """ Default constructor. """
        self._espn_html_root_folder = espn_html_root_folder
        self._nhlapi_downloads_root_folder = nhlapi_downloads_root_folder
        self._out_dir_path = out_dir_path

    def get_df(self):
        """ Gets dataframe of data. """
        # Parse nhlapi data
        nhlapi_data_df = NhlapiDataGenerator(self._nhlapi_downloads_root_folder).get_df()

        # Parse ESPN HTML data
        espn_html_draft_recap_df = EspnHtmlParser(self._espn_html_root_folder).get_draft_df()

        # Clean-up ESPN HTML draft data
        # Match player names to nhlapi names before merging
        espn_html_draft_recap_df['Player'] = espn_html_draft_recap_df['Player'].apply(lambda x: self._find_close_player_name_match_from_list(x, list(nhlapi_data_df['Player'])))

        # Clean-up nhlapi data
        # Drop duplicate entries for each player (agnostic of season/team/etc.)
        # TODO: This could be an issue for cases where there are same player names
        # TODO: This is also an issue because it drops season-by-season data for each player
        nhlapi_data_df = nhlapi_data_df.drop_duplicates('id', keep='last')

        # Drop columns we don't want merged that results in unwanted or duplicate columns
        nhlapi_data_df = nhlapi_data_df.drop(columns=['id', 'Position', 'Team', 'Season'])

        # Merge data from sources
        combined_df = espn_html_draft_recap_df.merge(nhlapi_data_df, how='left', on='Player')
        return combined_df

    def _find_file_in_folder(self, folder_path, str_pattern):
        """ Simple helper function that returns the path of the first file found
            that contains the given string pattern. """
        for item in os.listdir(folder_path):
            if str_pattern in item:
                return os.path.join(folder_path, item)
        return None

    def _find_close_player_name_match_from_list(self, player_name, players_list):
        """ Finds the closest player name match from a given list.
            Use the name from the list if a close match is found. """
        # Go through list and find a perfect match first
        for player in players_list:
            if player_name == player:
                return player

        # If no perfect match, find a close match
        for player in players_list:
            if player_name_is_close_match(player_name, player):
                return player

        return player_name

if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--espn_html", required=True, help="Root path of ESPN HTML files.")
    arg_parser.add_argument("--nhlapi", required=True, help="Root path of nhlapi downloads.")
    arg_parser.add_argument("--outdir", required=False, default=SCRIPT_DIR, help="Path to folder where output data will go.")

    args = arg_parser.parse_args()

    print("Generating draft data...")
    draft_data_gen = DraftDataGenerator(args.espn_html, args.nhlapi, args.outdir)
    draft_data_gen.get_df().to_csv(os.path.join(args.outdir, "draft_df.csv"), index=False)
    print("Done.")
