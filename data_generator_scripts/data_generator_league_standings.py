#!/usr/bin/env python
""" Generates league standings data. """
import argparse
import os
import timeit

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
from espn_html_parser import EspnHtmlParser

DEFAULT_ESPN_HTML_ROOT_FOLDER = os.path.join(SCRIPT_DIR, "..", "espn_html_files")
DEFAULT_OUTPUT_DIR = SCRIPT_DIR

if __name__ == "__main__":
    start_time = timeit.default_timer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--espn_html_root_folder", type=str, default=DEFAULT_ESPN_HTML_ROOT_FOLDER,
                        help="Root folder path containing ESPN HTML files.")
    parser.add_argument("--out_dir_path", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory path to save generated data.")
    args = parser.parse_args()

    print("Generating league standings data...")
    EspnHtmlParser(args.espn_html_root_folder).get_league_standings_stats_df().to_csv(os.path.join(args.out_dir_path, "standings_stats_df.csv"), index=False)
    EspnHtmlParser(args.espn_html_root_folder).get_league_standings_points_df().to_csv(os.path.join(args.out_dir_path, "standings_points_df.csv"), index=False)
    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")