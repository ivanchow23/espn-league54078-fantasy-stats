#!/usr/bin/env python
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
        # Create root folder for this test
        test_folder_path = os.path.join(self._root_folder_path, "test_download_teams_data_root")
        os.mkdir(test_folder_path)

        # Test invalid root folder path
        invalid_path = None
        self.assertFalse(statsapi_downloader.download_teams_data(invalid_path))

        # Test typical use-case but overwrite any existing files
        # - Check various files exist (assumes chosen teams are still in the league during time of test)
        statsapi_downloader.download_teams_data(test_folder_path, overwrite=True)

        data_folder_path = os.path.join(test_folder_path, "teams")
        self.assertTrue(os.path.exists(data_folder_path))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "teams_id_map.csv")))
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

        statsapi_downloader.download_teams_data(test_folder_path)

        self.assertTrue(os.path.exists(data_folder_path))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "teams_id_map.csv")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team1.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team6.json")))
        self.assertTrue(os.path.exists(os.path.join(data_folder_path, "team20.json")))

        new_mod_time_team1  = os.path.getmtime(os.path.join(data_folder_path, "team1.json"))
        new_mod_time_team6  = os.path.getmtime(os.path.join(data_folder_path, "team6.json"))
        new_mod_time_team20 = os.path.getmtime(os.path.join(data_folder_path, "team20.json"))

        self.assertEqual(mod_time_team1, new_mod_time_team1)
        self.assertEqual(mod_time_team6, new_mod_time_team6)
        self.assertEqual(mod_time_team20, new_mod_time_team20)

    def test_download_team_rosters_data(self):
        """ Tests functionality to download team roster data. """
        # Create root folder for this test
        test_folder_path = os.path.join(self._root_folder_path, "test_download_team_rosters_data_root")
        os.mkdir(test_folder_path)

        # Test typical case
        # This function depends on teams data to be downloaded. First test run will not have it.
        # - Check false return
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 2018, 2020))

        # Test typical case
        # This time, generate own test data to mimic downloaded team data.
        # - Check true return
        # - Check files exist in output
        teams_data_path = os.path.join(test_folder_path, "teams")
        os.mkdir(teams_data_path)
        self._create_empty_file(os.path.join(teams_data_path, "team1.json"))
        self._create_empty_file(os.path.join(teams_data_path, "team6.json"))
        self._create_empty_file(os.path.join(teams_data_path, "team20.json"))

        self.assertTrue(statsapi_downloader.download_team_rosters_data(test_folder_path, 2018, 2020))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20182019", "team_rosters", "20182019_team1_roster.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20192020", "team_rosters", "20192020_team6_roster.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20202021", "team_rosters", "20202021_team20_roster.json")))

        # Test typical case with overwrite
        # Keep track of modified time
        # - Check true return
        # - Check files exist in output
        # - Check modified time changed to a greater time (indicating overwrite)
        mod_time_team1  = os.path.getmtime(os.path.join(test_folder_path, "20182019", "team_rosters", "20182019_team1_roster.json"))
        mod_time_team6  = os.path.getmtime(os.path.join(test_folder_path, "20192020", "team_rosters", "20192020_team6_roster.json"))
        mod_time_team20 = os.path.getmtime(os.path.join(test_folder_path, "20202021", "team_rosters", "20202021_team20_roster.json"))

        self.assertTrue(statsapi_downloader.download_team_rosters_data(test_folder_path, 2018, 2020, overwrite=True))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20182019", "team_rosters", "20182019_team1_roster.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20192020", "team_rosters", "20192020_team6_roster.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "20202021", "team_rosters", "20202021_team20_roster.json")))

        new_mod_time_team1  = os.path.getmtime(os.path.join(test_folder_path, "20182019", "team_rosters", "20182019_team1_roster.json"))
        new_mod_time_team6  = os.path.getmtime(os.path.join(test_folder_path, "20192020", "team_rosters", "20192020_team6_roster.json"))
        new_mod_time_team20 = os.path.getmtime(os.path.join(test_folder_path, "20202021", "team_rosters", "20202021_team20_roster.json"))
        self.assertGreater(new_mod_time_team1, mod_time_team1)
        self.assertGreater(new_mod_time_team6, mod_time_team6)
        self.assertGreater(new_mod_time_team20, mod_time_team20)

        # Test same starting and end year
        # - Check return is valid
        self.assertTrue(statsapi_downloader.download_team_rosters_data(test_folder_path, 2020, 2020))

        # Test invalid start/end years
        # - Check false return
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 2015.1, 2020))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 2015, 2020.0))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 2021, 2020))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, "2020", "2021"))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, "2020.0", "2021.1"))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, "2020", "abc"))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, "efg", "2021"))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, None, 2021))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 2021, None))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, [2020], [2021]))

        # Test access before NHL founding year
        # - Check false return
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, "1916", 2021))
        self.assertFalse(statsapi_downloader.download_team_rosters_data(test_folder_path, 1916, 2021))

    def _create_empty_file(self, file_path):
        """ Helper function to simply create an empty file. """
        with open(file_path, 'w') as f:
            pass

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._root_folder_path)