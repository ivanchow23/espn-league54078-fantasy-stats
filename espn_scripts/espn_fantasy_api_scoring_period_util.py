#!/usr/bin/env python

""" Utility file to help with converting scoring periods to date by using ESPN API. """
from datetime import date, timedelta
import time
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "utils"))
from requests_util import RequestsUtil

class EspnFantasyApiScoringPeriodUtil:
    def __init__(self):
        self._req = RequestsUtil(f"https://site.web.api.espn.com/apis/site/v2/sports/hockey/nhl/scoreboard?")
        self._first_scoring_period_date = None


    def get_scoring_period_date(self, season_string, scoring_period):
        """ Convert scoring period number to an associated date in this date format: YYYY-MM-DD"""
        # First regular season game will be in the first year of the seasons
        year = str(season_string[:4])
        if self._first_scoring_period_date is None:
            self._first_scoring_period_date = self.__get_first_regular_season_game_date(year)

        # Math to convert the scoring period to date (Complicated due to converting date as a string to a time_struct/date objects)
        # Add number of days (Scoring Period Number - 1) to the date of the scoring period 1
        time_tuple = time.strptime(self._first_scoring_period_date,'%Y%m%d')
        scoring_period_date = date(time_tuple.tm_year, time_tuple.tm_mon, time_tuple.tm_mday) + timedelta(scoring_period - 1)
        date_string = scoring_period_date.strftime('%Y-%m-%d')
        return date_string

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