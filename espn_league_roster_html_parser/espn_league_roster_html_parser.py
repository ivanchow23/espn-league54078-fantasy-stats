#!/usr/bin/env python
""" Parses an ESPN league roster HTML page and saves to CSV files.
    Outputs two CSV files: One contains each team's roster information.
    Second contains a combined list of players. """

import argparse
from bs4 import BeautifulSoup
import os
import pandas as pd
import re

# Expected HTML title page format
HTML_TITLE_PAGE_RE_FORMAT = r"[\W\w]+ - [\W\w]+ - ESPN Fantasy Hockey"

# List of NHL team abbreviations found in the page
NHL_TEAM_ABBREVIATIONS_LIST = ["Ana", "Ari", "Bos", "Buf", "Cgy", "Car", "Chi", "Col", "Cls", "Dal", "Det", "Edm",
                               "Fla", "LA", "Min", "Mon", "Nsh", "NJ", "NYI", "NYR", "Ott", "Phi", "Pit", "SJ", "StL",
                               "TB", "Tor", "Van", "Vgs", "Wsh", "Wpg"]

# List of injury designations found in the page
INJURY_DESIGNATION_LIST = ["IR", "O", "D", "DTD", "Q"]

def _get_file_basename(file_basename):
    """ Helper function to determine what file basename to use as output.
        ESPN league roster pages use a certain title format, which could
        get saved as the file name when saving as HTML. Otherwise, just use
        the base filename if it does not match expected title format. """
    # Found a match
    if(re.match(HTML_TITLE_PAGE_RE_FORMAT, file_basename)):
        # Strip some extra text from name
        file_basename = file_basename.replace(" - ESPN Fantasy Hockey", "")
        return file_basename
    # Just use original basename
    else:
        return file_basename

def _get_team_rosters_df(title_tags_list, df_list):
    """ Combines list of dataframes into a single dataframe of all team rosters using
        title tags to identify a team name. Assumes title tags list and dataframes
        list are in the same order. """
    team_rosters_df = pd.DataFrame()

    # Create a list of dictionaries to title with its dataframe
    # Assumes indicies/order of the tag list matches the indicies/order of the dataframes
    for index, df in enumerate(df_list):
        # First, modify the player columns to extract metadata information out of the strings
        mod_df = df.copy(deep=True)
        mod_df = _get_modified_player_df(mod_df)

        # Next, create a multi-indexed dataframe to combine team name and roster info together
        multi_idx_tuple_arr = [(title_tags_list[index]['title'], col) for col in mod_df.columns]
        mod_df.columns = pd.MultiIndex.from_tuples(multi_idx_tuple_arr)

        # Combine with overall dataframe
        team_rosters_df = pd.concat([team_rosters_df, mod_df], axis=1)

    return team_rosters_df

def _get_combined_players_list_df(df_list):
    """ Combines list of dataframes into a single list of players in a dataframe. """
    combined_players_df = pd.DataFrame()
    for df in df_list:
        # First, modify the player columns to extract metadata information out of the strings
        mod_df = df.copy(deep=True)
        mod_df = _get_modified_player_df(mod_df)

        # Combine with overall dataframe
        combined_players_df = pd.concat([combined_players_df, mod_df], axis=0)

    return combined_players_df

def _get_modified_player_df(df):
    """ Takes in a dataframe containing player information and outputs a
        new dataframe with modified and additional columns of information. """
    player_df = df

    # Parse for additional metadata embedded in the player strings
    player_metadata_dict_list = []
    for player in player_df['PLAYER']:
        player_metadata_dict_list.append(_parse_metadata_from_player_str(player))

    # Convert list of dictionaries to dataframe
    player_metadata_df = pd.DataFrame(player_metadata_dict_list)

    # Drop original player column and append new parsed information
    player_df = player_df.drop(columns='PLAYER')
    for col in player_metadata_df.columns:
        player_df[col] = player_metadata_df[col]

    return player_df

def _parse_metadata_from_player_str(player_str):
    """ Helper function that parses metadata combined into the player name string.
        Input format: "<First Name> <Last Name>"<Injury Designation><Team><Position>".
        Returns a dictionary containing player metadata.

        Example: "Steven StamkosOTBF"
        {'Player': "Steven Stamkos", 'Injury Designation': "O", 'Team': "TB", 'Positon': "F"}
    """
    player_dict = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}

    # Handle special case where the player name is literally empty
    if player_str == "Empty":
        return player_dict

    # First, parse last letter that indicates player's position
    # Handle special case where a player is eligible for multiple positions
    if player_str.endswith("D, F"):
        player_dict['Position'] = "D/F"
        player_str = player_str[:len(player_str) - len("D, F")]
    # Otherwise, simple case where last character is the player position
    else:
        player_dict['Position'] = player_str[-1]
        player_str = player_str[:len(player_str) - 1]

    # Parse for team abbreviation
    for team in NHL_TEAM_ABBREVIATIONS_LIST:
        if player_str.endswith(team):
            player_dict['Team'] = team
            player_str = player_str[:len(player_str) - len(team)]
            break

    # Parse for injury designation
    for status in INJURY_DESIGNATION_LIST:
        if player_str.endswith(status):
            player_dict['Injury Designation'] = status
            player_str = player_str[:len(player_str) - len(status)]
            break

    # We should just be left with player name here
    player_dict['Player'] = player_str
    return player_dict

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', required=True, help="Input HTML file.")
    args = arg_parser.parse_args()

    in_file_path = args.i
    file_dir = os.path.dirname(in_file_path)
    file_basename = os.path.splitext(os.path.basename(in_file_path))[0]
    file_basename = _get_file_basename(file_basename)
    print("Processing: {}".format(in_file_path))

    # Read HTML file for all tables/data
    html_dfs = pd.read_html(in_file_path)

    # Read HTML file for team names
    soup = BeautifulSoup(open(in_file_path, 'r'), 'html.parser')
    span_tags = soup.find_all('span', class_='teamName')

    # Each tag's title should correspond in the same order as the list of dataframes
    # Check that number of tables match the number of tags
    if len(span_tags) != len(html_dfs):
        print("Length of title tags don't match length of HTML dataframes. Exiting...")
        exit(-1)

    # Combine into a single dataframe that shows each team roster
    team_rosters_output_path = os.path.join(file_dir, file_basename + ".csv")
    team_rosters_df = _get_team_rosters_df(span_tags, html_dfs)
    team_rosters_df.to_csv(team_rosters_output_path, index=False)
    print("Output to: {}".format(team_rosters_output_path))

    # Combine into a single dataframe which contains a list of all players
    players_list_output_path = os.path.join(file_dir, file_basename + " - All Players.csv")
    players_list_df = _get_combined_players_list_df(html_dfs)
    players_list_df.to_csv(players_list_output_path, index=False)
    print("Output to: {}".format(players_list_output_path))
    print("Done.\n")