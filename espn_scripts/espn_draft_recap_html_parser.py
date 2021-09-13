#!/usr/bin/env python
""" Parses an ESPN fantasy roster recap HTML page. """
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

def get_file_dict(draft_recap_html_path, clubhouse_html_paths):
    """ Parses the HTML files and returns dictionary of various information.
        Assumes all HTML files to be from the same season and league. """
    # Parse
    html_dfs = pd.read_html(draft_recap_html_path)

    # Read and parse HTML for various tags
    soup = BeautifulSoup(open(draft_recap_html_path, 'r'), 'html.parser')

    # Apparently can get league info from this obscure header and its common across the HTML pages I've inspected
    # Note: Won't be surprised if this might not work elsewhere
    league_name = ""
    league_name_tags = soup.find_all('h3', class_="jsx-1532665337 subHeader")
    try:
        league_name = league_name_tags[0].text
    except:
        # Intentional catch-all and pass since this method seems kind of hacky to begin with
        pass

    # Load correction file (designed to have only up to one per folder)
    # Create correction object regardless if file exists or not
    file_dir = os.path.dirname(draft_recap_html_path)
    corr_file_path = ""
    corr_file_paths = [f for f in os.listdir(file_dir) if "corrections" in f]
    if len(corr_file_paths) > 0:
        corr_file_path = os.path.join(file_dir, corr_file_paths[0])
    global espn_statsapi_corr
    espn_statsapi_corr = espn_statsapi_utils.CorrectionUtil(corr_file_path)

    # Combine dataframes
    combined_df = _get_combined_df(html_dfs)

    # Read clubhouse files to parse for owner names
    team_owner_dicts = []
    for html_path in clubhouse_html_paths:
        # Read clubhouse HTML file
        html_dfs = pd.read_html(html_path)

        # Read HTML file for various information
        soup = BeautifulSoup(open(html_path, 'r'), 'html.parser')

        # Parse for team name from file name
        team_name = ""
        file_name = os.path.basename(html_path)
        if len(file_name.split(" Clubhouse")) != 0:
            team_name = file_name.split(" Clubhouse")[0]

        # Parse for owner name
        owner_name = ""
        team_details_sec_span_tags = soup.find_all('span', class_='team-details-secondary')
        for tag in team_details_sec_span_tags:
            owner_name_search = tag.find('span', class_='owner-name')
            if owner_name_search:
                owner_name = owner_name_search.text

        # Add team and owner name to list
        team_owner_dicts.append({'Team Name': team_name, 'Owner Name': owner_name})

    # Merge owner names to combined dataframe
    team_owner_df = pd.DataFrame(team_owner_dicts)
    combined_df = combined_df.merge(team_owner_df, on="Team Name", how='left')

    return {'league_name': league_name, 'df': combined_df }

def process(input_folder_path, root_output_path):
    """ Parses input file and outputs to various files. """
    logger.info(f"Processing: {input_folder_path}")

    # Find files based on name
    draft_recap_html_paths = _find_files_recursive(input_folder_path, espn_utils.FILE_NAME_RE_FORMAT_DRAFT_RECAP)
    if len(draft_recap_html_paths) == 0:
        logger.info("No draft recap HTML files found to parse. Skipping...")
        return

    draft_recap_html_path = draft_recap_html_paths[0]
    clubhouse_html_paths = _find_files_recursive(input_folder_path, espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE)

    # Generate folders
    csv_folder_path = os.path.join(root_output_path, "csv")
    excel_folder_path = os.path.join(root_output_path, "excel")
    pickles_folder_path = os.path.join(root_output_path, "pickles")
    os.makedirs(csv_folder_path, exist_ok=True)
    os.makedirs(excel_folder_path, exist_ok=True)
    os.makedirs(pickles_folder_path, exist_ok=True)

    # Parse
    file_dict = get_file_dict(draft_recap_html_path, clubhouse_html_paths)
    file_basename = _strip_special_chars(f"Draft Recap - {file_dict['league_name']}")

    # CSV output
    out_file_path = os.path.join(csv_folder_path, file_basename + ".csv")
    file_dict['df'].to_csv(out_file_path, index=False)
    logger.info(f"Output: {out_file_path}")

    # Excel output
    out_file_path = os.path.join(excel_folder_path, file_basename + ".xlsx")
    file_dict['df'].to_excel(out_file_path, index=False)
    logger.info(f"Output: {out_file_path}")

    # Pickle output
    out_file_path = os.path.join(pickles_folder_path, file_basename + ".pickle")
    pickle.dump(file_dict['df'], open(out_file_path, 'wb'))
    logger.info(f"Output: {out_file_path}")

