from espn_html_parser_league_rosters import EspnHtmlParserLeagueRosters
import os
import pandas as pd
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnHtmlParserLeagueRosters(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_league_rosters")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_EspnHtmlParserLeagueRosters(self):
        """ Test constructor. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_EspnHtmlParserLeagueRosters")
        os.makedirs(test_folder, exist_ok=True)
        test_file_path = os.path.join(test_folder, "test.html")
        open(test_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueRosters(test_file_path)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueRosters(os.path.join(self._test_folder, "does_not_exist.html"))
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueRosters("Not a file.")
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueRosters(123)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueRosters([1, 2, 3])
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserLeagueRosters(None)
        self.assertFalse(espn.valid)

    def test_get_rosters_list(self):
        """ Test getting rosters list. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_rosters_list")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueRosters(empty_file_path)
        self.assertTrue(len(espn.get_rosters_list()) == 0)

        # Note: No tests for parsing a representative HTML page yet

    def test_get_standings_df(self):
        """ Test getting standings dataframe. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_standings_df")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserLeagueRosters(empty_file_path)
        self.assertTrue(espn.get_standings_df().empty)

        # Note: No tests for parsing a representative HTML page yet

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)