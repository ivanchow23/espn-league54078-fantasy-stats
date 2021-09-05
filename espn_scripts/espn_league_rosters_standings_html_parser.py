#!/usr/bin/env python
""" Parses an ESPN league rosters HTML page for standings information. """
import argparse
from bs4 import BeautifulSoup
import os
import pandas as pd
import pickle
import re

import espn_logger
logger = espn_logger.logger()

def get_dict(html_path):
    """ Parses the HTML file and returns dictionary of various information. """
    logger.info(f"Processing: {html_path}")

    # Read HTML file for all tables/data and update dataframes to get proper parsing
    html_dfs = pd.read_html(html_path)

    # Read HTML file for various information
    soup = BeautifulSoup(open(html_path, 'r'), 'html.parser')

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

    return {'league_name': league_name, 'df': pd.DataFrame(standings_dicts)}

def to_csv(html_path, root_output_path):
    """ Parses input files and outputs to CSV file. """
    output_folder_path = os.path.join(root_output_path, "csv")
    os.makedirs(output_folder_path, exist_ok=True)

    file_dict = get_dict(html_path)
    file_basename = _strip_special_chars(f"League Standings - {file_dict['league_name']}")
    out_file_path = os.path.join(output_folder_path, file_basename + ".csv")
    file_dict['df'].to_csv(out_file_path, index=False)
    logger.info(f"Output: {out_file_path}")

def to_excel(html_path, root_output_path):
    """ Parses input files and outputs to Excel file. """
    output_folder_path = os.path.join(root_output_path, "excel")
    os.makedirs(output_folder_path, exist_ok=True)

    file_dict = get_dict(html_path)
    file_basename = _strip_special_chars(f"League Standings - {file_dict['league_name']}")
    out_file_path = os.path.join(output_folder_path, file_basename + ".xlsx")
    with pd.ExcelWriter(out_file_path, engine='openpyxl') as excel_writer:
        file_dict['df'].to_excel(excel_writer, index=False)
    logger.info(f"Output: {out_file_path}")

def to_pickle(html_path, root_output_path):
    """ Parses input files and outputs to pickle. """
    output_folder_path = os.path.join(root_output_path, "pickles")
    os.makedirs(output_folder_path, exist_ok=True)

    file_dict = get_dict(html_path)
    file_basename = _strip_special_chars(f"League Standings - {file_dict['league_name']}")
    out_file_path = os.path.join(output_folder_path, file_basename + ".pickle")
    pickle.dump(file_dict['df'], open(out_file_path, 'wb'))
    logger.info(f"Output: {out_file_path}")

def _strip_special_chars(input_str):
    """ Helper function to strip special characters and replace them with an underscore. """
    # Add special character regex as needed
    return re.sub(r"[^A-Za-z0-9 \-!@#$%^&(),']+", "_", input_str)

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', required=True, help="Input HTML file(s).")
    args = arg_parser.parse_args()

    # Assumes all input files are from same directory
    output_folder_path = os.path.dirname(args.i)
    to_csv(args.i, output_folder_path)
    to_excel(args.i, output_folder_path)
    to_pickle(args.i, output_folder_path)