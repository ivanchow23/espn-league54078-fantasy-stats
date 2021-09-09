#!/usr/bin/env python
""" Parses an ESPN fantasy hockey clubhouse roster HTML page. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import pickle
import re
import sys

import espn_logger
logger = espn_logger.logger()

sys.path.insert(1, os.path.join(sys.path[0], "..", "espn_statsapi_scripts"))
import espn_statsapi_utils

# Declare correction object global for simplicity of access in functions
espn_statsapi_corr = None

# Number of expected tables in the HTML page
NUM_EXPECTED_HTML_TABLES = 6

def get_file_dicts(in_file_paths):
    """ Parses and returns a list of dictionaries corresponding to skater and goalie data for given input HTML files.
        Return data structure has the form:
        [ { 'skaters_df': skaters_df1, 'goalies_df': goalies_df1 ... },
          { 'skaters_df': skaters_df2, 'goalies_df': goalies_df2 ... },
          { 'skaters_df': skaters_df3, 'goalies_df': goalies_df3 ... },
          ...
        ]
    """
    file_dicts = []
    for in_file_path in in_file_paths:
        file_dir = os.path.dirname(in_file_path)

        # Read HTML file for all tables/data
        html_dfs = pd.read_html(in_file_path)

        # Check if HTML page contains at least expected number of tables
        if len(html_dfs) < NUM_EXPECTED_HTML_TABLES:
            logger.warning(f"Found {len(html_dfs)} tables (expected {NUM_EXPECTED_HTML_TABLES}). Skipping...")
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

        # Load correction file (designed to have only up to one per folder)
        # Create correction object regardless if file exists or not
        corr_file_path = ""
        corr_file_paths = [f for f in os.listdir(file_dir) if "corrections" in f]
        if len(corr_file_paths) > 0:
            corr_file_path = os.path.join(file_dir, corr_file_paths[0])
        global espn_statsapi_corr
        espn_statsapi_corr = espn_statsapi_utils.CorrectionUtil(corr_file_path)

        # Half the dataframes are used to parse for skater data and the other half for goalie data
        # Assumes first half of dataframes are for skater data, second half for goalie data
        skaters_df = _get_combined_df(html_dfs[0: int(len(html_dfs) / 2)])
        goalies_df = _get_combined_df(html_dfs[int(len(html_dfs) / 2):])

        # Fill output data
        file_dicts.append({'team_name': team_name, 'owner_name': owner_name, 'league_name': league_name,
                           'skaters_df': skaters_df, 'goalies_df': goalies_df })

    return file_dicts

def process(html_paths, root_output_path):
    """ Parses input files and outputs to various files. """
    [logger.info(f"Processing: {path}") for path in html_paths]

    # Generate folders
    csv_folder_path = os.path.join(root_output_path, "csv")
    excel_folder_path = os.path.join(root_output_path, "excel")
    pickles_folder_path = os.path.join(root_output_path, "pickles")
    os.makedirs(csv_folder_path, exist_ok=True)
    os.makedirs(excel_folder_path, exist_ok=True)
    os.makedirs(pickles_folder_path, exist_ok=True)

    # Parse
    file_dicts = get_file_dicts(html_paths)

    # CSV output
    for file_dict in file_dicts:
        file_basename = _strip_special_chars(f"{file_dict['team_name']} ({file_dict['owner_name']}) - {file_dict['league_name']}")
        skaters_out_file_path = os.path.join(csv_folder_path, file_basename + " - Skaters.csv")
        goalies_out_file_path = os.path.join(csv_folder_path, file_basename  + " - Goalies.csv")

        file_dict['skaters_df'].to_csv(skaters_out_file_path, index=False)
        file_dict['goalies_df'].to_csv(goalies_out_file_path, index=False)

        logger.info(f"Output: {skaters_out_file_path}")
        logger.info(f"Output: {goalies_out_file_path}")

    # Excel output
    for file_dict in file_dicts:
        # Use league name as the output file
        # Output dataframes into individual sheets of specified file
        file_basename = _strip_special_chars(f"Clubhouses - {file_dict['league_name']}")
        file_path = os.path.join(excel_folder_path, file_basename + ".xlsx")

        # Output to sheets in the Excel file
        skaters_sheet_name = _strip_special_chars(f"{file_dict['team_name']} ({file_dict['owner_name']}) - Skaters")
        goalies_sheet_name = _strip_special_chars(f"{file_dict['team_name']} ({file_dict['owner_name']}) - Goalies")

        # Excel writer can't make new file using just 'a' mode
        # First check if file already exists to append to, otherwise write to new file
        if os.path.exists(file_path):
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='a', if_sheet_exists='replace') as excel_writer:
                file_dict['skaters_df'].to_excel(excel_writer, sheet_name=skaters_sheet_name)
                file_dict['goalies_df'].to_excel(excel_writer, sheet_name=goalies_sheet_name)
        else:
            with pd.ExcelWriter(file_path, engine='openpyxl') as excel_writer:
                file_dict['skaters_df'].to_excel(excel_writer, sheet_name=skaters_sheet_name)
                file_dict['goalies_df'].to_excel(excel_writer, sheet_name=goalies_sheet_name)

        logger.info(f"Output: {file_path} (Sheet: {skaters_sheet_name})")
        logger.info(f"Output: {file_path} (Sheet: {goalies_sheet_name})")

    # Pickle output
    output_pickles_dict = {}
    for file_dict in file_dicts:
        # Use the file directory and league name as the pickle output path and store as a key
        file_name = _strip_special_chars(f"Clubhouses - {file_dict['league_name']}")
        file_path = os.path.join(pickles_folder_path, file_name + ".pickle")

        # First remove unnecessary keys from current dictionary
        del file_dict['league_name']

        # Add dictionary into list if key exists
        if file_path in output_pickles_dict:
            output_pickles_dict[file_path].append(file_dict)
        # Otherwise create new list
        else:
            output_pickles_dict[file_path] = [file_dict]

    # Next, dump to pickle
    for out_file_path, data in output_pickles_dict.items():
        pickle.dump(data, open(out_file_path, 'wb'))
        logger.info(f"Output: {out_file_path}")

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
        logger.error("Unknown key to access player information dataframe. Exiting...")
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

    # Map team abbreviations
    player_df[index_key, 'Team'] = player_df[index_key, 'Team'].apply(lambda str: espn_statsapi_utils.statsapi_team_abbrev(str))

    # Map player corrections
    if espn_statsapi_corr.valid:
        # Iterating through dataframes is not intended, but it's currently the simplist way
        for index, row in player_df[index_key].iterrows():
            # Apply correction if needed
            corrected_dict = espn_statsapi_corr.get_corrected_dict(row['Player'], row['Team'])
            if corrected_dict:
                # Note: Use "at" to change df values: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html
                # Note: Access an element in multi-index df as follows: https://stackoverflow.com/a/50002318
                logger.info(f"Correction: {row['Player']} {row['Team']} -> {corrected_dict['Corrected Player']} {corrected_dict['Corrected Team']}")
                player_df.at[index, (index_key, 'Player')] = corrected_dict['Corrected Player']
                player_df.at[index, (index_key, 'Team')] = corrected_dict['Corrected Team']

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
    process(args.i, output_folder_path)