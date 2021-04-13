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
import espn_league_rosters_html_parser
import espn_utils
import os
import re

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

def _move_files(src_folder, dest_folder, file_ext):
    """ Helper function that moves all files with given file extension from source to destination folder. """
    # Find files with given file extension in source folder
    print(f"Moving {file_ext} files from {src_folder} to {dest_folder}")
    files_to_move = []
    for f in os.listdir(src_folder):
        if f.endswith(file_ext):
            files_to_move.append(f)

    # Create destination folder if it doesn't exist
    if not os.path.exists(dest_folder):
        os.mkdir(dest_folder)

    # Move all files to destination folder - overwrite if it already exists
    for f in files_to_move:
        src_file_path = os.path.join(src_folder, f)
        dest_file_path = os.path.join(dest_folder, f)
        os.replace(src_file_path, dest_file_path)

if __name__ == "__main__":
    """ Main function. """
    # Read arguments
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-d', required=True, help="Input directory containing folder or folders of HTML pages to parse.")
    arg_parser.add_argument('-ch', required=False, action='store_true', help="Option to parse clubhouse files.")
    arg_parser.add_argument('-dr', required=False, action='store_true', help="Option to parse draft recap files.")
    arg_parser.add_argument('-lr', required=False, action='store_true', help="Option to parse league roster files.")
    arg_parser.add_argument('-all', required=False, action='store_true', help="Option to parse all files. Overrides all other options.")
    args = arg_parser.parse_args()

    # If parsing all, override all arguments
    if args.all:
        args.ch = True
        args.dr = True
        args.lr = True

    # Set-up common variables
    root_dir = args.d

    # Parsing clubhouse files
    if args.ch:
        print("\n------------------------------------------- Parsing ESPN clubhouse HTML files -------------------------------------------")
        file_paths = _find_files_recursive(root_dir, espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE)
        espn_clubhouse_html_parser.to_csvs(file_paths)
        espn_clubhouse_html_parser.to_excel(file_paths)

    # Parsing draft recap files
    if args.dr:
        print("\n------------------------------------------ Parsing ESPN draft recap HTML files ------------------------------------------")
        file_paths = _find_files_recursive(root_dir, espn_utils.FILE_NAME_RE_FORMAT_DRAFT_RECAP)
        espn_draft_recap_html_parser.to_csv(file_paths)
        espn_draft_recap_html_parser.to_excel(file_paths)

    # Parsing league roster files
    if args.lr:
        print("\n------------------------------------------ Parsing ESPN league roster HTML files ----------------------------------------")
        file_paths = _find_files_recursive(root_dir, espn_utils.FILE_NAME_RE_FORMAT_LEAGUE_ROSTERS)
        espn_league_rosters_html_parser.to_csv(file_paths)
        espn_league_rosters_html_parser.to_excel(file_paths)

    # Move files into folders
    # Find folder paths that contain HTML files because that is likely where all the output files are to move
    print("\n--------------------------------------------------- Moving output files -------------------------------------------------")
    folder_paths_with_html = _find_folders_with_html(root_dir)
    for folder_path in folder_paths_with_html:
        _move_files(folder_path, os.path.join(folder_path, "csv"), ".csv")
        _move_files(folder_path, os.path.join(folder_path, "excel"), ".xlsx")

    # Done!
    print("Done.")