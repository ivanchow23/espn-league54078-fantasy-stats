#!/usr/bin/env python
""" Parses various ESPN HTML pages for standings information. """
import argparse
from bs4 import BeautifulSoup
import espn_utils
import os
import pandas as pd
import pickle
import re

import espn_logger
logger = espn_logger.logger()

def get_dict(league_roster_html_path, clubhouse_html_paths):
    """ Parses the HTML files and returns dictionary of various information.
        Assumes all HTML files to be from the same season and league. """
    # Read league roster HTML file for all tables/data and update dataframes to get proper parsing
    html_dfs = pd.read_html(league_roster_html_path)

    # Read HTML file for various information
    soup = BeautifulSoup(open(league_roster_html_path, 'r'), 'html.parser')

    # Parse for team name and number of points and add to list
    standings_dicts = []
    for rank, (team_name_span_tag, pts_span_tag) in enumerate(zip(soup.find_all('span', class_='teamName'), soup.find_all('span', class_='pl2'))):
        standings_dicts.append({'Rank': rank + 1,
                                'Team Name': team_name_span_tag['title'],
                                'Points': int(re.findall(r"\d+", pts_span_tag.text)[0])})

    # Apparently can get league info from this obscure header and its common across the HTML pages I've inspected
    league_name = ""
    league_name_tags = soup.find_all('h3', class_="jsx-1532665337 subHeader")
    try:
        league_name = league_name_tags[0].text
    except:
        # Intentional catch-all and pass since this method seems kind of hacky to begin with
        pass

    # Read clubhouse files to parse for owner names
    team_owner_dicts = []
    for html_path in clubhouse_html_paths:
        # Read clubhouse HTML file
        html_dfs = pd.read_html(html_path)

        # Read HTML file for various information
        soup = BeautifulSoup(open(html_path, 'r'), 'html.parser')

        # Parse for team name
        team_name = ""
        team_name_span_tags = soup.find_all('span', class_='teamName')
        for tag in team_name_span_tags:
            try:
                team_name = tag['title']
            except KeyError:
                # Intentional pass - try next tag
                pass

        # Parse for owner name
        owner_name = ""
        team_details_sec_span_tags = soup.find_all('span', class_='team-details-secondary')
        for tag in team_details_sec_span_tags:
            owner_name_search = tag.find('span', class_='owner-name')
            if owner_name_search:
                owner_name = owner_name_search.text

        # Add team and owner name to list
        team_owner_dicts.append({'Team Name': team_name, 'Owner Name': owner_name})

    # Merge all the data together and reorder columns as needed
    standings_df = pd.DataFrame(standings_dicts)
    team_owner_df = pd.DataFrame(team_owner_dicts)
    combined_df = standings_df.merge(team_owner_df, on='Team Name', how='outer')
    combined_df = combined_df[['Rank', 'Team Name', 'Owner Name', 'Points']]

    return {'league_name': league_name, 'df': combined_df}

def process(input_folder_path, root_output_path):
    """ Parses input files from given directory and outputs to various files. """
    logger.info(f"Processing: {input_folder_path}")

    # Find files based on name
    league_roster_html_path = _find_files_recursive(input_folder_path, espn_utils.FILE_NAME_RE_FORMAT_LEAGUE_ROSTERS)[0]
    clubhouse_html_paths = _find_files_recursive(input_folder_path, espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE)

    # Generate folders
    csv_folder_path = os.path.join(root_output_path, "csv")
    excel_folder_path = os.path.join(root_output_path, "excel")
    pickles_folder_path = os.path.join(root_output_path, "pickles")
    os.makedirs(csv_folder_path, exist_ok=True)
    os.makedirs(excel_folder_path, exist_ok=True)
    os.makedirs(pickles_folder_path, exist_ok=True)

    # Parse
    file_dict = get_dict(league_roster_html_path, clubhouse_html_paths)
    file_basename = _strip_special_chars(f"League Standings - {file_dict['league_name']}")

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
    arg_parser.add_argument('-d', required=True, help="Input directory containing league roster and clubhouse HTML files.")
    args = arg_parser.parse_args()
    folder_path = args.d
    process(folder_path, folder_path)