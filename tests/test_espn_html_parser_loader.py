#!/usr/bin/env python
import csv
import os
import pickle
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
import espn_html_parser_loader

class TestEspnHtmlParserLoader(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_loader_folder")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_load_clubhouse_data(self):
        """ Test clubhouse data loading. """
        # Build test folder structure with some data in it
        test_folder_root_path = os.path.join(self._test_folder, "test_load_clubhouse_df")
        self._generate_typical_test_folder_structure(test_folder_root_path, "20202021")

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical case
        expected_data = [1, 2, 3]
        actual_data = espn.load_clubhouses_data("20202021")
        self.assertEqual(expected_data, actual_data)

        # Test invalid inputs
        self.assertIsNone(espn.load_clubhouses_data("12341235"))
        self.assertIsNone(espn.load_clubhouses_data(None))
        self.assertIsNone(espn.load_clubhouses_data(123))

    def test_load_draft_recap_data(self):
        """ Test draft recap data loading. """
        # Build test folder structure with some data in it
        test_folder_root_path = os.path.join(self._test_folder, "test_load_draft_recap_data")
        self._generate_typical_test_folder_structure(test_folder_root_path, "20202021")

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical case
        expected_data = [1, 2, 3]
        actual_data = espn.load_draft_recap_data("20202021")
        self.assertEqual(expected_data, actual_data)

        # Test invalid inputs
        self.assertIsNone(espn.load_draft_recap_data("12341235"))
        self.assertIsNone(espn.load_draft_recap_data(None))
        self.assertIsNone(espn.load_draft_recap_data(123))

    def test_load_league_standings_data(self):
        """ Test league standings data loading. """
        # Build test folder structure with some data in it
        test_folder_root_path = os.path.join(self._test_folder, "test_load_draft_recap_data")
        self._generate_typical_test_folder_structure(test_folder_root_path, "20202021")

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical case
        expected_data = [1, 2, 3]
        actual_data = espn.load_league_standings_data("20202021")
        self.assertEqual(expected_data, actual_data)

        # Test invalid inputs
        self.assertIsNone(espn.load_league_standings_data("12341235"))
        self.assertIsNone(espn.load_league_standings_data(None))
        self.assertIsNone(espn.load_league_standings_data(123))

    def test_get_seasons(self):
        """ Test getting season strings from root folder. """
        # Build test folder structure with empty files
        test_folder_root_path = os.path.join(self._test_folder, "test_get_seasons")
        os.makedirs(os.path.join(test_folder_root_path, "20192020"))
        os.makedirs(os.path.join(test_folder_root_path, "20202021"))
        os.makedirs(os.path.join(test_folder_root_path, "1234512346"))
        os.makedirs(os.path.join(test_folder_root_path, "invalid"))
        open(os.path.join(test_folder_root_path, "20032004"), 'w')
        open(os.path.join(test_folder_root_path, "empty.csv"), 'w')

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical case
        expected_data = ["20192020", "20202021", "1234512346"]
        actual_data = espn.get_seasons()
        self.assertEqual(set(expected_data), set(actual_data))


    def test__check_path(self):
        """ Test helper function. """
        # Build test folder structure with some data in it
        test_folder_root_path = os.path.join(self._test_folder, "test__find_file_path_recursive")
        test_season_folder_path = os.path.join(test_folder_root_path, "20202021")
        test_csv_folder_path = os.path.join(test_season_folder_path, "csv")
        test_pickle_folder_path = os.path.join(test_season_folder_path, "pickles")
        self._generate_typical_test_folder_structure(test_folder_root_path, "20202021")

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical paths that should exist (folders and files)
        self.assertTrue(espn._check_path(self._test_folder))
        self.assertTrue(espn._check_path(os.path.join(test_folder_root_path)))
        self.assertTrue(espn._check_path(os.path.join(test_season_folder_path)))
        self.assertTrue(espn._check_path(os.path.join(test_csv_folder_path, "Test.csv")))
        self.assertTrue(espn._check_path(os.path.join(test_pickle_folder_path, "Test.pickle")))

        # Test invalid paths
        self.assertFalse(espn._check_path(os.path.join(self._test_folder, "NotAFolder")))
        self.assertFalse(espn._check_path(os.path.join(test_season_folder_path, "Test2.pickle")))
        self.assertFalse(espn._check_path("not/a/path"))
        self.assertFalse(espn._check_path(None))
        self.assertFalse(espn._check_path(123))
        self.assertFalse(espn._check_path([1, 2, 3]))

    def test__find_file_path_recursive(self):
        """ Test helper function. """
        # Build test folder structure with some data in it
        test_folder_root_path = os.path.join(self._test_folder, "test__find_file_path_recursive")
        test_season_folder_path = os.path.join(test_folder_root_path, "20202021")
        test_csv_folder_path = os.path.join(test_season_folder_path, "csv")
        test_pickle_folder_path = os.path.join(test_season_folder_path, "pickles")
        self._generate_typical_test_folder_structure(test_folder_root_path, "20202021")

        # Instantiate
        espn = espn_html_parser_loader.EspnHtmlParserLoader(test_folder_root_path)

        # Test typical case
        expected_path = os.path.join(test_pickle_folder_path, "Test.pickle")
        actual_path = espn._find_file_path_recursive("20202021", "Test", ".pickle")
        self.assertEqual(expected_path, actual_path)

        # Test typical case
        expected_path = os.path.join(test_csv_folder_path, "Test.csv")
        actual_path = espn._find_file_path_recursive("20202021", "Test", ".csv")
        self.assertEqual(expected_path, actual_path)

        # Test typical case (shortened search string)
        expected_path = os.path.join(test_pickle_folder_path, "Test.pickle")
        actual_path = espn._find_file_path_recursive("20202021", "T", ".pickle")
        self.assertEqual(expected_path, actual_path)

        # Test typical case (shortened search string)
        expected_path = os.path.join(test_csv_folder_path, "Test.csv")
        actual_path = espn._find_file_path_recursive("20202021", "T", ".csv")
        self.assertEqual(expected_path, actual_path)

        # Test case-sensitive inputs
        self.assertIsNone(espn._find_file_path_recursive("20202021", "test", ".csv"))
        self.assertIsNone(espn._find_file_path_recursive("20202021", "Test", ".cSv"))
        self.assertIsNone(espn._find_file_path_recursive("20202021", "test", ".pickle"))
        self.assertIsNone(espn._find_file_path_recursive("20202021", "Test", ".Pickle"))

        # Test unknown files
        self.assertIsNone(espn._find_file_path_recursive("20202021", "Test", ".docx"))
        self.assertIsNone(espn._find_file_path_recursive("20202021", "Test1", ".csv"))
        self.assertIsNone(espn._find_file_path_recursive("20202021", "DoesNotExist", ".pickle"))

        # Test unknown season folder
        self.assertIsNone(espn._find_file_path_recursive("20192020", "Test", "pickle"))

        # Test invalid inputs
        self.assertIsNone(espn._find_file_path_recursive(None, "Test", "pickle"))
        self.assertIsNone(espn._find_file_path_recursive("20192020", None, "pickle"))
        self.assertIsNone(espn._find_file_path_recursive("20192020", "Test", None))

    def _generate_typical_test_folder_structure(self, root_path, season):
        """ Helper function that generates a typical testing folder structure.
            Folder structure generated:

            root_path
              <season>
                - csv
                  -> Test.csv
                  -> ...
                - pickles
                  -> Test.pickle
                  -> ...
        """
        # Folder paths
        season_folder_path = os.path.join(root_path, season)
        csv_folder_path = os.path.join(season_folder_path, "csv")
        pickle_folder_path = os.path.join(season_folder_path, "pickles")

        # Create folders and files
        os.makedirs(csv_folder_path, exist_ok=True)
        self._create_csv_file(os.path.join(csv_folder_path, "Test.csv"), [{'a': 1, 'b': 10}, {'a': 2, 'b': 20}])

        os.makedirs(pickle_folder_path, exist_ok=True)
        self._create_pickle_file(os.path.join(pickle_folder_path, "Test.pickle"), [1, 2, 3])
        self._create_pickle_file(os.path.join(pickle_folder_path, "Clubhouses.pickle"), [1, 2, 3])
        self._create_pickle_file(os.path.join(pickle_folder_path, "Draft Recap.pickle"), [1, 2, 3])
        self._create_pickle_file(os.path.join(pickle_folder_path, "League Standings.pickle"), [1, 2, 3])

    def _create_csv_file(self, file_path, data_dicts):
        """ Helper function to create a CSV file. """
        with open(file_path, 'w') as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=data_dicts[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_dicts)

    def _create_pickle_file(self, file_path, data):
        """ Helper function to create a pickle file. """
        pickle.dump(data, open(file_path, 'wb'))

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)