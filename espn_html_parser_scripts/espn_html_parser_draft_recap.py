#!/usr/bin/env python
""" Parser for ESPN draft recap files. """
import argparse
from bs4 import BeautifulSoup
import espn_html_parser_utils
import os
import pandas as pd

import espn_html_parser_logger
logger = espn_html_parser_logger.logger()

class EspnHtmlParserDraftRecap():
    """ Class for ESPN draft recap file parsing. """
    def __init__(self, html_path):
        """ Constructor. Accepts HTML input file path. """
        # Valid flag used publicly and internally to check if instance is valid
        self.valid = True

        # Input check
        if not espn_html_parser_utils.check_html(html_path):
            logger.warning(f"Invalid input: {html_path}. Skipping...")
            self.valid = False

        # Private variables
        self._html_path = html_path
        self._df = self._parse_draft_recap_df()

    def get_df(self):
        """ Returns dataframe of draft recap information. """
        return self._df

    def _parse_draft_recap_df(self):
        """ Parses HTML page. Returns dataframe of the draft recap information. """
        # Initialize
        combined_df = pd.DataFrame()

        # Invalid check
        if not self.valid:
            return combined_df

        # Read HTML file for all tables/data
        try:
            html_dfs = pd.read_html(self._html_path)
        # Intentional except-all
        except:
            logger.warning("Cannot parse input HTML.")
            self.valid = False
            return combined_df

        # Combine dataframes
        combined_df = self._get_combined_df(html_dfs)
        return combined_df

    def _get_combined_df(self, df_list):
        """ Combines list of dataframes into one big list. """
        combined_df = pd.DataFrame()
        for index, df in enumerate(df_list):
            # Add round number column to beginning of dataframe
            df.insert(0, 'Round Number', index + 1)
            combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

        # Rename "Team" column to differentiate between player's actual NHL team,
        # and name of a team in the fantasy league.
        combined_df = combined_df.rename(columns={'Team': "Team Name"})

        # Player column strings contain data nested in them, clean that up
        combined_df = self._modify_player_col(combined_df)

        # Clean-up dataframe and re-index. Use re-index values + 1 as number count
        combined_df = combined_df.drop('NO.', axis=1)
        combined_df.index = range(1, len(combined_df) + 1)
        combined_df = combined_df.reset_index()
        combined_df = combined_df.rename(columns={'index': 'Draft Number'})

        # Replace special characters in the team name to stay consistent with file names
        combined_df['Team Name'] = combined_df['Team Name'].apply(espn_html_parser_utils.sub_special_chars)
        return combined_df

    def _modify_player_col(self, df):
        """ Extracts metadata from the player strings in the player columns.
            Cleans player strings and inserts extra metadata columns. """
        # Parse for additional metadata embedded in the player strings
        player_metadata_dict_list = []
        for player in df['Player']:
            player_metadata_dict_list.append(espn_html_parser_utils.parse_draft_metadata_from_player_str(player))

        # New dataframe to add into original
        new_player_df = pd.DataFrame(player_metadata_dict_list)

        # Drop player column from original dataframe and insert new dataframe in its place
        col_index = df.columns.get_loc('Player')
        df = df.drop(columns='Player')
        for new_col in new_player_df.columns:
            df.insert(col_index, new_col, new_player_df[new_col])
            col_index += 1

        return df

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument('--input_file', '-i', required=False, help="Input HTML file.")
    args = arg_parse.parse_args()

    # Paths
    file_path = args.input_file
    file_basename = os.path.splitext(os.path.basename(file_path))[0]
    folder_path = os.path.dirname(file_path)

    # Parse
    espn_draft_recap = EspnHtmlParserDraftRecap(file_path)
    espn_draft_recap.get_df().to_csv(os.path.join(folder_path, f"{file_basename}.csv"), index=False)