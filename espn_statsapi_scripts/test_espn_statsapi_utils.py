#!/usr/bin/env python
import csv
import espn_statsapi_utils
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(SCRIPT_DIR, "test_espn_statsapi_utils")

class TestEspnUtils(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        # Create test directory
        os.makedirs(TEST_DIR, exist_ok=True)

        # Generate test file
        self._test_correction_file_path = os.path.join(TEST_DIR, "test.csv")
        self._create_csv(self._test_correction_file_path, [{'Player': "T.J. Brodie", 'Team': "CGY", 'Corrected Player': "TJ Brodie", 'Corrected Team': "CGY"},
                                                           {'Player': "Joe Pavelski", 'Team': "DAL", 'Corrected Player': "Joe Pavelski", 'Corrected Team': "DAL"},
                                                           {'Player': "Alexis Lafreniere", 'Team': "NYR", 'Corrected Player': "Alexis Lafrenière", 'Corrected Team': "NYR"}])

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

    def test_CorrectionUtil(self):
        """ Test instantiation of correction utility object. """
        # Test typical case
        corr = espn_statsapi_utils.CorrectionUtil(self._test_correction_file_path)
        self.assertTrue(corr.valid)

        # Test file with extra columns
        file_path = os.path.join(TEST_DIR, "test_correction_file_path_extra_cols.csv")
        self._create_csv(file_path, [{'Player': "T.J. Brodie", 'Team': "CGY", 'Corrected Player': "TJ Brodie", 'Corrected Team': "CGY", 'Extra': "123"}])
        corr = espn_statsapi_utils.CorrectionUtil(file_path)
        self.assertTrue(corr.valid)

        # Test mixed-case CSV suffix
        file_path = os.path.join(TEST_DIR, "test_correction_file_mixed_case_suffix.CsV")
        self._create_csv(file_path, [{'Player': "T.J. Brodie", 'Team': "CGY", 'Corrected Player': "TJ Brodie", 'Corrected Team': "CGY"}])
        corr = espn_statsapi_utils.CorrectionUtil(file_path)
        self.assertTrue(corr.valid)

        # Test invalid file path
        corr = espn_statsapi_utils.CorrectionUtil(r"not\a\valid\path.csv")
        self.assertFalse(corr.valid)

        # Test non-CSV
        with open(os.path.join(TEST_DIR, "blank.bin"), 'w') as f:
            pass
        corr = espn_statsapi_utils.CorrectionUtil(os.path.join(TEST_DIR, "blank.bin"))
        self.assertFalse(corr.valid)

        # Test empty file
        with open(os.path.join(TEST_DIR, "blank.csv"), 'w') as f:
            pass
        corr = espn_statsapi_utils.CorrectionUtil(os.path.join(TEST_DIR, "blank.bin"))
        self.assertFalse(corr.valid)

    def test_get_corrected_dict(self):
        """ Test getting corrected dict from correction object. """
        # Test typical case
        corr = espn_statsapi_utils.CorrectionUtil(self._test_correction_file_path)
        expected_ret = {'Corrected Player': "Alexis Lafrenière", 'Corrected Team': "NYR"}
        actual_ret = corr.get_corrected_dict("Alexis Lafreniere", "NYR")
        self.assertEqual(expected_ret, actual_ret)

        # Test no correcion entry
        corr = espn_statsapi_utils.CorrectionUtil(self._test_correction_file_path)
        actual_ret = corr.get_corrected_dict("Sidney Crosby", "PIT")
        self.assertIsNone(actual_ret)

        # Test invalid object
        corr = espn_statsapi_utils.CorrectionUtil(None)
        actual_ret = corr.get_corrected_dict("Sidney Crosby", "PIT")
        self.assertIsNone(actual_ret)

    def _create_csv(self, file_path, data_dicts):
        """ Simple helper function to generate a CSV file from list of dictionaries. """
        with open(file_path, 'w', newline="", encoding='utf-8') as csv_file:
            dict_writer = csv.DictWriter(csv_file, fieldnames=data_dicts[0].keys())
            dict_writer.writeheader()
            dict_writer.writerows(data_dicts)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(TEST_DIR)