from espn_html_parser_clubhouse import EspnHtmlParserClubhouse
import os
import pandas as pd
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnHtmlParserClubhouse(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_clubhouse")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_EspnHtmlParserClubhouse(self):
        """ Test constructor. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_EspnHtmlParserClubhouse")
        os.makedirs(test_folder, exist_ok=True)
        test_file_path = os.path.join(test_folder, "test.html")
        open(test_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserClubhouse(test_file_path)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserClubhouse(os.path.join(self._test_folder, "does_not_exist.html"))
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserClubhouse("Not a file.")
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserClubhouse(123)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserClubhouse([1, 2, 3])
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserClubhouse(None)
        self.assertFalse(espn.valid)

    def test_get_rosters_dict(self):
        """ Test getting dictionary of rosters. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_rosters_dict")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserClubhouse(empty_file_path)
        roster_dict = espn.get_rosters_dict()
        self.assertIsNone(roster_dict['skaters_df'])
        self.assertIsNone(roster_dict['goalies_df'])

        # Note: No tests for parsing a representative HTML page yet

    def test_get_team_owners_dict(self):
        """ Test getting dictionary of team owners. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_team_owners_dict")
        os.makedirs(test_folder, exist_ok=True)
        test_file_path = os.path.join(test_folder, "Test Team Name Clubhouse.html")
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(test_file_path, 'w')
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserClubhouse(empty_file_path)
        team_owners_dict = espn.get_team_owners_dict()
        self.assertEqual(team_owners_dict['Team Name'], "")
        self.assertEqual(team_owners_dict['Owner Name'], "")

        # Test empty input
        espn = EspnHtmlParserClubhouse(test_file_path)
        team_owners_dict = espn.get_team_owners_dict()
        self.assertEqual(team_owners_dict['Team Name'], "")
        self.assertEqual(team_owners_dict['Owner Name'], "")

        # Note: No tests for parsing a representative HTML page yet

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)