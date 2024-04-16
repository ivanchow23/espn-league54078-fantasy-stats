#!/usr/bin/env python

""" Contains functionality to download the and store the initial data period dates from ESPN fantasy API
    to local machines. Downloaded data will be organized into season folders. """
from datetime import date, timedelta
import time
import sys
import os
import toml

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, "espn_fantasy_api_downloads")
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "utils"))
from requests_util import RequestsUtil

class EspnFantasyApiScoringPeriodDateDownloader:
    def __init__(self, season, root_output_folder=DEFAULT_DOWNLOADS_DIR):
        self._req = RequestsUtil(f"https://site.web.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?")
        self._first_scoring_period_date = None

        # Store in a season string folder "XXXXYYYY"
        # Example: 2022 season corresponds to: "20212022"
        self._season_string = f"{season - 1}{season}"
        self._root_output_folder = os.path.join(root_output_folder, self._season_string)
        os.makedirs(self._root_output_folder, exist_ok=True)
        self._season = season

    def store_season_metadata(self):
        date_string = self.__get_first_regular_season_game_date(self._season - 1)
        data = {
            self._season_string: date_string
        }
        output_folder_path = os.path.join(self._root_output_folder, "metadata.toml")
        with open(output_folder_path, 'w') as file:
            toml.dump(data, file)


    def __get_first_regular_season_game_date(self, year):
        """ Convert the first scoring period number to an associated date in this date format: YYYYMMDD"""
        date_string = f"{year}1001"
        game_schedule_dict = self._req.load_json_from_endpoint(f"dates={date_string}")

        while((not self.__is_regular_season(game_schedule_dict))):
            time_tuple = time.strptime(date_string,'%Y%m%d')
            scoring_period_date= date(time_tuple.tm_year, time_tuple.tm_mon, time_tuple.tm_mday) + timedelta(1)
            date_string = scoring_period_date.strftime('%Y%m%d')
            game_schedule_dict = self._req.load_json_from_endpoint(f"dates={date_string}")
        return date_string

    def __is_regular_season(self, game_schedule_dict):
        if len(game_schedule_dict['events']) == 0:
            return False
        game = game_schedule_dict['events'][0]
        return game['season']['slug'] == 'regular-season'