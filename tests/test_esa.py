#!usr/bin/env python
import os
import shutil
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

import sys
sys.path.insert(1, os.path.join(SCRIPT_DIR, "..", "espn_statsapi_analysis"))
import esa

class TestEsa(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._test_folder_path = os.path.join(SCRIPT_DIR, "TestEsa")
        os.makedirs(self._test_folder_path, exist_ok=True)

    def test__get_import_modules_from_toml_list(self):
        """ Test helper function to get list of modules to import. """
        # Generate test folder structure
        # modules
        # - f1.py
        # - f2.py
        # - folder1
        #   -> f3.py
        #   -> f4.py
        # - folder2
        #   -> f5.py
        #   -> f6.py
        #   -> folder3
        #     -> f7.py
        #     -> f8.py
        test_folder_path = os.path.join(self._test_folder_path, "test__get_import_modules_from_toml_list", "modules")
        os.makedirs(test_folder_path, exist_ok=True)
        self._write_empty_file(os.path.join(test_folder_path, "f1.py"))
        self._write_empty_file(os.path.join(test_folder_path, "f2.py"))
        os.makedirs(os.path.join(test_folder_path, "folder1"), exist_ok=True)
        self._write_empty_file(os.path.join(test_folder_path, "folder1", "f3.py"))
        self._write_empty_file(os.path.join(test_folder_path, "folder1", "f4.py"))
        os.makedirs(os.path.join(test_folder_path, "folder2"), exist_ok=True)
        self._write_empty_file(os.path.join(test_folder_path, "folder2", "f5.py"))
        self._write_empty_file(os.path.join(test_folder_path, "folder2", "f6.py"))
        os.makedirs(os.path.join(test_folder_path, "folder2", "folder3"), exist_ok=True)
        self._write_empty_file(os.path.join(test_folder_path, "folder2", "folder3", "f7.py"))
        self._write_empty_file(os.path.join(test_folder_path, "folder2", "folder3", "f8.py"))

        # Test typical case
        input_list = ["f1", "f2"]
        expected_list = ["modules.f1", "modules.f2"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test typical case
        input_list = ["folder1.f3", "folder1.f4", "folder2.f6"]
        expected_list = ["modules.folder1.f3", "modules.folder1.f4", "modules.folder2.f6"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test typical case
        input_list = ["f1", "f2", "folder2.folder3.f7"]
        expected_list = ["modules.f1", "modules.f2", "modules.folder2.folder3.f7"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test "all in folder" operator
        input_list = [".*"]
        expected_list = ["modules.f1", "modules.f2"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test "all in folder" operator
        input_list = [".*", "folder1.*"]
        expected_list = ["modules.f1", "modules.f2", "modules.folder1.f3", "modules.folder1.f4"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test "all in folder" operator
        input_list = [".*", "folder1.*", "folder2.*", "folder2.folder3.*"]
        expected_list = ["modules.f1", "modules.f2", "modules.folder1.f3", "modules.folder1.f4",
                         "modules.folder2.f5", "modules.folder2.f6", "modules.folder2.folder3.f7",
                         "modules.folder2.folder3.f8"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test duplicate inputs
        input_list = ["folder1.f3", "folder1.f4", "folder1.*"]
        expected_list = ["modules.folder1.f3", "modules.folder1.f4"]
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test invalid input
        input_list = 123
        expected_list = []
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

        # Test invalid input
        input_list = None
        expected_list = []
        actual_list = esa._get_import_modules_from_toml_list(input_list, root_modules_path=test_folder_path)
        self.assertEqual(expected_list, actual_list)

    def _write_empty_file(self, file_path):
        """ Helper function to generate an empty file. """
        with open(file_path, 'w') as f:
            pass

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._test_folder_path)