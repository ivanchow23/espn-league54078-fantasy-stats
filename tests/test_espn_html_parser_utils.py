#!/usr/bin/env python
import espn_html_parser_scripts.espn_html_parser_utils as espn_html_parser_utils
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnHtmlParserUtils(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_utils")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_parse_draft_metadata_from_player_str(self):
        """ Tests metadata parsing from draft player string functionality. """
        # Test typical cases
        input_str = "Sidney Crosby Pit, C"
        expected_output = {'Player': "Sidney Crosby", 'Team': "Pit", 'Position': "C"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Vladimir Tarasenko StL, RW"
        expected_output = {'Player': "Vladimir Tarasenko", 'Team': "StL", 'Position': "RW"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Marc-Andre Fleury Vgs, G"
        expected_output = {'Player': "Marc-Andre Fleury", 'Team': "Vgs", 'Position': "G"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "James van Riemsdyk Tor, LW"
        expected_output = {'Player': "James van Riemsdyk", 'Team': "Tor", 'Position': "LW"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Martin St. Louis NYR, RW"
        expected_output = {'Player': "Martin St. Louis", 'Team': "NYR", 'Position': "RW"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Cody Glass , C"
        expected_output = {'Player': "Cody Glass", 'Team': "", 'Position': "C"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test various position designations
        input_str = "Player One Ana, D"
        expected_output = {'Player': "Player One", 'Team': "Ana", 'Position': "D"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Player One Vgs, LW"
        expected_output = {'Player': "Player One", 'Team': "Vgs", 'Position': "LW"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test invalid position designations which could still be parsed
        input_str = "Invalid Player Ana, E"
        expected_output = {'Player': "Invalid Player", 'Team': "Ana", 'Position': "E"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Invalid Player Ana, 123"
        expected_output = {'Player': "Invalid Player", 'Team': "Ana", 'Position': "123"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test unknown team abbreviations which could still be parsed
        input_str = "Some Player AAA, C"
        expected_output = {'Player': "Some Player", 'Team': "AAA", 'Position': "C"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test weird team abbreviations which could still be parsed
        input_str = "Some Player uTaH, C"
        expected_output = {'Player': "Some Player", 'Team': "uTaH", 'Position': "C"}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test incorrect input format
        input_str = "Invalid Format Ana,C"
        expected_output = {'Player': "", 'Team': "", 'Position': ""}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = "Invalid PlayerAna, LW"
        expected_output = {'Player': "", 'Team': "", 'Position': ""}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        # Test invalid inputs
        input_str = None
        expected_output = {'Player': "", 'Team': "", 'Position': ""}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = 12345
        expected_output = {'Player': "", 'Team': "", 'Position': ""}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

        input_str = [1, 2, 3]
        expected_output = {'Player': "", 'Team': "", 'Position': ""}
        actual_output = espn_html_parser_utils.parse_draft_metadata_from_player_str(input_str)
        self.assertEqual(expected_output, actual_output)

    def test_check_html(self):
        """ Test check HTML helper function. """
        # Create empty HTML file for testing
        html_path = os.path.join(self._test_folder, "test.html")
        csv_path = os.path.join(self._test_folder, "test.csv")
        self._create_empty_file(html_path)
        self._create_empty_file(csv_path)

        # Test typical case
        self.assertTrue(espn_html_parser_utils.check_html(html_path))

        # Test invalid cases
        self.assertFalse(espn_html_parser_utils.check_html(csv_path))
        self.assertFalse(espn_html_parser_utils.check_html(os.path.join(self._test_folder, "doesnt_exist.html")))
        self.assertFalse(espn_html_parser_utils.check_html(r"not/a/path"))
        self.assertFalse(espn_html_parser_utils.check_html("123"))
        self.assertFalse(espn_html_parser_utils.check_html(123))
        self.assertFalse(espn_html_parser_utils.check_html([1, 2, 3]))
        self.assertFalse(espn_html_parser_utils.check_html(None))

    def test_sub_special_chars(self):
        """ Test subbing special characters helper function. """
        # Test typical cases to replace
        self.assertEqual(espn_html_parser_utils.sub_special_chars("Sub?"), "Sub_")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("?Sub?"), "_Sub_")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("Sub:"), "Sub_")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("?:~"), "__~")
        self.assertEqual(espn_html_parser_utils.sub_special_chars(r"Sub\/123:"), "Sub__123_")

        # Test some characters that don't require replacing
        self.assertEqual(espn_html_parser_utils.sub_special_chars("#NoSub"), "#NoSub")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("NoSub!"), "NoSub!")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("!!!(NoSub)!!!"), "!!!(NoSub)!!!")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("No.Sub"), "No.Sub")
        self.assertEqual(espn_html_parser_utils.sub_special_chars("ミスター スパーコル.NoSub"), "ミスター スパーコル.NoSub")

        # Test non-string inputs
        self.assertEqual(espn_html_parser_utils.sub_special_chars(123), 123)
        self.assertEqual(espn_html_parser_utils.sub_special_chars([1, 2, 3]), [1, 2, 3])
        self.assertEqual(espn_html_parser_utils.sub_special_chars(None), None)

    def _create_empty_file(self, file_path):
        """ Helper function to create an empty file. """
        with open(file_path, 'w') as f:
            pass

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)