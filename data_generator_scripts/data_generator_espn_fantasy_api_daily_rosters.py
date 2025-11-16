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
        self._pbar = None

    def update_progress_bar(self, season, current_count, total_count):
        """ Function handler to update and show progress bar. """
        if self._pbar is None:
            self._pbar = tqdm(total=total_count, desc=f"Processing {season}",
                              bar_format="{desc}: |{bar:20}| {percentage:3.0f}% [{n_fmt}/{total_fmt}] [{elapsed}]")

        self._pbar.update(1)

        if current_count == total_count:
            self._pbar.close()
            self._pbar = None

class ProgressHandlerMultiprocess():
    """ Helper class to handle progress updates processing daily rosters data
        when using multiprocessing. Simply prints basic information for now.
        There is a known issue with tqdm and positioning multiple progress
        bars at once: https://github.com/tqdm/tqdm/issues/1000. """
    def __init__(self):
        """ Default constructor. """
        self._start_time = 0

    def update_progress_bar(self, season, current_count, total_count):
        """ Print to console. Uses same name as ProgressHandler.update_progress_bar
            to tempoarily simplify integration with main code. """
        if current_count == 1:
            print(f"Processing {season}...")
            self._start_time = timeit.default_timer()

        if current_count == total_count:
            print(f"Processing {season} [{current_count}/{total_count}] finished in {round(timeit.default_timer() - self._start_time, 1)}s.")

if __name__ == "__main__":
    start_time = timeit.default_timer()

    parser = argparse.ArgumentParser()
    parser.add_argument("--espn_fantasy_api_downloads_root_folder", type=str, default=DEFAULT_ESPN_FANTASY_API_DOWNLOADS_ROOT_FOLDER,
                        help="Root folder path containing ESPN Fantasy API downloaded files.")
    parser.add_argument("--out_dir_path", type=str, default=DEFAULT_OUTPUT_DIR,
                        help="Output directory path to save generated data.")
    args = parser.parse_args()

    print("Generating ESPN fantasy API daily rosters data...")
    parser = EspnFantasyApiDownloadsParser(args.espn_fantasy_api_downloads_root_folder)
    multiprocess = True

    # Set-up progress bar handling
    progress_handlers = []
    progress_handlers_funcs = {}
    for i, season_string in enumerate(parser.get_seasons()):
        if multiprocess:
            p = ProgressHandlerMultiprocess()
        else:
            p = ProgressHandler()
        progress_handlers.append(p)
        progress_handlers_funcs[season_string] = p.update_progress_bar

    # Parse daily rosters data
    df = parser.get_daily_rosters_df(progress_func_handlers=progress_handlers_funcs, multiprocess=multiprocess)
    df.to_csv(os.path.join(args.out_dir_path, "espn_fantasy_api_daily_rosters_df.csv"), index=False)

    # Finish
    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")