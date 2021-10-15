#!/usr/bin/env python
import csv
import json
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "statsapi_scripts"))
from statsapi_loader import StatsapiLoader

class TestStatsapiLoader(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_statsapi_loader_folder")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_load_player_dict(self):
        """ Test loading player information as a dictionary. """
        test_folder = os.path.join(self._test_folder, "test_load_player_dict")
        self._generate_typical_test_folder_structure(test_folder)
        statsapi = StatsapiLoader(test_folder)

        # Test typical case - player name only
        expected_data = {'Player Name': "Connor McDavid", 'Birth Country': "CAN"}
        actual_data = statsapi.load_player_dict("Connor McDavid")
        self.assertEqual(expected_data, actual_data)

        # Test typical case - player name and team name
        expected_data = {'Player Name': "Connor McDavid", 'Birth Country': "CAN"}
        actual_data = statsapi.load_player_dict("Connor McDavid", team="EDM")
        self.assertEqual(expected_data, actual_data)

        # Test typical case - player name and season
        expected_data = {'Player Name': "Connor McDavid", 'Birth Country': "CAN"}
        actual_data = statsapi.load_player_dict("Connor McDavid", season_string="20202021")
        self.assertEqual(expected_data, actual_data)

        # Test typical case - player name, team, and season
        expected_data = {'Player Name': "Connor McDavid", 'Birth Country': "CAN"}
        actual_data = statsapi.load_player_dict("Connor McDavid", team="EDM", season_string="20202021")
        self.assertEqual(expected_data, actual_data)

        # Test typical case - with utf-8 encoded string
        expected_data = {'Player Name': "Alexis Lafrenière", 'Birth Country': "CAN"}
        actual_data = statsapi.load_player_dict("Alexis Lafrenière")
        self.assertEqual(expected_data, actual_data)

        # Test unknown player
        self.assertIsNone(statsapi.load_player_dict("Sidney Crosby"))

        # Test unknown team
        self.assertIsNone(statsapi.load_player_dict("Connor McDavid", team="CGY"))

        # Test unknown season
        self.assertIsNone(statsapi.load_player_dict("Connor McDavid", season_string="19901991"))

        # Test unknown team and season
        self.assertIsNone(statsapi.load_player_dict("Connor McDavid", team="CGY", season_string="19901991"))

        # Test known team but unknown season
        self.assertIsNone(statsapi.load_player_dict("Connor McDavid", team="EDM", season_string="19901991"))

        # Test known season but unknown team
        self.assertIsNone(statsapi.load_player_dict("Connor McDavid", team="CGY", season_string="20202021"))

    def test_load_player_season_stats_dict(self):
        """ Tests loading player season stats as a dictionary. """
        test_folder = os.path.join(self._test_folder, "test_load_player_season_stats_dict")
        self._generate_typical_test_folder_structure(test_folder)
        statsapi = StatsapiLoader(test_folder)

        # Test typical case
        expected_data = {'Points': 105}
        actual_data = statsapi.load_player_season_stats_dict("Connor McDavid", "20202021")
        self.assertEqual(expected_data, actual_data)

        # Test typical case - player name, team, and season
        expected_data = {'Points': 105}
        actual_data = statsapi.load_player_season_stats_dict("Connor McDavid", "20202021", team="EDM")
        self.assertEqual(expected_data, actual_data)

        # Test unknown team
        self.assertIsNone(statsapi.load_player_season_stats_dict("Connor McDavid", "20202021", team="CGY"))

        # Test unknown season
        self.assertIsNone(statsapi.load_player_season_stats_dict("Connor McDavid", "19901991"))

    def test_get_seasons(self):
        """ Test getting season strings from root folder. """
        # Build test folder structure with empty files
        test_folder = os.path.join(self._test_folder, "test_get_seasons")
        os.makedirs(os.path.join(test_folder, "20192020"))
        os.makedirs(os.path.join(test_folder, "20202021"))
        os.makedirs(os.path.join(test_folder, "1234512346"))
        os.makedirs(os.path.join(test_folder, "invalid"))
        open(os.path.join(test_folder, "20032004"), 'w')
        open(os.path.join(test_folder, "players_id_map.csv"), 'w')

        # Instantiate
        statsapi = StatsapiLoader(test_folder)

        # Test typical case
        expected_data = ["20192020", "20202021", "1234512346"]
        actual_data = statsapi.get_seasons()
        self.assertEqual(set(expected_data), set(actual_data))

    def test__get_player_id(self):
        """ Test helper function to get player ID from map file. """
        test_folder = os.path.join(self._test_folder, "test__get_player_id")
        self._generate_typical_test_folder_structure(test_folder)
        statsapi = StatsapiLoader(test_folder)

        # Test typical case - player name only
        expected_id = 8478402
        actual_id = statsapi._get_player_id("Connor McDavid")
        self.assertEqual(expected_id, actual_id)

        # Test typical case - player name and team name
        expected_id = 8478402
        actual_id = statsapi._get_player_id("Connor McDavid", team="EDM")
        self.assertEqual(expected_id, actual_id)

        # Test typical case - player name and season
        expected_id = 8478402
        actual_id = statsapi._get_player_id("Connor McDavid", season_string="20202021")
        self.assertEqual(expected_id, actual_id)

        # Test typical case - player name, team, and season
        expected_id = 8478402
        actual_id = statsapi._get_player_id("Connor McDavid", team="EDM", season_string="20202021")
        self.assertEqual(expected_id, actual_id)

        # Test typical case - with utf-8 encoded string
        expected_id = 8482109
        actual_id = statsapi._get_player_id("Alexis Lafrenière")
        self.assertEqual(expected_id, actual_id)

        # Test unknown player
        expected_id = -1
        actual_id = statsapi._get_player_id("Sidney Crosby")
        self.assertEqual(expected_id, actual_id)

        # Test unknown team
        expected_id = -1
        actual_id = statsapi._get_player_id("Connor McDavid", team="CGY")
        self.assertEqual(expected_id, actual_id)

        # Test unknown season
        expected_id = -1
        actual_id = statsapi._get_player_id("Connor McDavid", season_string="19901991")
        self.assertEqual(expected_id, actual_id)

        # Test unknown team and season
        expected_id = -1
        actual_id = statsapi._get_player_id("Connor McDavid", team="CGY", season_string="19901991")
        self.assertEqual(expected_id, actual_id)

        # Test known team but unknown season
        expected_id = -1
        actual_id = statsapi._get_player_id("Connor McDavid", team="EDM", season_string="19901991")
        self.assertEqual(expected_id, actual_id)

        # Test known season but unknown team
        expected_id = -1
        actual_id = statsapi._get_player_id("Connor McDavid", team="CGY", season_string="20202021")
        self.assertEqual(expected_id, actual_id)

    def _generate_typical_test_folder_structure(self, root_path):
        """ Helper function to generate a test folder structure similar
            to what the statsapi downloader module would generate. """
        os.makedirs(os.path.join(root_path, "players"), exist_ok=True)
        os.makedirs(os.path.join(root_path, "teams"), exist_ok=True)
        os.makedirs(os.path.join(root_path, "20202021"), exist_ok=True)
        os.makedirs(os.path.join(root_path, "20202021", "season_stats"), exist_ok=True)

        players_map_dicts = [{'Player': "Connor McDavid", 'Team': "EDM", 'Season': "20202021", 'id': 8478402},
                             {'Player': "Alexis Lafrenière", 'Team': "NYR", 'Season': "20202021", 'id': 8482109}]
        self._create_csv_file(os.path.join(root_path, "players_id_map.csv"), players_map_dicts)

        teams_map_dicts = [{'id': 3, 'name': "New York Rangers", 'abbreviation': "NYR"},
                           {'id': 22, 'name': "Edmonton Oilers", 'abbreviation': "EDM"}]
        self._create_csv_file(os.path.join(root_path, "teams_id_map.csv"), teams_map_dicts)

        # Player data
        test_player_dict = {'Player Name': "Connor McDavid", 'Birth Country': "CAN"}
        json.dump(test_player_dict, open(os.path.join(os.path.join(root_path, "players", "player8478402.json")), 'w'))

        test_player_dict = {'Player Name': "Alexis Lafrenière", 'Birth Country': "CAN"}
        json.dump(test_player_dict, open(os.path.join(os.path.join(root_path, "players", "player8482109.json")), 'w'))

        # Season stats data
        test_player_dict = {'Points': 105}
        json.dump(test_player_dict, open(os.path.join(os.path.join(root_path, "20202021", "season_stats",
                  "20202021_player8478402_season_stats.json")), 'w'))

        test_player_dict = {'Points': 21}
        json.dump(test_player_dict, open(os.path.join(os.path.join(root_path, "20202021", "season_stats",
                  "20202021_player8482109_season_stats.json")), 'w'))

    def _create_csv_file(self, file_path, data_dicts):
        """ Helper function to create a CSV file. """
        with open(file_path, 'w', encoding='utf-8') as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=data_dicts[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_dicts)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)