from espn_html_parser_draft_recap import EspnHtmlParserDraftRecap
import os
import pandas as pd
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestEspnHtmlParserDraftRecap(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_draft_recap")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_EspnHtmlParserDraftRecap(self):
        """ Test constructor. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_EspnHtmlParserDraftRecap")
        os.makedirs(test_folder, exist_ok=True)
        test_file_path = os.path.join(test_folder, "test.html")
        open(test_file_path, 'w')

        # Test typical case
        espn = EspnHtmlParserDraftRecap(test_file_path)
        self.assertTrue(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserDraftRecap(os.path.join(self._test_folder, "does_not_exist.html"))
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserDraftRecap("Not a file.")
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserDraftRecap(123)
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserDraftRecap([1, 2, 3])
        self.assertFalse(espn.valid)

        # Test invalid input
        espn = EspnHtmlParserDraftRecap(None)
        self.assertFalse(espn.valid)

    def test_get_df(self):
        """ Test getting draft recap dataframe. """
        # Set up input files
        test_folder = os.path.join(self._test_folder, "test_get_df")
        os.makedirs(test_folder, exist_ok=True)
        empty_file_path = os.path.join(test_folder, "empty.html")
        open(empty_file_path, 'w')

        # Test empty input
        espn = EspnHtmlParserDraftRecap(empty_file_path)
        self.assertTrue(espn.get_df().empty)

        # Note: No tests for parsing a representative HTML page yet

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)