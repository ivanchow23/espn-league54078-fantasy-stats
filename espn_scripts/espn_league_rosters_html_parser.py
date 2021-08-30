#!/usr/bin/env python
""" Parses an ESPN league rosters HTML page and saves to CSV files. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import pickle
import re
import sys

sys.path.insert(1, os.path.join(sys.path[0], "..", "espn_statsapi_scripts"))
import espn_statsapi_utils

# Declare correction object global for simplicity of access in functions
espn_statsapi_corr = None

def get_file_dicts(in_file_paths):
    """ Parses and returns a list of dictionaries corresponding to league roster information for given input HTML files.
        Return data structure has the form:
        [ { 'league_name': "league_name1", 'team_rosters': { 'team_name1': { ... },
                                                                                      'team_name2': { ... },
                                                                                      'team_name3': { ... },
                                                                                       ...
                                                                                    } },

          { 'league_name': "league_name2", 'team_rosters': { 'team_nameA': { ... },
                                                                                      'team_nameB': { ... },
                                                                                      'team_nameC': { ... },
                                                                                       ...
                                                                                    } },
          ...
        ]
    """
    file_dicts = []
    for in_file_path in in_file_paths:
        file_dir = os.path.dirname(in_file_path)
        print("Processing: {}".format(in_file_path))

        # Read HTML file for all tables/data and update dataframes to get proper parsing
        html_dfs = pd.read_html(in_file_path)

        # Read HTML file for various information
        soup = BeautifulSoup(open(in_file_path, 'r'), 'html.parser')

        team_names_list = []
        for span_tag in soup.find_all('span', class_='teamName'):
            team_names_list.append(span_tag['title'])

        team_points_list = []
        for span_tag in soup.find_all('span', class_='pl2'):
            team_points_list.append(int(re.findall(r"\d+", span_tag.text)[0]))

        # Apparently can get league info from this obscure header and its common across the HTML pages I've inspected
        league_name = ""
        league_name_tags = soup.find_all('h3', class_="jsx-1532665337 subHeader")
        try:
            league_name = league_name_tags[0].text
        except:
            # Intentional catch-all and pass since this method seems kind of hacky to begin with
            pass

        # Tags should correspond in the same order as the list of dataframes
        # Check that number of tables match the number of tags
        if len(team_names_list) != len(html_dfs) or len(team_points_list) != len(html_dfs):
            print("Length of title tags don't match length of HTML dataframes. Skipping...")
            continue

        # Load correction file (designed to have only up to one per folder)
        # Create correction object regardless if file exists or not
        corr_file_path = ""
        corr_file_paths = [f for f in os.listdir(file_dir) if "corrections" in f]
        if len(corr_file_paths) > 0:
            corr_file_path = os.path.join(file_dir, corr_file_paths[0])
        global espn_statsapi_corr
        espn_statsapi_corr = espn_statsapi_utils.CorrectionUtil(corr_file_path)

        # Get team roster information
        # Assumes indicies/order of the tag list matches the indicies/order of the dataframes
        team_rosters_dict = {}
        for team_name, df, pts in zip(team_names_list, html_dfs, team_points_list):
            # Handle duplicate team names by appending some identifier
            team_name_key = team_name
            if team_name_key in team_rosters_dict:
                team_name_key += " (2)"

            team_rosters_dict[team_name_key] = {'roster_df': _get_modified_player_df(df), 'total_season_points': pts}

        # Fill output data
        file_dicts.append({'league_name': league_name, 'team_rosters': team_rosters_dict})

    return file_dicts

def to_csv(in_file_paths, root_output_path):
    """ Parses input files and outputs to CSV file. """
    output_folder_path = os.path.join(root_output_path, "csv")
    os.makedirs(output_folder_path, exist_ok=True)

    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # File basename with special characters strip (add special character regex as needed)
        file_basename = _strip_special_chars(f"League Rosters - {file_dict['league_name']}")

        # TODO: Think about if this should output league rosters into individual CSVs
        team_rosters_output_path = os.path.join(output_folder_path, file_basename + ".csv")
        team_rosters_df = _get_team_rosters_df(file_dict['team_rosters'])
        team_rosters_df.to_csv(team_rosters_output_path, index=False)
        print("Output to: {}".format(team_rosters_output_path))

def to_excel(in_file_paths, root_output_path):
    """ Parses input files and outputs to Excel file. """
    output_folder_path = os.path.join(root_output_path, "excel")
    os.makedirs(output_folder_path, exist_ok=True)

    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # Use league name as the output file
        # Output dataframes into individual sheets of specified file
        file_basename = _strip_special_chars(f"League Rosters - {file_dict['league_name']}")
        out_file_path = os.path.join(output_folder_path, file_basename + ".xlsx")

        # Add each team roster into its own sheet in the file
        for team_name_key, team_dict in file_dict['team_rosters'].items():
            # Excel writer can't make new file using just 'a' mode
            # First check if file already exists to append to, otherwise write to new file
            if os.path.exists(out_file_path):
                with pd.ExcelWriter(out_file_path, engine='openpyxl', mode='a') as excel_writer:
                    team_dict['roster_df'].to_excel(excel_writer, sheet_name=_strip_special_chars(team_name_key))
            else:
                with pd.ExcelWriter(out_file_path, engine='openpyxl') as excel_writer:
                    team_dict['roster_df'].to_excel(excel_writer, sheet_name=_strip_special_chars(team_name_key))

        print("Output to: {}".format(out_file_path))

def to_pickle(in_file_paths, root_output_path):
    """ Parses input files and outputs to pickle. """
    output_folder_path = os.path.join(root_output_path, "pickles")
    os.makedirs(output_folder_path, exist_ok=True)

    # First, get the directory from where input file is from
    output_pickles_dict = {}
    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # Use the file directory and league name as the pickle output path and store as a key
        file_name = _strip_special_chars(f"League Rosters - {file_dict['league_name']}")
        file_path = os.path.join(output_folder_path, file_name + ".pickle")

        # First remove unnecessary keys from current dictionary
        del file_dict['league_name']

        # Add dictionary into list if key exists
        if file_path in output_pickles_dict:
            output_pickles_dict[file_path].append(file_dict)
        # Otherwise create new list
        else:
            output_pickles_dict[file_path] = [file_dict]

    # Next, dump all pickles
    for out_file_path, data in output_pickles_dict.items():
        pickle.dump(data, open(out_file_path, 'wb'))
        print(f"Output to: {out_file_path}")

def _get_team_rosters_df(team_roster_dict):
    """ Combines dictionary of team roster dataframes into a single dataframe of all team rosters.
        Assumes input list structure in the form: { 'team_name1': { ... }, 'team_name2': { ... }, ... } """
    team_rosters_df = pd.DataFrame()

    for team_name, team_dict in team_roster_dict.items():
        mod_df = team_dict['roster_df'].copy(deep=True)

        # Create a multi-indexed dataframe to combine team name and roster info together
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

    # Map team abbreviations
    player_df['Team'] = player_df['Team'].apply(lambda str: espn_statsapi_utils.statsapi_team_abbrev(str))

    # Map player corrections
    if espn_statsapi_corr.valid:
        # Iterating through dataframes is not intended, but it's currently the simplist way
        for index, row in player_df.iterrows():
            # Apply correction if needed
            corrected_dict = espn_statsapi_corr.get_corrected_dict(row['Player'], row['Team'])
            if corrected_dict:
                print(f"Correction applied: {row['Player']} {row['Team']} -> {corrected_dict['Corrected Player']} {corrected_dict['Corrected Team']}")
                player_df.at[index, 'Player'] = corrected_dict['Corrected Player']
                player_df.at[index, 'Team'] = corrected_dict['Corrected Team']

    return player_df

def _strip_special_chars(input_str):
    """ Helper function to strip special characters and replace them with an underscore. """
    # Add special character regex as needed
    return re.sub(r"[^A-Za-z0-9 \-!@#$%^&(),']+", "_", input_str)

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', nargs='+', required=True, help="Input HTML file(s).")
    args = arg_parser.parse_args()

    # Assumes all input files are from same directory
    output_folder_path = os.path.dirname(args.i[0])
    to_csv(args.i, output_folder_path)
    to_excel(args.i, output_folder_path)
    to_pickle(args.i, output_folder_path)
    print("Done.\n")