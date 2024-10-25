#!/usr/bin/env python
import csv
import json
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_fantasy_api_scripts"))
from espn_fantasy_api_loader import EspnFantasyApiLoader

class TestEspnFantasyApiLoader(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_fantasy_api_loader")
        os.makedirs(self._test_folder, exist_ok=True)

    def test__load_json(self):
        """ Test JSON data loading functionality. """
        # Generate test structure
        root_folder_path = os.path.join(self._test_folder, "test__load_json")
        os.makedirs(root_folder_path, exist_ok=True)
        os.makedirs(os.path.join(root_folder_path, "20192020"), exist_ok=True)
        os.makedirs(os.path.join(root_folder_path, "20192020", "scoring_periods"), exist_ok=True)
        self._create_empty_json(os.path.join(root_folder_path, "20192020", "20192020_league_info.json"))
        self._create_empty_json(os.path.join(root_folder_path, "20192020", "scoring_periods", "20192020_scoring_period1.json"))
        self._create_empty_json(os.path.join(root_folder_path, "20192020", "20192020_all_players_info.json"))

        # Instantiate
        espn_api = EspnFantasyApiLoader(root_folder_path)

        # Test typical cases
        self.assertIsNotNone(espn_api._load_json("20192020", "20192020_league_info.json"))
        self.assertIsNotNone(espn_api._load_json("20192020", "scoring_periods", "20192020_scoring_period1.json"))
        self.assertIsNotNone(espn_api._load_json("20192020", "20192020_all_players_info.json"))

        # Test non-existent folders and files
        self.assertIsNone(espn_api._load_json("20192020", "2019_league_info.json"))
        self.assertIsNone(espn_api._load_json("2019", "2020_league_info.json"))
        self.assertIsNone(espn_api._load_json("2019", "2020_all_players_info.json"))

    def _create_empty_json(self, file_path):
        """ Helper function to create an empty JSON file. """
        with open(file_path, 'w') as f:
            f.write("{}")

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)