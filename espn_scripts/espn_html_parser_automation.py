#!/usr/bin/env python
""" This script is meant to help auto-generate files across folders easier.
    Given a root folder:
      1. Recursively searches for other folders within.
      2. Looks for file names in a certain format.
      3. Calls the appropriate ESPN HTML parsing script to generate files.
    File names must be in a certain format to be parsed.
"""
import argparse
import espn_clubhouse_html_parser
import espn_draft_recap_html_parser
import espn_standings_html_parser
import espn_utils
import os
import re
import timeit

def _find_files_recursive(root_folder, file_pattern_re):
    """ Recursively finds files with given pattern in a root folder. """
    file_paths_list = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if re.match(file_pattern_re, f):
                file_paths_list.append(os.path.join(root, f))
    return file_paths_list

def _find_folders_with_html(root_folder):
    """ Recursively finds all folders that contain at least one HTML file. """
    folder_paths_list = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if f.endswith(".html"):
                folder_paths_list.append(root)
                break
    return folder_paths_list

if __name__ == "__main__":
    """ Main function. """
    # Read arguments
    start_time = timeit.default_timer()
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', required=True, help="Input directory containing folder or folders of HTML pages to parse.")
    args = arg_parser.parse_args()

    # Set-up common variables
    root_dir = args.d
    folder_paths = _find_folders_with_html(root_dir)

    print("\n------------------------------------------- Parsing ESPN clubhouse HTML files -------------------------------------------")
    for folder_path in folder_paths:
        file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE)
        espn_clubhouse_html_parser.process(file_paths, folder_path)

    print("\n------------------------------------------ Parsing ESPN draft recap HTML files ------------------------------------------")
    for folder_path in folder_paths:
        file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_DRAFT_RECAP)
        for file_path in file_paths:
            espn_draft_recap_html_parser.process(file_path, folder_path)

    print("\n-------------------------------------------- Parsing ESPN standings HTML files ------------------------------------------")
    for folder_path in folder_paths:
        espn_standings_html_parser.process(folder_path, folder_path)

    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")