#!/usr/bin/env python
import os
import pandas as pd
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

    def test_download_players_data(self):
        """ Tests functionality to download players data. """
        # Create root folder for this test
        test_folder_path = os.path.join(self._root_folder_path, "test_download_players_data_root")
        os.mkdir(test_folder_path)

        # Test typical case
        test_input_file_path = os.path.join(test_folder_path, "test_input_file.csv")
        self._write_csv(test_input_file_path, [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/8470612"},
                                               {'Player': "Sidney Crosby", 'statsapi_endpoint': "/api/v1/people/8471675"},
                                               {'Player': "Connor McDavid", 'statsapi_endpoint': "/api/v1/people/8478402"}])
        self.assertTrue(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))

        # - Check expected files exist
        # - Check mapfile exists
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8470612.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8471675.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8478402.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # - Check mapfile contents
        expected_mapfile_data = [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/8470612", 'id': 8470612},
                                 {'Player': "Sidney Crosby", 'statsapi_endpoint': "/api/v1/people/8471675", 'id': 8471675},
                                 {'Player': "Connor McDavid", 'statsapi_endpoint': "/api/v1/people/8478402", 'id': 8478402}]
        actual_mapfile_data = pd.read_csv(os.path.join(test_folder_path, "players_id_map.csv")).to_dict('records')
        self.assertEqual(expected_mapfile_data, actual_mapfile_data)

        # Test typical case again, with no overwrite
        # - First, keep track of modification date from the first test
        mod_time_mapfile = os.path.getmtime(os.path.join(test_folder_path, "players_id_map.csv"))
        mod_time_player8470612 = os.path.getmtime(os.path.join(test_folder_path, "players", "player8470612.json"))
        mod_time_player8471675 = os.path.getmtime(os.path.join(test_folder_path, "players", "player8471675.json"))
        mod_time_player8478402 = os.path.getmtime(os.path.join(test_folder_path, "players", "player8478402.json"))
        self.assertTrue(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))

        # - Check expected files exist
        # - Check mapfile exists
        # - Check mapfile contents (same as previous test)
        # - Check files did not get modified
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8470612.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8471675.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8478402.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))
        self.assertEqual(expected_mapfile_data, actual_mapfile_data)
        self.assertEqual(os.path.getmtime(os.path.join(test_folder_path, "players", "player8470612.json")), mod_time_player8470612)
        self.assertEqual(os.path.getmtime(os.path.join(test_folder_path, "players", "player8471675.json")), mod_time_player8471675)
        self.assertEqual(os.path.getmtime(os.path.join(test_folder_path, "players", "player8478402.json")), mod_time_player8478402)

        # Test typical case again, with overwrite
        # - Check expected files exist
        # - Check mapfile exists
        # - Check mapfile contents (same as previous test)
        # - Check files did not get modified
        self.assertTrue(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path, overwrite=True))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8470612.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8471675.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8478402.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))
        self.assertEqual(expected_mapfile_data, actual_mapfile_data)
        self.assertGreater(os.path.getmtime(os.path.join(test_folder_path, "players", "player8470612.json")), mod_time_player8470612)
        self.assertGreater(os.path.getmtime(os.path.join(test_folder_path, "players", "player8471675.json")), mod_time_player8471675)
        self.assertGreater(os.path.getmtime(os.path.join(test_folder_path, "players", "player8478402.json")), mod_time_player8478402)

        # Test extra input columns
        self._clean_folder(test_folder_path)
        test_input_file_path = os.path.join(test_folder_path, "test_input_file.csv")
        self._write_csv(test_input_file_path, [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/8470612", 'extra': "AAA"},
                                               {'Player': "Sidney Crosby", 'statsapi_endpoint': "/api/v1/people/8471675", 'extra': "AAA"},
                                               {'Player': "Connor McDavid", 'statsapi_endpoint': "/api/v1/people/8478402", 'extra': "AAA"}])
        self.assertTrue(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))

        # - Check expected files exist
        # - Check mapfile exists
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8470612.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8471675.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players", "player8478402.json")))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # - Check mapfile contents
        expected_mapfile_data = [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/8470612", 'extra': "AAA", 'id': 8470612},
                                 {'Player': "Sidney Crosby", 'statsapi_endpoint': "/api/v1/people/8471675", 'extra': "AAA", 'id': 8471675},
                                 {'Player': "Connor McDavid", 'statsapi_endpoint': "/api/v1/people/8478402", 'extra': "AAA", 'id': 8478402}]
        actual_mapfile_data = pd.read_csv(os.path.join(test_folder_path, "players_id_map.csv")).to_dict('records')
        self.assertEqual(expected_mapfile_data, actual_mapfile_data)

        # Test empty input file
        # - Check false return
        self._clean_folder(test_folder_path)
        test_input_file_path = os.path.join(test_folder_path, "test_input_file.csv")
        self._create_empty_file(test_input_file_path)
        self.assertFalse(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))

        # Test invalid root folder paths
        # - Check false return
        # - Check mapfile does not exist
        self._clean_folder(test_folder_path)
        self.assertFalse(statsapi_downloader.download_players_data(None, test_input_file_path))
        self.assertFalse(statsapi_downloader.download_players_data([1, 2, 3], test_input_file_path))
        self.assertFalse(statsapi_downloader.download_players_data(r"?\not\a\valid\path", test_input_file_path))
        self.assertFalse(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # Test invalid input file paths
        # - Check false return
        # - Check mapfile does not exist
        self._clean_folder(test_folder_path)
        self.assertFalse(statsapi_downloader.download_players_data(test_folder_path, None))
        self.assertFalse(statsapi_downloader.download_players_data(test_folder_path, [1, 2, 3]))
        self.assertFalse(statsapi_downloader.download_players_data(test_folder_path, r"not\a\file?"))
        self.assertFalse(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # Test missing required headers
        # - Check false return
        # - Check mapfile does not exist
        self._clean_folder(test_folder_path)
        test_input_file_path = os.path.join(test_folder_path, "test_input_file.csv")
        self._write_csv(test_input_file_path, [{'statsapi_endpoint': "/api/v1/people/8470612"},
                                               {'statsapi_endpoint': "/api/v1/people/8471675"},
                                               {'statsapi_endpoint': "/api/v1/people/8478402"}])
        self.assertFalse(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))
        self.assertFalse(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # Test invalid endpoints
        # - Check true return
        # - Check mapfile exists
        self._clean_folder(test_folder_path)
        test_input_file_path = os.path.join(test_folder_path, "test_input_file.csv")
        self._write_csv(test_input_file_path, [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/abcdefg"},
                                               {'Player': "Connor McDavid", 'statsapi_endpoint': 12345},
                                               {'Player': "Carey Price", 'statsapi_endpoint': None}])
        self.assertTrue(statsapi_downloader.download_players_data(test_folder_path, test_input_file_path))
        self.assertTrue(os.path.exists(os.path.join(test_folder_path, "players_id_map.csv")))

        # - Check mapfile contents, but no valid ID mapping
        # Note: Expected data values are all strings because same column contain mix-and-match of data types
        expected_mapfile_data = [{'Player': "Ryan Getzlaf", 'statsapi_endpoint': "/api/v1/people/abcdefg", 'id': ""},
                                 {'Player': "Connor McDavid", 'statsapi_endpoint': "12345", 'id': ""},
                                 {'Player': "Carey Price", 'statsapi_endpoint': "", 'id': ""}]
        actual_mapfile_data = pd.read_csv(os.path.join(test_folder_path, "players_id_map.csv")).replace(float('nan'), "").to_dict('records')
        self.assertEqual(expected_mapfile_data, actual_mapfile_data)

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

    def _write_csv(self, file_path, dict_list):
        """ Writes a list of dictionaries to CSV. """
        df = pd.DataFrame(dict_list)
        df.to_csv(file_path, index=False)

    def _clean_folder(self, folder_path):
        """ Removes all files/folders in folder path, but does not remove
            folder itself (unlike shutil.rmtree). However, implementation
            is simply to use shutil.rmtree, but then create the folder again."""
        shutil.rmtree(folder_path)
        os.mkdir(folder_path)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(self._root_folder_path)