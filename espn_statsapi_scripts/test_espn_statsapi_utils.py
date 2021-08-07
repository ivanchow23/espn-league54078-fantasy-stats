#!/usr/bin/env python
import os
import espn_statsapi_utils
import unittest

import espn_statsapi_utils
import unittest

class TestEspnUtils(unittest.TestCase):
    def SetUp(self):
        """ Set-up required items. """
        pass

    def test_statsapi_team_abbrev(self):
        """ Test statsapi team abbreviation function. """
        # Test typical case
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("Ana"), "ANA")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("Sea"), "SEA")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("NYR"), "NYR")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("SJ"), "SJS")

        # Test non-existent mapping
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("Aaa"), "")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("123"), "")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev("???"), "")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev(""), "")

        # Test invalid input
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev(None), "")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev(123), "")
        self.assertEqual(espn_statsapi_utils.statsapi_team_abbrev([1, 2, 3]), "")

    def test_espn_team_abbrev(self):
        """ Test ESPN team abbreviation function. """
        # Test typical case
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("ANA"), "Ana")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("SEA"), "Sea")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("NYR"), "NYR")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("SJS"), "SJ")

        # Test non-existent mapping
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("AAA"), "")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("123"), "")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev("???"), "")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev(""), "")

        # Test invalid input
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev(None), "")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev(123), "")
        self.assertEqual(espn_statsapi_utils.espn_team_abbrev([1, 2, 3]), "")        

    def TearDown(self):
        """ Remove any items. """
        pass