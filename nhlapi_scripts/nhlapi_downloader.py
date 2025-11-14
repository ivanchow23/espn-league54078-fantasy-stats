#!/usr/bin/env python
""" Contains functionality to download data from nhlapi to local machine.
    Downloaded data has folder structure:

    nhlapi_data_root_folder
    - teams.json
    - 20192020
      - team_rosters
        -> 20192020_team_roster_<team1>.json
        -> 20192020_team_roster_<team2>.json
      - etc.

    - 20202021
      - team_rosters
        -> 20202021_team_roster_<team1>.json
        -> 20202021_team_roster_<team2>.json
      - etc.
"""
import argparse
import json
import os
import timeit
from utils.requests_util import RequestsUtil

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class NhlapiDownloader():
    def __init__(self, root_output_folder=os.path.join(SCRIPT_DIR, "nhlapi_downloads"), overwrite=True):
        """ Constructor. """
        self._root_output_folder = root_output_folder
        self._overwrite = overwrite

        # Create root output folder where downloaded data be output
        os.makedirs(self._root_output_folder, exist_ok=True)

    @property
    def overwrite(self):
        """ Overwrite property and getter. """
        return self._overwrite

    @overwrite.setter
    def overwrite(self, overwrite):
        """ Overwrite setter. """
        self._overwrite = overwrite

    def download_teams_data(self):
        """ Download all teams data. This provides us with each team's ID,
            letter codes, etc. """
        req = RequestsUtil("https://api.nhle.com/")
        output_file_path = os.path.join(self._root_output_folder, "teams.json")
        req.save_json_from_endpoint("stats/rest/en/team", output_file_path)

    def download_team_rosters_data(self, season_string):
        """ Download all team rosters data for the given season. Downloaded
            files have the form: "XXXXYYYY_team_roster_<team_abbrev>.json",
            where XXXXYYYY is the season.

            Note: Depends on the teams information to be present. Ensure
            download_teams_data() is called first. """
        # Output folder
        req = RequestsUtil("https://api-web.nhle.com/")
        output_folder_path = os.path.join(self._root_output_folder, season_string, "team_rosters")
        os.makedirs(output_folder_path, exist_ok=True)

        # Read teams data to get abbreviations
        teams_data = json.load(open(os.path.join(self._root_output_folder, "teams.json"), 'r'))
        team_abbrev_list = [d['triCode'] for d in teams_data['data']]

        # Prepare links and output paths for download
        # Example link: https://api-web.nhle.com/v1/roster/DAL/20222023
        download_dict_list = [{'endpoint': f"v1/roster/{abbrev}/{season_string}",
                               'out_file_path': os.path.join(output_folder_path, f"{season_string}_team_roster_{abbrev}.json")}
                               for abbrev in team_abbrev_list]

        # Download
        req.save_jsons_from_endpoints_async(download_dict_list)

if __name__ == "__main__":
    """ Main function. """
    total_start_timer = timeit.default_timer()

    # Read arguments
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--start_year", "-s", required=True, type=int, help="Starting season of data to download (Example: 2015 will download 20152016).")
    arg_parse.add_argument("--end_year", "-e", required=True, type=int, help="End season of data to download (Example: 2025 will download 20252026).")
    args = arg_parse.parse_args()

    # Instantiate
    start_timer = timeit.default_timer()
    nhlapi_downloader = NhlapiDownloader()
    print(f"Downloaded teams data in {round(timeit.default_timer() - start_timer, 1)}s.")

    # Download most up-to-date teams data
    nhlapi_downloader.download_teams_data()

    # Download relevant data for each season
    for season in range(args.start_year, args.end_year + 1):
        # Example: The 2020 season will be "20202021"
        season_string = f"{season}{season + 1}"

        start_timer = timeit.default_timer()
        nhlapi_downloader.download_team_rosters_data(season_string)
        print(f"Downloaded team rosters data for {season_string} in {round(timeit.default_timer() - start_timer, 1)}s.")

    print(f"Finished in {round(timeit.default_timer() - total_start_timer, 1)}s.")