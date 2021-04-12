#!/usr/bin/env python
""" Parses an ESPN fantasy hockey clubhouse roster HTML page. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import re

# Number of expected tables in the HTML page
NUM_EXPECTED_HTML_TABLES = 6

def get_file_dicts(in_file_paths):
    """ Parses and returns a list of dictionaries corresponding to skater and goalie data for given input HTML files.
        Return data structure has the form:
        [ { 'file_dir': "file_dir1", ..., 'skaters_df': skaters_df1, 'goalies_df': goalies_df1 },
          { 'file_dir': "file_dir2", ..., 'skaters_df': skaters_df2, 'goalies_df': goalies_df2 },
          { 'file_dir': "file_dir3", ..., 'skaters_df': skaters_df3, 'goalies_df': goalies_df3 },
          ...
        ]
    """
    file_dicts = []
    for in_file_path in in_file_paths:
        file_dir = os.path.dirname(in_file_path)
        print("Processing: {}".format(in_file_path))

        # Read HTML file for all tables/data
        html_dfs = pd.read_html(in_file_path)

        # Check if HTML page contains at least expected number of tables
        if len(html_dfs) < NUM_EXPECTED_HTML_TABLES:
            print("Found {} tables (expected {}). Skipping...".format(len(html_dfs), NUM_EXPECTED_HTML_TABLES))
            continue

        # Read and parse HTML for various tags
        soup = BeautifulSoup(open(in_file_path, 'r'), 'html.parser')

        # Parse for team name
        team_name = ""
        team_name_span_tags = soup.find_all('span', class_='teamName')
        for tag in team_name_span_tags:
            try:
                team_name = tag['title']
            except KeyError:
                # Intentional pass - try next tag
                pass

        # Parse for league and owner name, which can be found under secondary team detail as an anchor link
        league_name = ""
        owner_name = ""
        team_details_sec_span_tags = soup.find_all('span', class_='team-details-secondary')
        for tag in team_details_sec_span_tags:
            league_name_search = tag.find('a', class_='AnchorLink')
            if league_name_search:
                league_name = league_name_search.text

            owner_name_search = tag.find('span', class_='owner-name')
            if owner_name_search:
                owner_name = owner_name_search.text

        # Half the dataframes are used to parse for skater data and the other half for goalie data
        # Assumes first half of dataframes are for skater data, second half for goalie data
        skaters_df = _get_combined_df(html_dfs[0: int(len(html_dfs) / 2)])
        goalies_df = _get_combined_df(html_dfs[int(len(html_dfs) / 2):])

        # Fill output data
        file_dicts.append({'file_dir': file_dir, 'team_name': team_name, 'owner_name': owner_name,
                           'league_name': league_name, 'skaters_df': skaters_df, 'goalies_df': goalies_df })

    return file_dicts

def to_csvs(in_file_paths):
    """ Parses input files and outputs to individual CSV files. """
    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # File basename with special characters strip (add special character regex as needed)
        file_basename = f"{file_dict['team_name']} ({file_dict['owner_name']}) - {file_dict['league_name']}"
        file_basename = re.sub(r"[^A-Za-z0-9 \-()]+", "_", file_basename)

        skaters_out_file_path = os.path.join(file_dict['file_dir'], file_basename + " - Skaters.csv")
        file_dict['skaters_df'].to_csv(skaters_out_file_path, index=False)
        print("Output to: {}".format(skaters_out_file_path))

        goalies_out_file_path = os.path.join(file_dict['file_dir'], file_basename  + " - Goalies.csv")
        file_dict['goalies_df'].to_csv(goalies_out_file_path, index=False)
        print("Output to: {}".format(goalies_out_file_path))

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
    arg_parser.add_argument('-i', nargs='+', required=True, help="Input HTML file(s).")
    args = arg_parser.parse_args()
    to_csvs(args.i)
    print("Done.\n")