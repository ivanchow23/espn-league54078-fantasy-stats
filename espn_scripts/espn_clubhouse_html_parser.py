#!/usr/bin/env python
""" Parses an ESPN fantasy hockey clubhouse roster HTML page.
    Saves team and player stats information to CSV. """

import argparse
import espn_utils
import os
import pandas as pd
import re

# Number of expected tables in the HTML page
NUM_EXPECTED_HTML_TABLES = 6

def run(in_file_path):
    """ Runs the script. """
    file_dir = os.path.dirname(in_file_path)
    file_basename = os.path.splitext(os.path.basename(in_file_path))[0]
    file_basename = _get_file_basename(file_basename)
    print("Processing: {}".format(in_file_path))

    # Read HTML file for all tables/data
    html_dfs = pd.read_html(in_file_path)

    # Check if HTML page contains at least expected number of tables
    if len(html_dfs) < NUM_EXPECTED_HTML_TABLES:
        print("Found {} tables (expected {}). Exiting...".format(len(html_dfs), NUM_EXPECTED_HTML_TABLES))
        exit(-1)

    # Half the dataframes are used to parse for skater data and the other half for goalie data
    # Assume first half of dataframes are for skater data, second half for goalie data
    skaters_out_file_path = os.path.join(file_dir, file_basename + " - Skaters.csv")
    skaters_df = _get_combined_df(html_dfs[0: int(len(html_dfs) / 2)])
    skaters_df.to_csv(skaters_out_file_path, index=False)
    print("Output to: {}".format(skaters_out_file_path))

    goalies_out_file_path = os.path.join(file_dir, file_basename + " - Goalies.csv")
    goalies_df = _get_combined_df(html_dfs[int(len(html_dfs) / 2):])
    goalies_df.to_csv(goalies_out_file_path, index=False)
    print("Output to: {}".format(goalies_out_file_path))
    print("Done.\n")

def _get_file_basename(file_basename):
    """ Helper function to determine what file basename to use as output.
        ESPN roster clubhouse pages use a certain title format, which could
        get saved as the file name when saving as HTML. Otherwise, just use
        the base filename if it does not match expected title format. """
    # Found a match
    if(re.match(espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE, file_basename)):
        # Strip some extra text from name
        file_basename = file_basename.replace(" - ESPN Fantasy Hockey", "")
        file_basename = file_basename.replace(" Clubhouse", "")
        return file_basename
    # Just use original basename
    else:
        return file_basename

def _get_combined_df(df_list):
    """ Returns a combined dataframe of player, season stats, and fantasy points.
        List of input dataframes are assumed to be in specific formats. """
    # First dataframe contains player information
    # This dataframe has information we want to clean/modify before combining
    combined_df = _get_modified_player_df(df_list[0])

    # Second dataframe contains each player's season stats
    combined_df = combined_df.merge(df_list[1], left_index=True, right_index=True)

    # Third dataframe contains each player's fantasy points stats
    combined_df = combined_df.merge(df_list[2], left_index=True, right_index=True)

    # Clean-up and finish
    combined_df = combined_df.replace(to_replace="--", value="")
    return combined_df

def _get_modified_player_df(df):
    """ Takes in a dataframe containing player information and outputs a
        new dataframe with modified and additional columns of information. """
    player_df = df.copy(deep=True)

    # Check if dataframe contain skater or goalie information
    if 'Skaters' in player_df.columns:
        index_key = 'Skaters'
    elif 'Goalies' in player_df.columns:
        index_key = 'Goalies'
    else:
        print("Unknown key to access player information dataframe. Exiting...")
        exit(-1)

    # Parse for additional metadata embedded in the player strings
    player_metadata_dict_list = []
    for player in player_df[index_key, 'Player']:
        player_metadata_dict_list.append(espn_utils.parse_metadata_from_player_str(player))

    # Convert list of dictionaries to dataframe
    player_metadata_df = pd.DataFrame(player_metadata_dict_list)

    # Drop original player column and append new parsed information
    player_df = player_df.drop((index_key, 'Player'), axis = 1)
    for col in player_metadata_df.columns:
        player_df[index_key, col] = player_metadata_df[col]

    return player_df

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', required=True, help="Input HTML file.")
    args = arg_parser.parse_args()
    run(args.i)