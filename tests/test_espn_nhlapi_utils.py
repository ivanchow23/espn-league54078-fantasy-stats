#!/usr/bin/env python
import os
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_nhlapi_scripts"))
import espn_nhlapi_utils as enu

class TestEspnUtils(unittest.TestCase):
    def test_player_name_is_close_match_identical(self):
        """ Test player_name_is_close_match for identical names """
        self.assertTrue(enu.player_name_is_close_match("Sidney Crosby", "Sidney Crosby"))

    def test_player_name_is_close_match_accented_characters(self):
        """ Test player_name_is_close_match with accented characters """
        self.assertTrue(enu.player_name_is_close_match("Tim Stutzle", "Tim Stützle"))

    def test_player_name_is_close_match_identical_spaced_lastname(self):
        """ Test player_name_is_close_match for identical but with spaced last name """
        self.assertTrue(enu.player_name_is_close_match("Martin St. Louis", "Martin St. Louis"))

    def test_player_name_is_close_match_different_abbrev_first_names(self):
        """ Test player_name_is_close_match for different abbreviated first names """
        self.assertTrue(enu.player_name_is_close_match("P.K. Subban", "PK Subban"))
        self.assertTrue(enu.player_name_is_close_match("TJ Brodie", "T.J. Brodie"))

    def test_player_name_is_close_match_shortened_names(self):
        """ Test player_name_is_close_match for shortened names """
        self.assertTrue(enu.player_name_is_close_match("Cam Atkinson", "Cameron Atkinson"))
        self.assertTrue(enu.player_name_is_close_match("Mitchell Marner", "Mitch Marner"))

    def test_player_name_is_close_match_different_first_name(self):
        """ Test player_name_is_close_match for different first names """
        self.assertFalse(enu.player_name_is_close_match("Erik Karlsson", "William Karlsson"))

    def test_player_name_is_close_match_different_first_character_of_first_name(self):
        """ Test player_name_is_close_match for different starting character of first names """
        self.assertFalse(enu.player_name_is_close_match("Ryan Getzlaf", "Cyan Getzlaf"))

    def test_player_name_is_close_match_different_first_name_same_first_character(self):
        """ Test player_name_is_close_match for different first names but same first character """
        self.assertFalse(enu.player_name_is_close_match("Bob Smith", "Brad Smith"))

    def test_player_name_is_close_match_set_of_hardcoded_names(self):
        """ Test player_name_is_close_match for a set of hardcoded names """
        self.assertTrue(enu.player_name_is_close_match("Mike Cammalleri", "Michael Cammalleri"))
        self.assertTrue(enu.player_name_is_close_match("Michael Cammalleri", "Mike Cammalleri"))
        self.assertTrue(enu.player_name_is_close_match("Matt Dumba", "Mathew Dumba"))
        self.assertTrue(enu.player_name_is_close_match("Mathew Dumba", "Matt Dumba"))