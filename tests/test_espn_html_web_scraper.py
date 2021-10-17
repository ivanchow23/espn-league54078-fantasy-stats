#!/usr/bin/env python
import os
import pickle
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
from espn_html_web_scraper import EspnHtmlWebScraper

class TestEspnHtmlWebScraper(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_web_scraper")
        os.makedirs(self._test_folder, exist_ok=True)

        # Instantiate an instance for all tests to use
        self._espn = EspnHtmlWebScraper(league_id=54078,
                                        season_id=2022,
                                        num_teams=7,
                                        out_dir=self._test_folder)
        self._espn.init_driver()

    def test__save_html(self):
        """ Test saving HTML from given URL functionality. """
        test_folder = os.path.join(self._test_folder, "test__save_html")
        os.makedirs(test_folder, exist_ok=True)

        # Test typical case
        url = "https://fantasy.espn.com/hockey/league/standings?leagueId=54078"
        html_path = self._espn._save_html(url, test_folder)
        self.assertTrue(os.path.exists(html_path))

        # Test invalid URL causing failed retries and no saved HTML
        url = "invalid_url"
        self._espn.GET_RETRY_NUM_TIMES = 3
        self._espn.GET_RETRY_TIME_SEC = 2
        html_path = self._espn._save_html(url, os.path.join(test_folder, "test_invalid.html"))
        self.assertIsNone(html_path)

    def test__append_dict_to_pickle(self):
        """ Test appending dictionary to a pickle file. """
        test_folder = os.path.join(self._test_folder, "test__append_dict_to_pickle")
        os.makedirs(test_folder, exist_ok=True)

        # Test typical case - no pickle exists
        #   - Check pickle exists
        #   - Check contents are expected
        pickle_path = os.path.join(test_folder, "test.pickle")
        input_dict = {'Key1': 123}
        expected_dict = input_dict
        self._espn._append_dict_to_pickle(input_dict, pickle_path)
        self.assertTrue(os.path.exists(pickle_path))
        self.assertEqual(expected_dict, pickle.load(open(pickle_path, 'rb')))

        # Test typical case - pickle exists (from previous test)
        #   - Check contents are expected
        input_dict = {'Key2': {'Key2.1': 1, 'Key2.2': 2}}
        expected_dict = {'Key1': 123, 'Key2': {'Key2.1': 1, 'Key2.2': 2}}
        self._espn._append_dict_to_pickle(input_dict, pickle_path)
        self.assertEqual(expected_dict, pickle.load(open(pickle_path, 'rb')))

        # Test typical case
        # Multiple keys in dict and pickle exists (from previous test)
        #   - Check contents are expected
        input_dict = {'Key3': {'Key3.1': 10, 'Key3.2': 20}, 'Key4': 456}
        expected_dict = {'Key1': 123,
                         'Key2': {'Key2.1': 1, 'Key2.2': 2},
                         'Key3': {'Key3.1': 10, 'Key3.2': 20},
                         'Key4': 456}
        self._espn._append_dict_to_pickle(input_dict, pickle_path)
        self.assertEqual(expected_dict, pickle.load(open(pickle_path, 'rb')))

        # Test non-dictionary input
        input_data = [1, 2, 3]
        expected_dict = {'Key1': 123,
                         'Key2': {'Key2.1': 1, 'Key2.2': 2},
                         'Key3': {'Key3.1': 10, 'Key3.2': 20},
                         'Key4': 456}
        self._espn._append_dict_to_pickle(input_dict, pickle_path)
        self.assertEqual(expected_dict, pickle.load(open(pickle_path, 'rb')))

        # Test non-dictionary pickle
        pickle_path = os.path.join(test_folder, "not_dict.pickle")
        pickle.dump([1, 2, 3], open(pickle_path, 'wb'))
        input_dict = {'Key1': 123}
        self._espn._append_dict_to_pickle(input_dict, pickle_path)
        self.assertEqual([1, 2, 3], pickle.load(open(pickle_path, 'rb')))

    def tearDown(self):
        """ Remove any items. """
        # Close drivers
        self._espn.close_driver()

        # Clean up log files that could be result of using drivers
        for f in os.listdir(SCRIPT_DIR):
            if f.endswith(".log"):
                os.remove(os.path.join(SCRIPT_DIR, f))

        # Remove testing folder
        shutil.rmtree(self._test_folder)