def _get_combined_df(df_list):
    """ Combines list of dataframes into one big list. """
    combined_df = pd.DataFrame()
    for df in df_list:
        combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

    # Rename "Team" column to differentiate between player's actual NHL team,
    # and name of a team in the fantasy league.
    combined_df = combined_df.rename(columns={'Team': "Team Name"})

    # Player column strings contain data nested in them, clean that up
    combined_df = _modify_player_col(combined_df)

    # Clean-up dataframe and re-index. Use re-index values + 1 as number count
    combined_df = combined_df.drop('NO.', axis=1)
    combined_df.index = range(1, len(combined_df) + 1)
    combined_df = combined_df.reset_index()
    combined_df = combined_df.rename(columns={'index': 'Draft Number'})

    # Replace special characters in the team name to stay consistent with file names
    combined_df['Team Name'] = combined_df['Team Name'].apply(_strip_special_chars)

    return combined_df

def _modify_player_col(df):
    """ Extracts metadata from the player strings in the player columns.
        Cleans player strings and inserts extra metadata columns. """
    # Parse for additional metadata embedded in the player strings
    player_metadata_dict_list = []
    for player in df['Player']:
        player_metadata_dict_list.append(espn_utils.parse_draft_metadata_from_player_str(player))

    # New dataframe to add into original
    new_player_df = pd.DataFrame(player_metadata_dict_list)

    # Drop player column from original dataframe and insert new dataframe in its place
    col_index = df.columns.get_loc('Player')
    df = df.drop(columns='Player')
    for new_col in new_player_df.columns:
        df.insert(col_index, new_col, new_player_df[new_col])
        col_index += 1

    # Map team abbreviations
    df['Team'] = df['Team'].apply(lambda str: espn_statsapi_utils.statsapi_team_abbrev(str))

    # Map player corrections
    if espn_statsapi_corr.valid:
        # Iterating through dataframes is not intended, but it's currently the simplist way
        for index, row in df.iterrows():
            # Apply correction if needed
            corrected_dict = espn_statsapi_corr.get_corrected_dict(row['Player'], row['Team'])
            if corrected_dict:
                logger.info(f"Correction: {row['Player']} {row['Team']} -> {corrected_dict['Corrected Player']} {corrected_dict['Corrected Team']}")
                df.at[index, 'Player'] = corrected_dict['Corrected Player']
                df.at[index, 'Team'] = corrected_dict['Corrected Team']
    return df

def _find_files_recursive(root_folder, file_pattern_re):
    """ Recursively finds files with given pattern in a root folder. """
    file_paths_list = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if re.match(file_pattern_re, f):
                file_paths_list.append(os.path.join(root, f))
    return file_paths_list

def _strip_special_chars(input_str):
    """ Helper function to strip special characters and replace them with an underscore. """
    # Add special character regex as needed
    return re.sub(r"[^A-Za-z0-9 \-!@#$%^&(),']+", "_", input_str)

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', required=True, help="Input directory containing draft recap and clubhouse HTML files.")
    args = arg_parser.parse_args()
    folder_path = args.d
    process(folder_path, folder_path)