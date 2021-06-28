#!/usr/bin/env python
import json
import os
import statsapi_utils
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestStatsApiUtils(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        pass

    def test_load_json_from_url(self):
        """ Test functionality to load stats API data to JSON given a URL. """
        # Load expected data from known file to begin
        with open(os.path.join(SCRIPT_DIR, "test_files", "8447492.json")) as f:
            expected_data = json.load(f)

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

    def _rm_file(self, file):
        """ Helper function to remove a file. Does nothing if it doesn't exist. """
        try:
            os.remove(file)
        except:
            pass

    def tearDown(self):
        """ Remove any items. """
        pass