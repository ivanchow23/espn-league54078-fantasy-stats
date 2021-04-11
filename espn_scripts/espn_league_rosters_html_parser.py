#!/usr/bin/env python
""" Parses an ESPN league rosters HTML page and saves to CSV files. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import re

def get_file_dicts(in_file_paths):
    """ Parses and returns a list of dictionaries corresponding to league roster information for given input HTML files.
        Return data structure has the form:
        [ { 'file_dir': "file_dir1", 'file_basename': "file_basename1", 'team_rosters': { 'team_name1': roster_df1,
                                                                                          'team_name2': roster_df2,
                                                                                          'team_name3': roster_df3,
                                                                                          ...
                                                                                        } },

          { 'file_dir': "file_dir2", 'file_basename': "file_basename2", 'team_rosters': { 'team_nameA': roster_dfA,
                                                                                          'team_nameB': roster_dfB,
                                                                                          'team_nameC': roster_dfC,
                                                                                          ...
                                                                                        } },
          ...
        ]
    """
    file_dicts = []
    for in_file_path in in_file_paths:
        # File paths and basenames
        file_dir = os.path.dirname(in_file_path)
        file_basename = os.path.splitext(os.path.basename(in_file_path))[0]
        file_basename = _get_file_basename(file_basename)
        print("Processing: {}".format(in_file_path))

        # Read HTML file for all tables/data
        html_dfs = pd.read_html(in_file_path)

        # Read HTML file for team names
        soup = BeautifulSoup(open(in_file_path, 'r'), 'html.parser')
        team_name_span_tags = soup.find_all('span', class_='teamName')

        # Each tag's title should correspond in the same order as the list of dataframes
        # Check that number of tables match the number of tags
        if len(team_name_span_tags) != len(html_dfs):
            print("Length of title tags don't match length of HTML dataframes. Skipping...")
            continue

        # Get team roster information
        # Assumes indicies/order of the tag list matches the indicies/order of the dataframes
        # TODO: Known issue where this will overwrite an existing team key if same team names exist as duplicates
        team_rosters_dict = {}
        for span_tag, df in zip(team_name_span_tags, html_dfs):
            team_rosters_dict[span_tag['title']] = df

        # Fill output data
        file_dicts.append({'file_dir': file_dir, 'file_basename': file_basename, 'team_rosters': team_rosters_dict})

    return file_dicts

def to_csv(in_file_paths):
    """ Parses input files and outputs to CSV file. """
    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        team_rosters_output_path = os.path.join(file_dict['file_dir'], file_dict['file_basename'] + ".csv")
        team_rosters_df = _get_team_rosters_df(file_dict['team_rosters'])
        team_rosters_df.to_csv(team_rosters_output_path, index=False)
        print("Output to: {}".format(team_rosters_output_path))

def _get_file_basename(file_basename):
    """ Helper function to determine what file basename to use as output.
        ESPN league roster pages use a certain title format, which could
        get saved as the file name when saving as HTML. Otherwise, just use
        the base filename if it does not match expected title format. """
    # Found a match
    if(re.match(espn_utils.FILE_NAME_RE_FORMAT_LEAGUE_ROSTERS, file_basename)):
        # Strip some extra text from name
        file_basename = file_basename.replace(" - ESPN Fantasy Hockey", "")
        return file_basename
    # Just use original basename
    else:
        return file_basename

def _get_team_rosters_df(team_roster_dict):
    """ Combines dictionary of team roster dataframes into a single dataframe of all team rosters.
        Assumes input list structure in the form: { 'team_name1': team_df1, 'team_name2': team_df2, ... } """
    team_rosters_df = pd.DataFrame()

    for team_name, team_df in team_roster_dict.items():
        # First, modify the player columns to extract metadata information out of the strings
        mod_df = team_df.copy(deep=True)
        mod_df = _get_modified_player_df(mod_df)

        # Next, create a multi-indexed dataframe to combine team name and roster info together
        multi_idx_tuple_arr = [(team_name, col) for col in mod_df.columns]
        mod_df.columns = pd.MultiIndex.from_tuples(multi_idx_tuple_arr)

        # Combine with overall dataframe
        team_rosters_df = pd.concat([team_rosters_df, mod_df], axis=1)

    return team_rosters_df

def _get_modified_player_df(df):
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

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', required=True, help="Input HTML file.")
    args = arg_parser.parse_args()
    to_csv([args.i])
    print("Done.\n")