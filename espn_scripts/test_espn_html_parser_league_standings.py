from espn_html_parser_league_standings import EspnHtmlParserLeagueStandings
import os
import pandas as pd
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnHtmlParserLeagueStandings(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_league_standings")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_EspnHtmlParserLeagueStandings(self):
        """ Test constructor. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_EspnHtmlParserLeagueStandings")
        os.makedirs(test_folder, exist_ok=True)
        test_file_path = os.path.join(test_folder, "test.html")
        open(test_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueStandings(test_file_path)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueStandings(os.path.join(self._test_folder, "does_not_exist.html"))
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueStandings("Not a file.")
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueStandings(123)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueStandings([1, 2, 3])
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueStandings(None)
        self.assertFalse(espn.valid)

    def test_get_season_standings_points_df(self):
        """ Test getting season standings points dataframe. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_season_standings_points_df")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueStandings(empty_file_path)
        df = espn.get_season_standings_points_df()
        self.assertTrue(df.empty)

        # Note: No tests for parsing a representative HTML page yet

    def test_get_season_standings_stats_df(self):
        """ Test getting season standings raw stats dataframe. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_season_standings_stats_df")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueStandings(empty_file_path)
        df = espn.get_season_standings_stats_df()
        self.assertTrue(df.empty)

        # Note: No tests for parsing a representative HTML page yet

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)