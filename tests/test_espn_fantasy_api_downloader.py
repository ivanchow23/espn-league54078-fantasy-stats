#!/usr/bin/env python
from espn_fantasy_api_scripts.espn_fantasy_api_downloader import EspnFantasyApiDownloader
from espn_fantasy_api_scripts.espn_fantasy_api_downloader import EspnApiDownloader
import json
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
TEST_LEAGUE_ID = 54078
TEST_SEASON = 2025

class TestEspnFantasyApiDDownloader(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_fantasy_api_downloader")
        os.makedirs(self._test_folder, exist_ok=True)

        self._api_downloader = EspnApiDownloader(root_output_folder=self._test_folder)
        self._fapi_downloader = EspnFantasyApiDownloader(league_id=TEST_LEAGUE_ID,
                                                    season=TEST_SEASON,
                                                    root_output_folder=self._test_folder)

    def test_download_league_info(self):
        """ Tests downloading league info data. """
        # Download
        self._fapi_downloader.download_league_info()

        # Test file exists
        expected_path = os.path.join(self._test_folder, "20242025", "20242025_league_info.json")
        self.assertTrue(os.path.isfile(expected_path))

        # Test contents in file
        expected_data = self._load_json(expected_path)
        self.assertTrue("members" in expected_data)
        self.assertTrue("status" in expected_data)
        self.assertTrue("teams" in expected_data)

    def test_download_draft_details(self):
        """ Tests downloading draft details data. """
        # Download
        self._fapi_downloader.download_draft_details()

        # Test file exists
        expected_path = os.path.join(self._test_folder, "20242025", "20242025_draft_details.json")
        self.assertTrue(os.path.isfile(expected_path))

        # Test contents in file
        expected_data = self._load_json(expected_path)
        self.assertTrue("draftDetail" in expected_data)
        self.assertTrue("picks" in expected_data['draftDetail'])
        self.assertTrue("playerId" in expected_data['draftDetail']['picks'][0])

    def test_download_scoring_period(self):
        """ Tests downloading a scoring period. """
        # Download
        self._fapi_downloader.download_scoring_period(id=10)

        # Test file exists
        expected_path = os.path.join(self._test_folder, "20242025", "scoring_periods", "20242025_scoring_period10.json")
        self.assertTrue(os.path.isfile(expected_path))

        # Test contents in file
        expected_data = self._load_json(expected_path)
        self.assertTrue("teams" in expected_data)
        self.assertTrue(expected_data['id'], 54078)
        self.assertEqual(expected_data["scoringPeriodId"], 10)

    def test_download_all_players_info(self):
        """ Tests downloading all players info. """
        # Download
        self._fapi_downloader.download_all_players_info()

        # Test file exists
        expected_path = os.path.join(self._test_folder, "20242025", "20242025_all_players_info.json")
        self.assertTrue(os.path.isfile(expected_path))

        # Test contents in file
        expected_data = self._load_json(expected_path)
        self.assertTrue("players" in expected_data)
        self.assertTrue(len(expected_data['players']) > 0)
        self.assertTrue("id" in expected_data['players'][0])

    def test_download_athletes_data(self):
        """ Tests downloading athletes data. """
        # Download
        self._api_downloader.download_athletes_data([3895074])

        # Test file exists
        expected_path = os.path.join(self._test_folder, "athletes", "3895074.json")
        self.assertTrue(os.path.isfile(expected_path))

        # Test contents in file
        expected_data = self._load_json(expected_path)
        self.assertTrue("athlete" in expected_data)
        self.assertTrue("fullName" in expected_data['athlete'])
        self.assertTrue(expected_data['athlete']['id'], 3895074)

    def _load_json(self, file_path):
        """ Helper function to load a JSON file. """
        with open(file_path, 'r') as f:
            return json.load(f)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)