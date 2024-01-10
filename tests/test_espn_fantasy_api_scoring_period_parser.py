#!/usr/bin/env python
import os
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_scripts"))
from espn_fantasy_api_scoring_period_parser import EspnFantasyApiScoringPeriodParser

class TestEspnFantasyApiScoringPeriodParser(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        pass

    def test_get_owner_roster_applied_stats_as_dicts(self):
        """ Test typical use-case of getting applied stats. """
        # Mimic part of the loaded dictionary structure
        input_dict = {'scoringPeriodId': 1,
                      'teams': [{'owners': ["1a2b"],
                                 'roster': {'entries': [{'lineupSlotId': 3, 'playerPoolEntry': {'player': {'fullName': "Player 1", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 5, 'appliedStats': {'13': 2, '14': 1, '38': 1, '39': 1}, 'stats': {'13': 2, '14': 1, '38': 1, '39': 1}}]}}},
                                                        {'lineupSlotId': 4, 'playerPoolEntry': {'player': {'fullName': "Player 2", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 3, 'appliedStats': {'13': 0, '14': 3, '38': 0, '39': 0}, 'stats': {'13': 0, '14': 3, '38': 0, '39': 0}}]}}},
                                                        {'lineupSlotId': 5, 'playerPoolEntry': {'player': {'fullName': "Player 3", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 2, 'appliedStats': {'1': 1,  '7': 1}, 'stats': {'1': 1,  '7': 1}}]}}}
                                                       ]}}]}

        # Instantiate
        parser = EspnFantasyApiScoringPeriodParser(input_dict)
        actual_result = parser.get_owner_roster_applied_stats_as_dicts("1a2b")
        expected_result = [{'fullName': "Player 1", 'lineupSlotId': 3, 'G': 2, 'A': 1, 'PPP': 1, 'SHP': 1, 'appliedTotal': 5, 'GP': 1},
                           {'fullName': "Player 2", 'lineupSlotId': 4, 'G': 0, 'A': 3, 'PPP': 0, 'SHP': 0, 'appliedTotal': 3, 'GP': 1},
                           {'fullName': "Player 3", 'lineupSlotId': 5, 'W': 1, 'SO': 1, 'appliedTotal': 2, 'GP': 1}]

        self.assertEquals(expected_result, actual_result)

    def test_get_owner_roster_applied_stats_as_dicts_no_game(self):
        """ Test when player(s) did not play a game for given scoring period.
            Pattern appears to be when scoringPeriodId of the dictionary does
            not exist in any stat entries. """
        # Mimic part of the loaded dictionary structure
        input_dict = {'scoringPeriodId': 1,
                      'teams': [{'owners': ["1a2b"],
                                 'roster': {'entries': [{'lineupSlotId': 3, 'playerPoolEntry': {'player': {'fullName': "Player 1", 'stats': [{'scoringPeriodId': 10, 'appliedTotal': 5, 'appliedStats': {'13': 2, '14': 1, '38': 1, '39': 1}, 'stats': {'13': 2, '14': 1, '38': 1, '39': 1}}]}}},
                                                        {'lineupSlotId': 4, 'playerPoolEntry': {'player': {'fullName': "Player 2", 'stats': [{'scoringPeriodId': 20, 'appliedTotal': 3, 'appliedStats': {'13': 0, '14': 3, '38': 0, '39': 0}, 'stats': {'13': 0, '14': 3, '38': 0, '39': 0}}]}}},
                                                        {'lineupSlotId': 5, 'playerPoolEntry': {'player': {'fullName': "Player 3", 'stats': [{'scoringPeriodId': 99, 'appliedTotal': 2, 'appliedStats': {'1': 1,  '7': 1}, 'stats': {'1': 1,  '7': 1}}]}}}
                                                       ]}}]}

        parser = EspnFantasyApiScoringPeriodParser(input_dict)
        actual_result = parser.get_owner_roster_applied_stats_as_dicts("1a2b")
        expected_result = [{'fullName': "Player 1", 'lineupSlotId': 3},
                           {'fullName': "Player 2", 'lineupSlotId': 4},
                           {'fullName': "Player 3", 'lineupSlotId': 5}]

        self.assertEquals(expected_result, actual_result)

    def test_get_owner_roster_applied_stats_as_dicts_empty_applied_stats_and_stats_for_scoring_period(self):
        """ Test when player(s) did not play a game (even though there was a game)
            for a given scoring period. Pattern appears to be when scoringPeriodId
            of a dictionary exists, but one of appliedStats or stats dictionary is
            empty. """
        # Mimic part of the loaded dictionary structure
        input_dict = {'scoringPeriodId': 1,
                      'teams': [{'owners': ["1a2b"],
                                 'roster': {'entries': [{'lineupSlotId': 3, 'playerPoolEntry': {'player': {'fullName': "Player 1", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 0, 'appliedStats': {}, 'stats': {}}]}}},
                                                        {'lineupSlotId': 4, 'playerPoolEntry': {'player': {'fullName': "Player 2", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 0, 'appliedStats': {}, 'stats': {'1': 5}}]}}},
                                                        {'lineupSlotId': 5, 'playerPoolEntry': {'player': {'fullName': "Player 3", 'stats': [{'scoringPeriodId': 1, 'appliedTotal': 0, 'appliedStats': {'6': 0}, 'stats': {}}]}}}
                                                       ]}}]}

        parser = EspnFantasyApiScoringPeriodParser(input_dict)
        actual_result = parser.get_owner_roster_applied_stats_as_dicts("1a2b")
        expected_result = [{'fullName': "Player 1", 'lineupSlotId': 3, 'appliedTotal': 0},
                           {'fullName': "Player 2", 'lineupSlotId': 4, 'appliedTotal': 0},
                           {'fullName': "Player 3", 'lineupSlotId': 5, 'appliedTotal': 0, 'SV': 0}]

        self.assertEquals(expected_result, actual_result)

    def tearDown(self):
        """ Remove any items. """
        pass