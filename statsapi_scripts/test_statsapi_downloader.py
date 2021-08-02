#!/usr/env/bin python
import os
import shutil
import statsapi_downloader
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

class TestStatsApiDownloader(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        self._root_folder_path = os.path.join(SCRIPT_DIR, "test_folder")
        os.mkdir(self._root_folder_path)

    def test_download_teams_data(self):
        """ Tests functionality to download team data. """
        # Test invalid root folder path
        invalid_path = None
        self.assertFalse(statsapi_downloader.download_teams_data(invalid_path))

        # Test typical use-case but overwrite any existing files
        # - Check various files exist (assumes chosen teams are still in the league during time of test)
        statsapi_downloader.download_teams_data(self._root_folder_path, overwrite=True)

        data_folder_path = os.path.join(self._root_folder_path, "teams")
        self.assertTrue(os.path.exists(data_folder_path))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team6.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team20.json")))

        # Test typical use-case but don't overwrite any existing files (depends on previous case)
        # First, store modification date of various files before running function
        # - Check various files exist
        # - Check files did not change
        mod_time_team1  = os.path.getmtime(os.path.join(data_folder_path, "team1.json"))
        mod_time_team6  = os.path.getmtime(os.path.join(data_folder_path, "team6.json"))
        mod_time_team20 = os.path.getmtime(os.path.join(data_folder_path, "team20.json"))

        statsapi_downloader.download_teams_data(self._root_folder_path)

        self.assertTrue(os.path.exists(data_folder_path))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team6.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team20.json")))

        new_mod_time_team1  = os.path.getmtime(os.path.join(data_folder_path, "team1.json"))
        new_mod_time_team6  = os.path.getmtime(os.path.join(data_folder_path, "team6.json"))
        new_mod_time_team20 = os.path.getmtime(os.path.join(data_folder_path, "team20.json"))

        self.assertEqual(mod_time_team1, new_mod_time_team1)
        self.assertEqual(mod_time_team6, new_mod_time_team6)
        self.assertEqual(mod_time_team20, new_mod_time_team20)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._root_folder_path)