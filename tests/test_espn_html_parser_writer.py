#!/usr/bin/env python
import os
import pandas as pd
import pickle
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_html_parser_scripts"))
import espn_html_parser_writer

class TestEspnHtmlParserWriter(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder = os.path.join(SCRIPT_DIR, "test_espn_html_parser_writer_folder")
        os.makedirs(self._test_folder, exist_ok=True)

    def test_EspnHtmlParserWriter(self):
        """ Test instantiation of class. """
        test_folder = os.path.join(self._test_folder, "test_EspnHtmlParserWriter")

        # Test typical case
        espn = espn_html_parser_writer.EspnHtmlParserWriter(test_folder)
        self.assertTrue(os.path.exists(os.path.join(test_folder, "csv")))
        self.assertTrue(os.path.exists(os.path.join(test_folder, "excel")))
        self.assertTrue(os.path.exists(os.path.join(test_folder, "pickles")))

    def test_df_to_csv(self):
        """ Test dataframe to CSV. """
        test_folder = os.path.join(self._test_folder, "test_df_to_csv")
        test_df = pd.DataFrame([{'A': 1, 'B': 2}, {'A': 3, 'B': 4}])
        espn = espn_html_parser_writer.EspnHtmlParserWriter(test_folder)

        # Test typical case
        espn.df_to_csv(test_df, "test_df.csv")
        expected_data = test_df
        actual_data = pd.read_csv(os.path.join(test_folder, "csv", "test_df.csv"))
        pd.testing.assert_frame_equal(expected_data, actual_data)

        # Test empty dataframe
        espn.df_to_csv(pd.DataFrame(), "test_empty_df.csv")
        self.assertFalse(os.path.exists(os.path.join(test_folder, "csv", "test_empty_df.csv")))

        # Test invalid input
        espn.df_to_csv([1, 2, 3], "test_invalid_df.csv")
        self.assertFalse(os.path.exists(os.path.join(test_folder, "csv", "test_invalid_df.csv")))

        # Test invalid input
        espn.df_to_csv(123, "test_invalid_df.csv")
        self.assertFalse(os.path.exists(os.path.join(test_folder, "csv", "test_invalid_df.csv")))

        # Test invalid input
        espn.df_to_csv("123", "test_invalid_df.csv")
        self.assertFalse(os.path.exists(os.path.join(test_folder, "csv", "test_invalid_df.csv")))

        # Test invalid input
        espn.df_to_csv(None, "test_invalid_df.csv")
        self.assertFalse(os.path.exists(os.path.join(test_folder, "csv", "test_invalid_df.csv")))

    def test_df_to_excel(self):
        """ Test dataframe to Excel. """
        test_folder = os.path.join(self._test_folder, "test_df_to_excel")
        test_df1 = pd.DataFrame([{'A': 1, 'B': 2}, {'A': 3, 'B': 4}])
        test_df2 = pd.DataFrame([{'C': 5, 'D': 6}, {'C': 7, 'D': 8}])
        test_df3 = pd.DataFrame([{'E': 9, 'F': 10}, {'E': 11, 'F': 12}])
        test_multi_df = pd.DataFrame(columns=pd.MultiIndex.from_tuples([("Test", "Col1"), ("Test", "Col2")]))
        test_multi_df['Test'] = pd.DataFrame([{'Col1': 100, 'Col2': 200}, {'Col1': 101, 'Col2': 201}])
        espn = espn_html_parser_writer.EspnHtmlParserWriter(test_folder)

        # Test typical case - no sheet specified
        file_name = "test_file_single_sheet.xlsx"
        espn.df_to_excel(test_df1, file_name)
        output_file_path = os.path.join(test_folder, "excel", file_name)
        pd.testing.assert_frame_equal(test_df1, pd.read_excel(output_file_path, sheet_name="Sheet1"))

        # Test typical case - multi-index dataframe
        # Note: Expected return is a lot different than original input
        #   - Multi-index dataframe writes produce a single empty row
        #   - It also currently does not support index=False, so also "read-in" the index column
        # Therefore, intentionally not checking the contents of the file
        # Instead, this is only to test that the index=False logic does not cause a "not implemented" error
        file_name = "test_file_multiindex_df.xlsx"
        espn.df_to_excel(test_multi_df, file_name)

        # Test typical case - write to multiple sheets
        file_name = "test_file_multiple_sheets.xlsx"
        espn.df_to_excel(test_df1, file_name, sheet_name="Test Sheet 1")
        espn.df_to_excel(test_df2, file_name, sheet_name="Test Sheet 2")
        espn.df_to_excel(test_df3, file_name, sheet_name="Test Sheet 3")
        output_file_path = os.path.join(test_folder, "excel", file_name)
        pd.testing.assert_frame_equal(test_df1, pd.read_excel(output_file_path, sheet_name="Test Sheet 1"))
        pd.testing.assert_frame_equal(test_df2, pd.read_excel(output_file_path, sheet_name="Test Sheet 2"))
        pd.testing.assert_frame_equal(test_df3, pd.read_excel(output_file_path, sheet_name="Test Sheet 3"))

        # Test writing to a sheet that already exists
        file_name = "test_file_write_sheet_exists.xlsx"
        test_file_path = os.path.join(test_folder, file_name)
        espn.df_to_excel(test_df1, file_name, sheet_name="Test Sheet")
        espn.df_to_excel(test_df2, file_name, sheet_name="Test Sheet")
        output_file_path = os.path.join(test_folder, "excel", file_name)
        pd.testing.assert_frame_equal(test_df2, pd.read_excel(output_file_path, sheet_name="Test Sheet"))

        # Test invalid inputs
        test_file_path = os.path.join(test_folder, "test_invalid.xlsx")
        espn.df_to_excel("123", test_file_path)
        espn.df_to_excel(123, test_file_path)
        espn.df_to_excel([1, 2, 3], test_file_path)
        espn.df_to_excel(None, test_file_path)
        self.assertFalse(os.path.exists(test_file_path))

    def test_to_pickle(self):
        """ Test data to pickle. """
        test_folder = os.path.join(self._test_folder, "test_to_pickle")
        test_file_path = os.path.join(test_folder, "test.pickle")
        espn = espn_html_parser_writer.EspnHtmlParserWriter(test_folder)

        # Test typical case of various inputs
        input_data = 123
        espn.to_pickle(input_data, test_file_path)
        self.assertTrue(input_data, pickle.load(open(test_file_path, 'rb')))

        # Test typical case of various inputs
        input_data = pd.DataFrame([{'A': 1, 'B': 2}, {'A': 3, 'B': 4}])
        espn.to_pickle(input_data, test_file_path)
        pd.testing.assert_frame_equal(input_data, pickle.load(open(test_file_path, 'rb')))

        # Test typical case of various inputs
        input_data = [pd.DataFrame([{'A': 1, 'B': 2}, {'A': 3, 'B': 4}]),
                      pd.DataFrame([{'C': 10, 'D': 20}, {'C': 30, 'D': 40}])]
        espn.to_pickle(input_data, test_file_path)
        self.assertTrue(input_data, pickle.load(open(test_file_path, 'rb')))

        # Test typical case of various inputs
        input_data = {'key1': "data", 'nested_dict': {'key2': 123}, 'key3': pd.DataFrame([{'A': 1, 'B': 2}]), 'key4': [1, 2, 3]}
        espn.to_pickle(input_data, test_file_path)
        self.assertTrue(input_data, pickle.load(open(test_file_path, 'rb')))

        # Test typical case of various inputs
        input_data = None
        espn.to_pickle(input_data, test_file_path)
        self.assertIsNone(pickle.load(open(test_file_path, 'rb')))

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder)