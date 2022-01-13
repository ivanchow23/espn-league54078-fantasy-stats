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
        self._req = RequestsUtil("https://statsapi.web.nhl.com/api/v1/")

    def test_load_json_from_endpoint(self):
        """ Test loading a JSON from an endpoint. """
        # Directly request data from server as expected data
        response = requests.get("https://statsapi.web.nhl.com/api/v1/people/8477492")
        expected_data = response.json()

        # Test typical case
        actual_data = self._req.load_json_from_endpoint("people/8477492")
        self.assertEqual(expected_data, actual_data)

        # Test invalid endpoint
        self.assertIsNone(self._req.load_json_from_endpoint("peopl/8477492"))

    def test_save_json_from_endpoint(self):
        """ Test saving a JSON from an endpoint. """
        # Create test folder
        test_folder_path = os.path.join(self._test_folder_path, "test_save_json_from_endpoint")
        os.makedirs(test_folder_path, exist_ok=True)

        # Directly request data from server as expected data
        response = requests.get("https://statsapi.web.nhl.com/api/v1/people/8477492")
        expected_data = response.json()

        # Test typical case
        out_file_path = os.path.join(test_folder_path, "8477492.json")
        self.assertTrue(self._req.save_json_from_endpoint("people/8477492", out_file_path))
        self.assertEqual(expected_data, json.load(open(out_file_path, 'r')))

        # Test invalid endpoint
        out_file_path = os.path.join(test_folder_path, "Invalid.json")
        self.assertFalse(self._req.save_json_from_endpoint("???/8477492", out_file_path))
        self.assertFalse(os.path.exists(out_file_path))

    def load_jsons_from_endpoints_async(self):
        """ Test loading JSONs from endpoints asynchronously. """
        # Test typical input
        # Check for each returned dictionary, check the ID
        endpoint_list = [f"teams/{team_id}" for team_id in range(1, 6)]
        actual_data = self._req.load_jsons_from_endpoints_async(endpoint_list)
        for i, json_data in enumerate(actual_data):
            self.assertEqual(json_data['teams'][0]['id'], i + 1)

        # Test typical input
        # Check order of returned dictionaries are preserved using async
        # Retry multiple times to test repeatability
        num_tries = 3
        endpoint_list = ["teams/1", "teams/20", "teams/12", "teams/55", "teams/2"]
        for i in range(0, num_tries):
            actual_data = self._req.load_jsons_from_endpoints_async(endpoint_list)
            self.assertEqual(actual_data[0]['teams'][0]['id'], 1)
            self.assertEqual(actual_data[1]['teams'][0]['id'], 20)
            self.assertEqual(actual_data[2]['teams'][0]['id'], 12)
            self.assertEqual(actual_data[3]['teams'][0]['id'], 55)
            self.assertEqual(actual_data[4]['teams'][0]['id'], 2)

        # Test invalid inputs
        endpoint_list = ["v???/teams/0",
                         "teams/20",
                         "invalid?"]
        actual_data = self._req.load_jsons_from_endpoints_async(endpoint_list)
        self.assertEqual(actual_data[0], {})
        self.assertEqual(actual_data[1]['teams'][0]['id'], 20)
        self.assertEqual(actual_data[2], {})

    def test_save_jsons_from_endpoints_async(self):
        """ Test saving JSONs from endpoints asynchronously. """
        # Create test folder
        test_folder_path = os.path.join(self._test_folder_path, "test_save_jsons_from_endpoints_async")
        os.makedirs(test_folder_path, exist_ok=True)

        # Test typical input
        # Check for saved files and their corresponding IDs in file
        input_dicts = [{'endpoint': "teams/1", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'endpoint': "teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")},
                       {'endpoint': "teams/3", 'out_file_path': os.path.join(test_folder_path, "team3.json")}]

        num_saved = self._req.save_jsons_from_endpoints_async(input_dicts)
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team1.json"), 'r'))['teams'][0]['id'], 1)
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team2.json"), 'r'))['teams'][0]['id'], 2)
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team3.json"), 'r'))['teams'][0]['id'], 3)
        self.assertEqual(num_saved, 3)

        # Test typical input
        # Check order of data is preserved using async
        # Retry multiple times to test repeatability
        num_tries = 3
        input_dicts = [{'endpoint': "teams/3", 'out_file_path': os.path.join(test_folder_path, "team3.json")},
                       {'endpoint': "teams/1", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'endpoint': "teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")}]

        for i in range(0, num_tries):
            num_saved = self._req.save_jsons_from_endpoints_async(input_dicts)
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "team1.json"), 'r'))['teams'][0]['id'], 1)
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "team2.json"), 'r'))['teams'][0]['id'], 2)
            self.assertEqual(json.load(open(os.path.join(test_folder_path, "team3.json"), 'r'))['teams'][0]['id'], 3)
            self.assertEqual(num_saved, 3)

        # Test invalid input
        input_dicts = [{'endpoint': "v???/teams/0", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'endpoint': "teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")},
                       {'endpoint': "invalid?", 'out_file_path': os.path.join(test_folder_path, "team3.json")}]

        num_saved = self._req.save_jsons_from_endpoints_async(input_dicts)
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team1.json"), 'r')), {})
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team2.json"), 'r'))['teams'][0]['id'], 2)
        self.assertEqual(json.load(open(os.path.join(test_folder_path, "team3.json"), 'r')), {})
        self.assertEqual(num_saved, 3)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder_path)