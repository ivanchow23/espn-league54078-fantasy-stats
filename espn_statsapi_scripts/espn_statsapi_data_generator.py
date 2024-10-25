#!/usr/bin/env python
""" ESPN-statsapi data generator script.
    Takes in an ESPN and statsapi root folder as sources and generates
    various relevant data outputs for downstream consumption and analysis.
"""
import argparse
import os
import pandas as pd

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
from espn_html_parser_loader import EspnHtmlParserLoader
from statsapi_loader import StatsapiLoader

class DraftDataGenerator():
    """ Generate draft related data. """
    def __init__(self, espn_html_parser_loader, statsapi_loader, out_dir):
        self._espn_html_parser_loader = espn_html_parser_loader
        self._statsapi_loader = statsapi_loader
        self._out_dir = out_dir

    def generate(self):
        """ Output dataframe to file. """
        self._load_draft_df().to_csv(os.path.join(self._out_dir, "draft_df.csv"), index=False)

    def _load_draft_df(self):
        """ Loads and prepares all relevant data into a dataframe. """
        # Initialize
        combined_df = pd.DataFrame()

        # Load draft information for all seasons and combine
        for season_string in self._espn_html_parser_loader.get_seasons():
            draft_df = self._espn_html_parser_loader.load_draft_recap_data(season_string)
            if draft_df is None:
                continue

            # Append season information and combine to master dataframe
            draft_df['Season'] = season_string
            combined_df = pd.concat([combined_df, draft_df], ignore_index=True)

        # Append additional "metadata" to the dataframe
        combined_df['Player Birth Country'] = combined_df['Player'].apply(
            lambda player: self._get_player_info(self._statsapi_loader.load_player_dict(player), 'birthCountry'))
        combined_df['Player Age'] = combined_df.apply(
            lambda x: self._get_player_age(self._statsapi_loader.load_player_dict(x['Player']), x['Season']), axis=1)
        combined_df['Player Weight (lbs)'] = combined_df['Player'].apply(
            lambda player: self._get_player_info(self._statsapi_loader.load_player_dict(player), 'weight'))
        combined_df['Player Height (cm)'] = combined_df['Player'].apply(
            lambda player: self._get_player_height_cm(self._statsapi_loader.load_player_dict(player)))

        # Append season stats to the dataframe
        # Load player season stats data for all entries for all seasons
        combined_df['GP'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'games'), axis=1)
        combined_df['G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'goals'), axis=1)
        combined_df['A'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'assists'), axis=1)
        combined_df['PTS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'points'), axis=1)
        combined_df['+/-'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'plusMinus'), axis=1)
        combined_df['PIM'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'pim'), axis=1)
        combined_df['HITS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'hits'), axis=1)
        combined_df['S'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shots'), axis=1)
        combined_df['S%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shotPct'), axis=1)
        combined_df['PPG'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlayGoals'), axis=1)
        combined_df['PPP'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlayPoints'), axis=1)
        combined_df['GWG'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'gameWinningGoals'), axis=1)
        combined_df['OTG'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'overTimeGoals'), axis=1)
        combined_df['SHG'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedGoals'), axis=1)
        combined_df['SHP'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedPoints'), axis=1)
        combined_df['FO%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'faceOffPct'), axis=1)
        combined_df['BKS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'blocked'), axis=1)
        combined_df['SHFT'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shifts'), axis=1)
        combined_df['TOI'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'timeOnIce'), axis=1)
        combined_df['PPTOI'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlayTimeOnIce'), axis=1)
        combined_df['ETOI'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'evenTimeOnIce'), axis=1)
        combined_df['SHTOI'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedTimeOnIce'), axis=1)
        combined_df['TOI/G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'timeOnIcePerGame'), axis=1)
        combined_df['ETOI/G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'evenTimeOnIcePerGame'), axis=1)
        combined_df['SHTOI/G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedTimeOnIcePerGame'), axis=1)
        combined_df['PPTOI/G'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlayTimeOnIcePerGame'), axis=1)

        combined_df['GS'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'gamesStarted'), axis=1)
        combined_df['W'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'wins'), axis=1)
        combined_df['L'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'losses'), axis=1)
        combined_df['OT'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'ot'), axis=1)
        combined_df['T'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'ties'), axis=1)
        combined_df['SO'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shutouts'), axis=1)
        combined_df['SV%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'SavePercentage'), axis=1)
        combined_df['GAA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'goalAgainstAverage'), axis=1)
        combined_df['SV'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'saves'), axis=1)
        combined_df['SA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shotsAgainst'), axis=1)
        combined_df['GA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'goalsAgainst'), axis=1)
        combined_df['PPSV'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlaySaves'), axis=1)
        combined_df['SHSV'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedSaves'), axis=1)
        combined_df['ESV'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'evenSaves'), axis=1)
        combined_df['PPSA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlayShots'), axis=1)
        combined_df['SHSA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedShots'), axis=1)
        combined_df['ESA'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'evenShots'), axis=1)
        combined_df['PPSV%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'powerPlaySavePercentage'), axis=1)
        combined_df['SHSV%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'shortHandedSavePercentage'), axis=1)
        combined_df['ESV%'] = combined_df.apply(
            lambda x: self._get_player_season_stat(
                self._statsapi_loader.load_player_season_stats_dict(x['Player'], x['Season']), 'evenStrengthSavePercentage'), axis=1)

        return combined_df

    def _get_player_info(self, player_dict, key):
        """ Takes in a dictionary from statsapi loaded JSON file and looks
            for data in the given key under the "people" key. This is where
            most of a player's information exists. """
        if player_dict is None:
            return None

        try:
            return player_dict['people'][0][key]
        except KeyError:
            return None

    def _get_player_age(self, player_dict, season_string):
        """ Takes in a dictionary from statsapi loaded JSON file and
            calculates the player's rough age at the current time of the
            given season. Does this by simply taking the difference between
            player's birth year and the start of the season.

            Example: Birth year = 1995-07-23, Season = 20202021
                    Age = 2020 - 1995 = 25
        """
        # String from data dict expected to be in the form "YYYY-MM-DD"
        # Parse for YYYY
        birth_date_string = self._get_player_info(player_dict, 'birthDate')
        if birth_date_string is None:
            return None
        birth_year = int(birth_date_string[0:4])

        # Season string expected to be in the form: "XXXXYYYY"
        # Parse for start of season XXXX
        season = int(season_string[0:4])
        return season - birth_year

    def _get_player_height_cm(self, player_dict):
        """ Takes in a dictionary from statsapi loaded JSON file and converts
            the string of a player's height from feet and inches into an
            integer in units cm. The height string is directly the value that
            comes from the player's height in the JSON file. Note: This
            method's string parsing logic is meant to be super simple.

            Example: '6\' 3"' = 190.5 cm """
        # Height string is expected to be in the form like: '6\' 3"'
        height_string = self._get_player_info(player_dict, 'height')

        # Very basic way to parse for the values
        # First, split the string into sections
        str_list = height_string.split()

        # Next, assume 1st element in list is feet, 2nd element is inches
        # Remove corresponding ' and " charaters
        str_list[0] = str_list[0].replace("\'", "")
        str_list[1] = str_list[1].replace("\"", "")

        # Convert height to inches
        height_in = (int(str_list[0]) * 12) + int(str_list[1])

        # Finally, convert to cm
        return round(height_in * 2.54, 1)

    def _get_player_season_stat(self, player_season_stats_dict, key):
        """ Returns the value given a dictionary of the player's season stats
            and the key corresponding to the stat. Note: Error handling is
            extremely basic. Meant simple usage to get basic stat keys. Does
            not differentiate between skaters and goalies (can technically
            try accessing goalie wins stats on a skater). """
        if player_season_stats_dict is None:
            return None

        try:
            return player_season_stats_dict['stats'][0]['splits'][0]['stat'][key]
        except KeyError:
            return None
        except IndexError:
            return None

class StandingsDataGenerator():
    """ Generate season standings related data. """
    def __init__(self, espn_html_parser_loader, out_dir):
        self._espn_html_parser_loader = espn_html_parser_loader
        self._out_dir = out_dir

        self._standings_dict = self._load_standings_dict()
        self._standings_points_df = self._load_standings_points_df()
        self._standings_stats_df = self._load_standings_stats_df()

    def generate(self):
        """ Output dataframe to file. """
        # Output raw dataframes
        self._standings_points_df.to_csv(os.path.join(self._out_dir, "standings_points_df.csv"), index=False)
        self._standings_stats_df.to_csv(os.path.join(self._out_dir, "standings_stats_df.csv"), index=False)

    def _load_standings_dict(self):
        """ Loads and prepares all relevant data into dictionary of
            dataframes. Each season's league standings data are in a
            slightly different format, so organize based on seasons.

            Example return:
            { '20182019': {'season_points': df, 'season_stats': df},
              '20192020': {'season_points': df, 'season_stats': df},
              '20202021': {'season_points': df, 'season_stats': df}
            }

            This is to load all the data as close to the rawest form
            as possible without losing specific columns from certain
            seasons. Another method may be required to filter and
            combine only the necessary data as needed.
        """
        # Initialize
        standings_dict = {}

        # Load standings information and combine into respective dataframes
        for season_string in self._espn_html_parser_loader.get_seasons():
            standings_dict[season_string] = {}

            league_standings_dict = self._espn_html_parser_loader.load_league_standings_data(season_string)
            if league_standings_dict is None or len(league_standings_dict) == 0:
                continue

            standings_dict[season_string]['season_points'] = league_standings_dict['season_points']
            standings_dict[season_string]['season_stats'] = league_standings_dict['season_stats']

        return standings_dict

    def _load_standings_points_df(self):
        """ Load season standings points as a dataframe. Combines all
            seasons into a single dataframe. Assumes standings
            dictionary is already loaded to operate on. """
        combined_df = pd.DataFrame()
        for season_string in self._standings_dict.keys():
            if self._standings_dict[season_string] == {}:
                continue

            # Dataframes are multi-index columns
            # Drop the top level before combining
            df = self._standings_dict[season_string]['season_points']
            df.columns = df.columns.droplevel(0)

            # Insert column of season information
            df.insert(0, 'Season', season_string)

            # Combine dataframe
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        return combined_df

    def _load_standings_stats_df(self):
        """ Load season standings stats as a dataframe. Combines all
            seasons into a single dataframe. Assumes standings
            dictionary is already loaded to operate on. """
        combined_df = pd.DataFrame()
        for season_string in self._standings_dict.keys():
            if self._standings_dict[season_string] == {}:
                continue

            # Dataframes are multi-index columns
            # Drop the top level before combining
            df = self._standings_dict[season_string]['season_stats']
            df.columns = df.columns.droplevel(0)

            # Insert column of season information
            df.insert(0, 'Season', season_string)

            # Combine dataframe
            combined_df = pd.concat([combined_df, df], ignore_index=True)

        return combined_df

if __name__ == "__main__":
    """ Main runner script. """
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--espn", required=True, help="Root path of parsed ESPN data from ESPN scripts.")
    arg_parser.add_argument("--statsapi", required=True, help="Root path of statsapi data cache from statsapi downloader.")
    arg_parser.add_argument("--outdir", required=True, help="Path to folder where output data will go.")
    args = arg_parser.parse_args()
    espn_html_parser_loader = EspnHtmlParserLoader(args.espn)
    statsapi_loader = StatsapiLoader(args.statsapi)

    DraftDataGenerator(espn_html_parser_loader, statsapi_loader, args.outdir).generate()
    StandingsDataGenerator(espn_html_parser_loader, args.outdir).generate()
