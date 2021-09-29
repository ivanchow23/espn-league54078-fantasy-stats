#!/usr/bin/env python
import json
import os
import requests
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
import statsapi_utils

class TestStatsApiUtils(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        pass

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
        # Test typical case
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertTrue(os.path.exists(out_path))
        self._rm_file(out_path)

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/ap/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://statsapi.web.nhl.com/api/v1/teams/invalid"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "htts://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = "https://www.google.com"
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = 12345
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = ""
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid URL
        url = None
        out_path = os.path.join(SCRIPT_DIR, "out.json")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.jsn")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.csv")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = os.path.join(SCRIPT_DIR, "out.jsonn")
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(out_path))

        # Test invalid output file
        url = "https://statsapi.web.nhl.com/api/v1/teams"
        out_path = None
        statsapi_utils.save_json_from_url(url, out_path)
        self.assertFalse(os.path.exists(os.path.join(SCRIPT_DIR, "out.json")))

    def test_get_full_url(self):
        """ Test functionality of getting the full statsapi URL link. """
        # Test typical case
        suffix = "/api/v1/teams"
        expected_result = statsapi_utils.URL_STRING + suffix
        actual_result = statsapi_utils.get_full_url(suffix)
        self.assertEqual(expected_result, actual_result)

    def _rm_file(self, file):
        """ Helper function to remove a file. Does nothing if it doesn't exist. """
        try:
            os.remove(file)
        except:
            pass

    def tearDown(self):
        """ Remove any items. """
        pass