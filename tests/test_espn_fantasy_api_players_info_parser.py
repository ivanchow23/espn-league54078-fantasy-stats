#!/usr/bin/env python
from espn_fantasy_api_scripts.espn_fantasy_api_all_players_info_parser import EspnFantasyApiAllPlayersInfoParser
import os
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnFantasyApiAllPlayerInfoParser(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        pass

    def test_get_all_players_info_as_dicts(self):
        """ Test typical use-case of getting applied stats. """
        # Mimic part of the loaded dictionary structure
        input_dict = {
            "players": [{
                "player": {"fullName": "Player 1",
                           "id": 12345,
                           "stats": [{"appliedTotal": 414.0, "id": "102023", "stats": {'13': 0, '14': 0, '38': 0, '39': 0}},
                                     {"appliedTotal": 566.0, "id": "002023", "stats": {'13': 2, '14': 1, '38': 1, '39': 1, '34': 23}}
                            ]}}]}

        # Instantiate
        parser = EspnFantasyApiAllPlayersInfoParser('20222023', input_dict)
        actual_result = parser.get_all_players_info_as_dicts()
        expected_result = [{'Player Name': "Player 1", 'Player ID': 12345, 'Fantasy Points': 566.0, 'G': 2, 'A': 1, 'PPP': 1, 'SHP': 1, 'GP': 23}]

        self.assertEqual(expected_result, actual_result)

    def tearDown(self):
        """ Remove any items. """
        pass