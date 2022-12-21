#!/usr/bin/env python
""" Contains functionality to download data from ESPN fantasy API to local machine.
    Downloaded data will be organized into season folders. """
import argparse
from datetime import datetime
import json
import os
import sys
import timeit

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, "espn_fantasy_api_downloads")
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "utils"))
from requests_util import RequestsUtil

class EspnFantasyApiDownloader:
    def __init__(self, season, league_id, root_output_folder=DEFAULT_DOWNLOADS_DIR, cookies={}):
        """ Constructor. """
        # Store in a season string folder "XXXXYYYY"
        # Example: 2022 season corresponds to: "20212022"
        self._season_string = f"{season - 1}{season}"
        self._root_output_folder = os.path.join(root_output_folder, self._season_string)
        os.makedirs(self._root_output_folder, exist_ok=True)

        self._season = season
        self._league_id = league_id
        self._cookies = cookies

        # Older seasons used a different access point
        if season < 2018:
            self._req = RequestsUtil(f"https://fantasy.espn.com/apis/v3/games/fhl/leagueHistory/{league_id}?seasonId={season}&")
        else:
            self._req = RequestsUtil(f"https://fantasy.espn.com/apis/v3/games/fhl/seasons/{season}/segments/0/leagues/{league_id}?")

    def download_league_info(self):
        """ Downloads data containing general information about the league. """
        output_path = os.path.join(self._root_output_folder, f"{self._season_string}_league_info.json")
        print(f"Downloading to: {output_path}")
        start_time = timeit.default_timer()
        if not self._req.save_json_from_endpoint("view=mSettings&view=mTeam", output_path, cookies=self._cookies):
            print(f"Download failed.")
            return

        print(f"Downloaded in {round(timeit.default_timer() - start_time, 1)}s.")

    def download_realtime_stats(self):
        """ Downloads realtime data. Appends a datetime timestamp to the downloaded
            file to indicate when this was taken. """
        output_folder_path = os.path.join(self._root_output_folder, "realtime_stats")
        os.makedirs(output_folder_path, exist_ok=True)
        dt = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

        output_path = os.path.join(output_folder_path, f"{self._season_string}_realtime_stats_{dt}.json")
        print(f"Downloading to: {output_path}")
        start_time = timeit.default_timer()
        if not self._req.save_json_from_endpoint("view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam",
                                                 output_folder_path,
                                                 cookies=self._cookies):
            print(f"Download failed.")
            return

        print(f"Downloaded in {round(timeit.default_timer() - start_time, 1)}s.")

    def download_scoring_period(self, id):
        """ Downloads a single scoring period of the season and league. """
        output_folder_path = os.path.join(self._root_output_folder, "scoring_periods")
        os.makedirs(output_folder_path, exist_ok=True)

        output_path = os.path.join(output_folder_path, f"{self._season_string}_scoring_period{id}.json")
        print(f"Downloading to: {output_path}")
        start_time = timeit.default_timer()
        if not self._req.save_json_from_endpoint(f"scoringPeriodId={id}&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                                                 output_path,
                                                 cookies=self._cookies):
            print(f"Download failed.")
            return

        print(f"Downloaded in {round(timeit.default_timer() - start_time, 1)}s.")

    def download_scoring_periods(self):
        """ Downloads data for all scoring periods of the season and league.
            Depends on league information to be present to find the first and
            last scoring periods of the season. Ensure download_league_info()
            is called first. """
        output_folder_path = os.path.join(self._root_output_folder, "scoring_periods")
        os.makedirs(output_folder_path, exist_ok=True)

        # Read league information file to get scoring periods
        league_info_path = os.path.join(self._root_output_folder, f"{self._season_string}_league_info.json")
        league_info_json = json.load(open(league_info_path, 'r'))

        # Handle older season data formats
        if self._season < 2018:
            league_info_json = league_info_json[0]

        # Get start and end scoring periods
        try:
            scoring_period_id_start = league_info_json['status']['firstScoringPeriod']
            scoring_period_id_end = league_info_json['status']['finalScoringPeriod']
        except:
            print("Cannot get start/end scoring period IDs. Skipping download...")
            return

        # Build links to download rosters for each scoring periods
        download_dict_list = [{'endpoint': f"scoringPeriodId={id}&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                               'out_file_path': os.path.join(output_folder_path, f"{self._season_string}_scoring_period{id}.json")}
                                for id in range(scoring_period_id_start, scoring_period_id_end + 1)]
        # Download
        print(f"Downloading to: {output_folder_path}")
        start_time = timeit.default_timer()
        num_saved = self._req.save_jsons_from_endpoints_async(download_dict_list, cookies=self._cookies)
        print(f"Downloaded {num_saved} files in {round(timeit.default_timer() - start_time, 1)}s.")

if __name__ == "__main__":
    """ Main function. """
    start_time = timeit.default_timer()

    # Read arguments
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--league_id", "-l", required=True, type=int, help="League ID.")
    arg_parse.add_argument("--start_year", "-s", required=True, type=int, help="Starting season of data to download.")
    arg_parse.add_argument("--end_year", "-e", required=True, type=int, help="End season of data to download.")
    arg_parse.add_argument("--output_path", "-o", required=False, default=DEFAULT_DOWNLOADS_DIR,
                                                  type=str, help="Output path of where downloaded data will go. Defaults to a folder within script directory.")
    arg_parse.add_argument("--espn_s2", required=False, type=str, help="espn_s2 string used for a cookie for ESPN fantasy API requests.")
    args = arg_parse.parse_args()

    league_id = args.league_id
    start_year = args.start_year
    end_year = args.end_year
    output_path = args.output_path
    espn_s2 = args.espn_s2

    # Download various data for all given seasons
    for season in range(start_year, end_year + 1):
        espn_api = EspnFantasyApiDownloader(season, league_id, root_output_folder=output_path, cookies={'espn_s2': espn_s2})
        espn_api.download_league_info()
        #espn_api.download_scoring_period(144)
        espn_api.download_scoring_periods()

    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")