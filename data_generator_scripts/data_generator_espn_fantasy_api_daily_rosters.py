#!/usr/bin/env python
""" Generates ESPN fantasy API daily rosters data. """
import argparse
import os
import timeit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_fantasy_api_scripts"))
from espn_fantasy_api_downloads_parser import EspnFantasyApiDownloadsParser

DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER = os.path.join(SCRIPT_DIR, "..", "espn_fantasy_api_scripts", "espn_fantasy_api_downloads")
DEFAULT_OUTPUT_DIR = SCRIPT_DIR

if __name__ == "__main__":
    start_time = timeit.default_timer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--espn_fantasy_api_downloads_root_folder", type=str, default=DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER,
                        help="Root folder path containing ESPN Fantasy API downloaded files.")
    parser.add_argument("--out_dir_path", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory path to save generated data.")
    args = parser.parse_args()

    print("Generating ESPN fantasy API daily rosters data...")
    EspnFantasyApiDownloadsParser(args.espn_fantasy_api_downloads_root_folder).get_daily_rosters_df().to_csv(os.path.join(args.out_dir_path, "espn_fantasy_api_daily_rosters_df.csv"), index=False)
    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")