#!/usr/bin/env python
import json
import os
import requests
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "utils"))
from requests_util import RequestsUtil

class TestRequestsUtil(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder_path = os.path.join(SCRIPT_DIR, "test_requests_util")
        os.makedirs(self._test_folder_path, exist_ok=True)

        # Instantiate class to a known API
        self._req = RequestsUtil("https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/2023/segments/0/leagues/54078?")

    def test_load_json_from_endpoint(self):
        """ Test loading a JSON from an endpoint. """
        # Directly request data from server as expected data
        response = requests.get("https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/2023/segments/0/leagues/54078?view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam")
        expected_data = response.json()

        # Test typical case
        actual_data = self._req.load_json_from_endpoint("view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam")
        self.assertEqual(expected_data, actual_data)

    def test_save_json_from_endpoint(self):
        """ Test saving a JSON from an endpoint. """
        # Create test folder
        test_folder_path = os.path.join(self._test_folder_path, "test_save_json_from_endpoint")
        os.makedirs(test_folder_path, exist_ok=True)

        # Directly request data from server as expected data
        response = requests.get("https://lm-api-reads.fantasy.espn.com/apis/v3/games/fhl/seasons/2023/segments/0/leagues/54078?view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam")
        expected_data = response.json()

        # Test typical case
        out_file_path = os.path.join(test_folder_path, "test_typical.json")
        self.assertTrue(self._req.save_json_from_endpoint("view=mLiveScoring&view=mMatchupScore&view=mRoster&view=mSettings&view=mStandings&view=mStatus&view=mTeam", out_file_path))
        self.assertEqual(expected_data, json.load(open(out_file_path, 'r')))

    def test_load_jsons_from_endpoints_async(self):
        """ Test loading JSONs from endpoints asynchronously. """
        # Test typical input
        # Check for each returned dictionary, check the ID
        endpoint_list = ["scoringPeriodId=0&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                         "scoringPeriodId=1&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                         "scoringPeriodId=2&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav"]
        actual_data = self._req.load_jsons_from_endpoints_async(endpoint_list)
        for i, json_data in enumerate(actual_data):
            self.assertEqual(json_data['scoringPeriodId'], i)

        # Test typical input
        # Check order of returned dictionaries are preserved using async
        # Retry multiple times to test repeatability
        num_tries = 3
        endpoint_list = ["scoringPeriodId=3&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                         "scoringPeriodId=2&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav",
                         "scoringPeriodId=5&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav"]
        for i in range(0, num_tries):
            actual_data = self._req.load_jsons_from_endpoints_async(endpoint_list)
            self.assertEqual(actual_data[0]['scoringPeriodId'], 3)
            self.assertEqual(actual_data[1]['scoringPeriodId'], 2)
            self.assertEqual(actual_data[2]['scoringPeriodId'], 5)

    def test_save_jsons_from_endpoints_async(self):
        """ Test saving JSONs from endpoints asynchronously. """
        # Create test folder
        test_folder_path = os.path.join(self._test_folder_path, "test_save_jsons_from_endpoints_async")
        os.makedirs(test_folder_path, exist_ok=True)

        # Test typical input
        # Check for saved files and their corresponding IDs in file
        input_dicts = [{'endpoint': "scoringPeriodId=0&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "0.json")},
                       {'endpoint': "scoringPeriodId=1&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "1.json")},
                       {'endpoint': "scoringPeriodId=2&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "2.json")}]

        num_saved = self._req.save_jsons_from_endpoints_async(input_dicts)
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "0.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "1.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "2.json")))
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "0.json"), 'r'))['scoringPeriodId'], 0)
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "1.json"), 'r'))['scoringPeriodId'], 1)
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "2.json"), 'r'))['scoringPeriodId'], 2)
        self.assertEqual(num_saved, 3)

        # Test typical input
        # Check order of data is preserved using async
        # Retry multiple times to test repeatability
        num_tries = 3
        input_dicts = [{'endpoint': "scoringPeriodId=3&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "3.json")},
                       {'endpoint': "scoringPeriodId=2&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "2.json")},
                       {'endpoint': "scoringPeriodId=5&view=mRoster&view=mScoreboard&view=mSettings&view=mStatus&view=modular&view=mNav", 'out_file_path': os.path.join(test_folder_path, "5.json")}]

        for i in range(0, num_tries):
            num_saved = self._req.save_jsons_from_endpoints_async(input_dicts)
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "3.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "2.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "5.json")))
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "3.json"), 'r'))['scoringPeriodId'], 3)
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "2.json"), 'r'))['scoringPeriodId'], 2)
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "5.json"), 'r'))['scoringPeriodId'], 5)
            self.assertEqual(num_saved, 3)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder_path)