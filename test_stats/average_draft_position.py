#!/usr/bin/env python
""" Test stat that finds average draft position of each player drafted. """
import argparse
import os
import pandas as pd
import re

DRAFT_RECAP_CSV_FILE_NAME_RE = r"Draft Recap - [\W\w]+.csv"

if __name__ == "__main__":
    """ Usage: Enter folder containing folders of data from each season. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', required=True, help="Input directory containing folders of data of each season.")
    args = arg_parser.parse_args()
    root_folder_path = args.d

    # Find all draft recap files
    file_paths_list = []
    for root, dirs, files in os.walk(root_folder_path):
        for f in files:
            if re.match(DRAFT_RECAP_CSV_FILE_NAME_RE, f):
                file_paths_list.append(os.path.join(root, f))

    # Read in files and combine to dataframe
    combined_df = pd.DataFrame()
    for file_path in file_paths_list:
        file_df = pd.read_csv(file_path)
        combined_df = pd.concat([combined_df, file_df], axis=0, ignore_index=True)

    grouped_df = combined_df.groupby(['Player'])['Draft Number'].agg(['count', 'mean', 'min', 'max']).round(0)
    grouped_df = grouped_df.rename(columns={'count': '# Times Drafted',
                                            'mean': 'Average Draft Position',
                                            'min': 'Highest Position',
                                            'max': 'Lowest Position'})

    grouped_df = grouped_df.sort_values(by='Average Draft Position')
    grouped_df.to_csv("avg_draft_pos.csv")
