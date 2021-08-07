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

sys.path.insert(1, os.path.join(sys.path[0], "..", "espn_statsapi_scripts"))
import espn_statsapi_utils

def get_file_dicts(in_file_paths):
    """ Parses and returns a list of dictionaries corresponding to draft recap information for given input HTML files.
        Return data structure has the form:
        [ { 'file_dir': "file_dir1", 'league_name': "league_nameA", ..., 'df': df1 },
          { 'file_dir': "file_dir2", 'league_name': "league_nameB", ..., 'df': df2 },
          { 'file_dir': "file_dir3", 'league_name': "league_nameC", ..., 'df': df3 },
          ...
        ]
    """
    file_dicts = []
    for in_file_path in in_file_paths:
        file_dir = os.path.dirname(in_file_path)
        print("Processing: {}".format(in_file_path))

        # Parse
        html_dfs = pd.read_html(in_file_path)
        combined_df = _get_combined_df(html_dfs)

        # Read and parse HTML for various tags
        soup = BeautifulSoup(open(in_file_path, 'r'), 'html.parser')

        # Apparently can get league info from this obscure header and its common across the HTML pages I've inspected
        # Note: Won't be surprised if this might not work elsewhere
        league_name = ""
        league_name_tags = soup.find_all('h3', class_="jsx-1532665337 subHeader")
        try:
            league_name = league_name_tags[0].text
        except:
            # Intentional catch-all and pass since this method seems kind of hacky to begin with
            pass

        # Fill output data
        file_dicts.append({'file_dir': file_dir, 'league_name': league_name, 'df': combined_df })

    return file_dicts

def to_csv(in_file_paths):
    """ Parses input files and outputs to CSV file. """
    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # File basename with special characters strip (add special character regex as needed)
        file_basename = _strip_special_chars(f"Draft Recap - {file_dict['league_name']}")
        out_file_path = os.path.join(file_dict['file_dir'], file_basename + ".csv")

        file_dict['df'].to_csv(out_file_path, index=False)
        print("Output to: {}".format(out_file_path))

def to_excel(in_file_paths):
    """ Parses input files and outputs to Excel file. """
    file_dicts = get_file_dicts(in_file_paths)
    for file_dict in file_dicts:
        # Use league name as the output file
        # Output dataframes into individual sheets of specified file
        file_basename = _strip_special_chars(f"Draft Recap - {file_dict['league_name']}")
        out_file_path = os.path.join(file_dict['file_dir'], file_basename + ".xlsx")

        # Output to Excel file
        file_dict['df'].to_excel(out_file_path, index=False)
        print("Output to: {}".format(out_file_path))

def to_pickle(in_file_paths):
    """ Parses input files and outputs to pickle. """
    file_dicts = get_file_dicts(in_file_paths)

    # First, get the directory from where input file is from
    output_pickles_dict = {}
    for file_dict in file_dicts:
        # Use the file directory and league name as the pickle output path and store as a key
        file_name = _strip_special_chars(f"Draft Recap - {file_dict['league_name']}")
        file_path = os.path.join(file_dict['file_dir'], file_name + ".pickle")

        # First remove unnecessary keys from current dictionary
        del file_dict['file_dir']
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

def _get_combined_df(df_list):
    """ Combines list of dataframes into one big list. """
    combined_df = pd.DataFrame()
    for df in df_list:
        combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

    # Rename "Team" column to differentiate between player's actual NHL team, 
    # and name of a team in the fantasy league.
    combined_df = combined_df.rename(columns={'Team': "ESPN Fantasy Team"})

    # Player column strings contain data nested in them, clean that up
    combined_df = _modify_player_col(combined_df)

    # Clean-up dataframe and re-index. Use re-index values + 1 as number count
    combined_df = combined_df.drop('NO.', axis=1)
    combined_df.index = range(1, len(combined_df) + 1)
    combined_df = combined_df.reset_index()
    combined_df = combined_df.rename(columns={'index': 'Draft Number'})
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

    return df

def _strip_special_chars(input_str):
    """ Helper function to strip special characters and replace them with an underscore. """
    # Add special character regex as needed
    return re.sub(r"[^A-Za-z0-9 \-!@#$%^&(),']+", "_", input_str)

if __name__ == "__main__":
    """ Main function. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', nargs='+', required=True, help="Input HTML file(s).")
    args = arg_parser.parse_args()
    to_csv(args.i)
    to_excel(args.i)
    to_pickle(args.i)
    print("Done.\n")