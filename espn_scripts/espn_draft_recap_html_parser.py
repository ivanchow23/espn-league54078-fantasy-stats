#!/usr/bin/env python
""" Parses an ESPN fantasy roster recap HTML page and outputs to CSV. """
import argparse
from espn_utils import parse_draft_metadata_from_player_str
import os
import pandas as pd
import re

# Expected HTML title page format
HTML_TITLE_PAGE_RE_FORMAT = r"Draft Recap - [\W\w]+ - ESPN Fantasy Hockey"

def _get_file_basename(file_basename):
    """ Helper function to determine what file basename to use as output.
        ESPN draft recap pages use a certain title format, which could
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

def _get_combined_df(df_list):
    """ Combines list of dataframes into one big list. """
    combined_df = pd.DataFrame()
    for df in df_list:
        combined_df = pd.concat([combined_df, df], axis=0, ignore_index=True)

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
        player_metadata_dict_list.append(parse_draft_metadata_from_player_str(player))

    # New dataframe to add into original
    # Rename "Team" key to "NHL Team" to differentiate between ESPN fantasy team (uses same column name)
    new_player_df = pd.DataFrame(player_metadata_dict_list)
    new_player_df = new_player_df.rename(columns={'Team': 'NHL Team'})

    # Drop player column from original dataframe and insert new dataframe in its place
    col_index = df.columns.get_loc('Player')
    df = df.drop(columns='Player')
    for new_col in new_player_df.columns:
        df.insert(col_index, new_col, new_player_df[new_col])
        col_index += 1

    return df

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

    html_dfs = pd.read_html(in_file_path)
    combined_df = _get_combined_df(html_dfs)

    out_file_path = os.path.join(file_dir, file_basename + ".csv")
    combined_df.to_csv(out_file_path, index=False)
    print("Output to: {}".format(out_file_path))
    print("Done.\n")