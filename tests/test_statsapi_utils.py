#!/usr/bin/env python
import json
import os
import requests
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
import statsapi_utils

class TestStatsApiUtils(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder_path = os.path.join(SCRIPT_DIR, "test_statsapi_utils")
        os.makedirs(self._test_folder_path, exist_ok=True)

    def test_load_json_from_url(self):
        """ Test functionality to load stats API data to JSON given a URL. """
        # Directly request data from server as expected data
        response = requests.get("https://statsapi.web.nhl.com/api/v1/people/8477492")
        expected_data = response.json()

        # Test typical case
        url = "https://statsapi.web.nhl.com/api/v1/people/8477492"
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertEqual(expected_data, actual_data)

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/api/v1/peopl/8477492"
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/api/v1/people/invalid"
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

        # Test invalid URL
        url = "https://www.google.com"
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

        # Test invalid URL
        url = 12345
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

        # Test invalid URL
        url = ""
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

        # Test invalid URL
        url = None
        actual_data = statsapi_utils.load_json_from_url(url)
        self.assertNotEqual(expected_data, actual_data)
        self.assertIsNone(actual_data)

    def test_save_json_from_url(self):
        """ Test functionality to download/save stats API data to JSON given a URL. """
        test_folder_path = os.path.join(self._test_folder_path, "test_save_json_from_url")
        os.makedirs(test_folder_path, exist_ok=True)

        # Test typical case
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertTrue(os.path.exists(out_path))
        self._rm_file(out_path)

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/ap/v1/teams"
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/api/v1/teams/invalid"
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "htts://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://www.google.com"
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = 12345
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = ""
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = None
        out_path = os.path.join(test_folder_path, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(test_folder_path, "out.jsn")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(test_folder_path, "out.csv")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(test_folder_path, "out.jsonn")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = None
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(os.path.join(test_folder_path, "out.json")))

    def test_load_jsons_from_urls_async(self):
        """ Test functionality to load JSONs asynchronously. """
        # Test typical input
        # Check for each returned dictionary, check the ID
        url_list = [f"https://statsapi.web.nhl.com/api/v1/teams/{team_id}"
                    for team_id in range(1, 6)]
        actual_data = statsapi_utils.load_jsons_from_urls_async(url_list)
        for i, json_data in enumerate(actual_data):
            self.assertEqual(json_data['teams'][0]['id'], i + 1)

        # Test typical input
        # Check order of returned dictionaries are preserved using async
        # Retry multiple times to test repeatability
        url_list = ["https://statsapi.web.nhl.com/api/v1/teams/1",
                    "https://statsapi.web.nhl.com/api/v1/teams/20",
                    "https://statsapi.web.nhl.com/api/v1/teams/12",
                    "https://statsapi.web.nhl.com/api/v1/teams/55",
                    "https://statsapi.web.nhl.com/api/v1/teams/2"]

        num_tries = 3
        for i in range(0, num_tries):
            actual_data = statsapi_utils.load_jsons_from_urls_async(url_list)
            self.assertEqual(actual_data[0]['teams'][0]['id'], 1)
            self.assertEqual(actual_data[1]['teams'][0]['id'], 20)
            self.assertEqual(actual_data[2]['teams'][0]['id'], 12)
            self.assertEqual(actual_data[3]['teams'][0]['id'], 55)
            self.assertEqual(actual_data[4]['teams'][0]['id'], 2)

        # Test invalid inputs
        url_list = ["https://statsapi.web.nhl.com/api/v???/teams/0",
                    "https://statsapi.web.nhl.com/api/v1/teams/20",
                    "https://?invalid?url?"]
        actual_data = statsapi_utils.load_jsons_from_urls_async(url_list)
        self.assertEqual(actual_data[0], {})
        self.assertEqual(actual_data[1]['teams'][0]['id'], 20)
        self.assertEqual(actual_data[2], {})


    def test_save_jsons_from_urls_async(self):
        """ Test functionality to save JSONs asynchronously. """
        test_folder_path = os.path.join(self._test_folder_path, "test_save_jsons_from_urls_async")
        os.makedirs(test_folder_path, exist_ok=True)

        # Test typical input
        # Check for saved files and their corresponding IDs in file
        input_dicts = [{'url': "https://statsapi.web.nhl.com/api/v1/teams/1", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'url': "https://statsapi.web.nhl.com/api/v1/teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")},
                       {'url': "https://statsapi.web.nhl.com/api/v1/teams/3", 'out_file_path': os.path.join(test_folder_path, "team3.json")}]

        num_saved = statsapi_utils.save_jsons_from_urls_async(input_dicts)
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team1.json"))['teams'][0]['id'], 1)
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team2.json"))['teams'][0]['id'], 2)
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team3.json"))['teams'][0]['id'], 3)
        self.assertEqual(num_saved, 3)

        # Test typical input
        # Check order of data is preserved using async
        # Retry multiple times to test repeatability
        input_dicts = [{'url': "https://statsapi.web.nhl.com/api/v1/teams/3", 'out_file_path': os.path.join(test_folder_path, "team3.json")},
                       {'url': "https://statsapi.web.nhl.com/api/v1/teams/1", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'url': "https://statsapi.web.nhl.com/api/v1/teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")}]
        num_tries = 3
        for i in range(0, num_tries):
            num_saved = statsapi_utils.save_jsons_from_urls_async(input_dicts)
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
            self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
            self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team1.json"))['teams'][0]['id'], 1)
            self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team2.json"))['teams'][0]['id'], 2)
            self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team3.json"))['teams'][0]['id'], 3)
            self.assertEqual(num_saved, 3)

        # Test invalid input
        input_dicts = [{'url': "https://statsapi.web.nhl.com/api/v???/teams", 'out_file_path': os.path.join(test_folder_path, "team1.json")},
                       {'url': "https://statsapi.web.nhl.com/api/v1/teams/2", 'out_file_path': os.path.join(test_folder_path, "team2.json")},
                       {'url': "https://?invalid?url?", 'out_file_path': os.path.join(test_folder_path, "team3.json")}]

        num_saved = statsapi_utils.save_jsons_from_urls_async(input_dicts)
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team2.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "team3.json")))
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team1.json")), {})
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team2.json"))['teams'][0]['id'], 2)
        self.assertEqual(self._load_json_dict(os.path.join(test_folder_path, "team3.json")), {})
        self.assertEqual(num_saved, 3)

    def test_get_full_url(self):
        """ Test functionality of getting the full statsapi URL link. """
        # Test typical case
        suffix = "/api/v1/teams"
        expected_result = statsapi_utils.URL_STRING + suffix
        actual_result = statsapi_utils.get_full_url(suffix)
        self.assertEqual(expected_result, actual_result)

    def _load_json_dict(self, file_path):
        """ Helper function to load JSON dictionary from file. """
        return json.load(open(file_path, 'r'))

    def _rm_file(self, file):
        """ Helper function to remove a file. Does nothing if it doesn't exist. """
        try:
            os.remove(file)
        except:
            pass

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder_path)