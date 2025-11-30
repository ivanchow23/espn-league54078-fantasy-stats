#!/usr/bin/env python
from espn_fantasy_api_scripts.espn_fantasy_api_draft_details_parser import EspnFantasyApiDraftDetailsParser
import os
import unittest

class TestEspnFantasyApiDraftDetailsParser(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        pass

    def test_get_draft_details_as_dicts(self):
        """ Test typical use-case of getting draft details """
        # Mimic part of the loaded dictionary structure
        input_dict = {
            "draftDetail": {'picks': [{'overallPickNumber': 1, 'roundPickNumber': 1, 'roundId': 1, 'teamId': "abcd", 'playerId': 12345},
                                      {'overallPickNumber': 2, 'roundPickNumber': 2, 'roundId': 1, 'teamId': "efgh", 'playerId': 99999},
                                      {'overallPickNumber': 3, 'roundPickNumber': 3, 'roundId': 1, 'teamId': "wxyz", 'playerId': 54321}]}}

        # Instantiate
        parser = EspnFantasyApiDraftDetailsParser(input_dict)
        actual_result = parser.get_draft_details_as_dicts()
        expected_result = [{'Draft Number': 1, 'Round Pick Number': 1, 'Round Number': 1, 'Owner ID': "abcd", 'Player ID': 12345,},
                           {'Draft Number': 2, 'Round Pick Number': 2, 'Round Number': 1, 'Owner ID': "efgh", 'Player ID': 99999,},
                           {'Draft Number': 3, 'Round Pick Number': 3, 'Round Number': 1, 'Owner ID': "wxyz", 'Player ID': 54321,}]

        self.assertEqual(expected_result, actual_result)

    def tearDown(self):
        """ Remove any items. """
        pass