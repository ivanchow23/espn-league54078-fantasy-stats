#!/usr/bin/env python
""" Generates ESPN fantasy API daily rosters data. """
import argparse
from espn_fantasy_api_scripts.espn_fantasy_api_downloads_parser import EspnFantasyApiDownloadsParser
import os
import timeit
from tqdm import tqdm

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER = os.path.join(SCRIPT_DIR, "..", "espn_fantasy_api_scripts", "espn_fantasy_api_downloads")
DEFAULT_OUTPUT_DIR = SCRIPT_DIR

class ProgressHandler():
    """ Helper class to handle progress updates processing daily rosters data. """
    def __init__(self):
        """ Default constructor. """
        self._current_season = 0
        self._pbar = None
        self._pbar_active = False
        self._num_seasons = 0

    def update_progress_bar(self, season, current_count, total_count):
        """ Function handler to show progress bar. """
        # Create new progress bar for processing a new season
        if season != self._current_season:
            self._num_seasons += 1
            if self._pbar_active:
                self._pbar.close()

            self._current_season = season
            self._pbar = tqdm(total=total_count, desc=f"Processing {season}",
                              bar_format="{desc}: |{bar:20}| {percentage:3.0f}% [{n_fmt}/{total_fmt}] [{elapsed}]")
            self._pbar_active = True

        self._pbar.update(1)

    def close(self):
        """ Close the active progress bar cleanly. """
        if self._pbar_active and self._pbar is not None:
            self._pbar.close()
            self._pbar_active = False
            self._pbar = None

if __name__ == "__main__":
    start_time = timeit.default_timer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--espn_fantasy_api_downloads_root_folder", type=str, default=DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER,
                        help="Root folder path containing ESPN Fantasy API downloaded files.")
    parser.add_argument("--out_dir_path", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory path to save generated data.")
    args = parser.parse_args()

    print("Generating ESPN fantasy API daily rosters data...")
    progress_handler = ProgressHandler()
    df = EspnFantasyApiDownloadsParser(args.espn_fantasy_api_downloads_root_folder).get_daily_rosters_df(progress_func_handler=progress_handler.update_progress_bar)
    df.to_csv(os.path.join(args.out_dir_path, "espn_fantasy_api_daily_rosters_df.csv"), index=False)
    progress_handler.close()
    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")