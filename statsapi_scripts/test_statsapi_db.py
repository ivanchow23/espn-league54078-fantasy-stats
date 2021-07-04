#!/usr/bin/env python
import csv
import os
import shutil
import sqlite3
import statsapi_db
import unittest

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
TEST_DIR = os.path.join(SCRIPT_DIR, "test_statsapi_db")

class TestStatsApiDb(unittest.TestCase):
    def setUp(self):
        """ Set-up required items. """
        # Make new test directory
        if os.path.exists(TEST_DIR):
            shutil.rmtree(TEST_DIR)
        os.mkdir(TEST_DIR)

        # Test database
        self._test_db_path = os.path.join(TEST_DIR, "unittest.db")
        self._create_db(self._test_db_path)

        # Test player input file
        self._test_player_input_file = os.path.join(TEST_DIR, "unittest_players.csv")

    def test_create_db(self):
        """ Test functionality of creating a new local database. """
        # Test typical use-case
        # Check table columns match test case
        db_path = os.path.join(TEST_DIR, "test.db")
        self.assertTrue(statsapi_db.create_db(db_path))

        expected_table_cols = ['id', 'name', 'abbreviation', 'link']
        actual_table_cols = self._get_table_cols(db_path, "teams")
        self.assertEqual(expected_table_cols, actual_table_cols)

        expected_table_cols = ['id', 'name', 'link']
        actual_table_cols = self._get_table_cols(db_path, "players")
        self.assertEqual(expected_table_cols, actual_table_cols)

        # Test invalid database file paths
        db_path = "invaliddb"
        self.assertFalse(statsapi_db.create_db(db_path))

        # Test invalid database file paths
        db_path = "invalid_db.d"
        self.assertFalse(statsapi_db.create_db(db_path))

        # Test invalid database file paths
        db_path = 123
        self.assertFalse(statsapi_db.create_db(db_path))

        # Test invalid database file paths
        db_path = os.path.join(SCRIPT_DIR, "test.d")
        self.assertFalse(statsapi_db.create_db(db_path))

        # Test invalid database file paths
        db_path = os.path.join(SCRIPT_DIR, "?", "test.db")
        self.assertFalse(statsapi_db.create_db(db_path))

        # Test invalid database file paths
        db_path = "this/is/not/a/path/test.db"
        self.assertFalse(statsapi_db.create_db(db_path))

    def test_update_teams_table(self):
        """ Test functionality of updating teams table in the database. """
        # Test typical use-case
        db_path = os.path.join(TEST_DIR, "test.db")
        statsapi_db.create_db(db_path)
        self.assertTrue(statsapi_db.update_teams_table(db_path))

        # Connect to the database
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Test certain entries exist
        cur.execute("SELECT * FROM teams WHERE name='New Jersey Devils'")
        actual_ret = cur.fetchone()
        expected_ret = (1, 'New Jersey Devils', 'NJD', '/api/v1/teams/1')
        self.assertEqual(expected_ret, actual_ret)

        cur.execute("SELECT * FROM teams WHERE abbreviation='MTL'")
        actual_ret = cur.fetchone()
        expected_ret = (8, 'Montréal Canadiens', 'MTL', '/api/v1/teams/8')
        self.assertEqual(expected_ret, actual_ret)

        cur.execute("SELECT * FROM teams WHERE link='/api/v1/teams/55'")
        actual_ret = cur.fetchone()
        expected_ret = (55, 'Seattle Kraken', 'SEA', '/api/v1/teams/55')
        self.assertEqual(expected_ret, actual_ret)

        conn.close()

    def test_update_players_table(self):
        """ Test functionality of updating teams table in the database. """
        # Test typical case
        self._write_csv(self._test_player_input_file,
                        headers=['Player Name', 'Team', 'Year'],
                        dict_list=[{'Player Name': "Martin Brodeur", 'Team': "NJD", 'Year': "20122013"},
                                   {'Player Name': "Sidney Crosby", 'Team': "PIT", 'Year': "20182019"},
                                   {'Player Name': "Nathan MacKinnon", 'Team': "COL", 'Year': "20202021"}])

        # Check proper return on function call
        self.assertTrue(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Check expected entries are updated in the database
        # Note: Querying returns entries sorted by primary key, which is the ID
        expected_ret = [(8455710, "Martin Brodeur", "/api/v1/people/8455710"),
                        (8471675, "Sidney Crosby", "/api/v1/people/8471675"),
                        (8477492, "Nathan MacKinnon", "/api/v1/people/8477492")]

        actual_ret = self._get_all_player_entries(self._test_db_path)
        self.assertEqual(expected_ret, actual_ret)

        # Test extra input file headers
        self._write_csv(self._test_player_input_file,
                        headers=['Player Name', 'Team', 'Year', 'Extra'],
                        dict_list=[{'Player Name': "Martin Brodeur", 'Team': "NJD", 'Year': "20122013", 'Extra': 123},
                                   {'Player Name': "Sidney Crosby", 'Team': "PIT", 'Year': "20182019", 'Extra': 123},
                                   {'Player Name': "Nathan MacKinnon", 'Team': "COL", 'Year': "20202021", 'Extra': 123}])

        # Check proper return on function call
        self.assertTrue(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Check expected entries are updated in the database
        # Note: Querying returns entries sorted by primary key, which is the ID
        expected_ret = [(8455710, "Martin Brodeur", "/api/v1/people/8455710"),
                        (8471675, "Sidney Crosby", "/api/v1/people/8471675"),
                        (8477492, "Nathan MacKinnon", "/api/v1/people/8477492")]

        actual_ret = self._get_all_player_entries(self._test_db_path)
        self.assertEqual(expected_ret, actual_ret)

        # Test new entry
        self._write_csv(self._test_player_input_file,
                        headers=['Player Name', 'Team', 'Year'],
                        dict_list=[{'Player Name': "Alex Ovechkin", 'Team': "WSH", 'Year': "20142015"}])

        # Check proper return on function call
        self.assertTrue(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Check expected entries are updated in the database
        # Note: Querying returns entries sorted by primary key, which is the ID
        expected_ret = [(8455710, "Martin Brodeur", "/api/v1/people/8455710"),
                        (8471214, "Alex Ovechkin", "/api/v1/people/8471214"),
                        (8471675, "Sidney Crosby", "/api/v1/people/8471675"),
                        (8477492, "Nathan MacKinnon", "/api/v1/people/8477492")]

        actual_ret = self._get_all_player_entries(self._test_db_path)
        self.assertEqual(expected_ret, actual_ret)

        # Test:
        # - Player does not exist for a given roster
        # - Invalid team
        # - Invalid year
        self._write_csv(self._test_player_input_file,
                        headers=['Player Name', 'Team', 'Year'],
                        dict_list=[{'Player Name': "Invalid Player", 'Team': "WSH", 'Year': "20142015"},
                                   {'Player Name': "Sidney Crosby", 'Team': "AAA", 'Year': "20172018"},
                                   {'Player Name': "Evgeni Malkin", 'Team': "PIT", 'Year': "11111112"}])

        # Check proper return on function call
        self.assertTrue(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Check expected entries are updated in the database - Expect no change from last test
        # Despite invalid inputs, expect function to continue rather than crash
        # Note: Querying returns entries sorted by primary key, which is the ID
        expected_ret = [(8455710, "Martin Brodeur", "/api/v1/people/8455710"),
                        (8471214, "Alex Ovechkin", "/api/v1/people/8471214"),
                        (8471675, "Sidney Crosby", "/api/v1/people/8471675"),
                        (8477492, "Nathan MacKinnon", "/api/v1/people/8477492")]

        actual_ret = self._get_all_player_entries(self._test_db_path)
        self.assertEqual(expected_ret, actual_ret)

        # Test missing input file headers
        self._write_csv(self._test_player_input_file,
                        headers=['Player Name', 'Year'],
                        dict_list=[{'Player Name': "Martin Brodeur", 'Year': "20122013"},
                                   {'Player Name': "Sidney Crosby", 'Year': "20182019"},
                                   {'Player Name': "Nathan MacKinnon", 'Year': "20202021"}])
        self.assertFalse(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Test missing input file headers
        self._write_csv(self._test_player_input_file,
                        headers=['Player', 'Year'],
                        dict_list=[{'Player': "Martin Brodeur", 'Year': "20122013"},
                                   {'Player': "Sidney Crosby", 'Year': "20182019"},
                                   {'Player': "Nathan MacKinnon", 'Year': "20202021"}])
        self.assertFalse(statsapi_db.update_players_table(self._test_db_path, self._test_player_input_file))

        # Test empty input file
        with open(os.path.join(TEST_DIR, "empty.csv"), 'w') as f:
            input_file_path = os.path.join(TEST_DIR, "empty.csv")
            self.assertFalse(statsapi_db.update_players_table(self._test_db_path, input_file_path))

        # Test invalid input file
        input_file_path = "invalid/path/to/file.csv"
        self.assertFalse(statsapi_db.update_players_table(self._test_db_path, input_file_path))

        # Test invalid input file
        input_file_path = 123
        self.assertFalse(statsapi_db.update_players_table(self._test_db_path, input_file_path))

        # Test invalid input file
        input_file_path = None
        self.assertFalse(statsapi_db.update_players_table(self._test_db_path, input_file_path))

        # Test invalid input file
        with open(os.path.join(TEST_DIR, "not_a_csv.txt"), 'w') as f:
            input_file_path = os.path.join(TEST_DIR, "not_a_csv.txt")
            self.assertFalse(statsapi_db.update_players_table(self._test_db_path, input_file_path))

    def _create_db(self, db_path):
        """ Very simple helper function to generate a database file for testing.
            Test database requires dual maintenance with implementation to be
            most updated with tests. """
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Create tables
        cur.execute("CREATE TABLE teams (id integer PRIMARY KEY, name text, abbreviation text, link text)")
        conn.commit()
        cur.execute("CREATE TABLE players (id integer PRIMARY KEY, name text, link text)")
        conn.commit()

        # Insert some known data into teams table
        cur.execute("INSERT INTO teams VALUES (?, ?, ?, ?)", (1, "New Jersey Devils", "NJD", "/api/v1/teams/1"))
        conn.commit()
        cur.execute("INSERT INTO teams VALUES (?, ?, ?, ?)", (5, "Pittsburgh Penguins", "PIT", "/api/v1/teams/5"))
        conn.commit()
        cur.execute("INSERT INTO teams VALUES (?, ?, ?, ?)", (15, "Washington Capitals", "WSH", "/api/v1/teams/15"))
        conn.commit()
        cur.execute("INSERT INTO teams VALUES (?, ?, ?, ?)", (21, "Colorado Avalanche", "COL", "/api/v1/teams/21"))
        conn.commit()

        conn.close()

    def _get_table_cols(self, db_path, table_name):
        """ Helper function to get list of table columns. """
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute(f"SELECT * from {table_name}")
        conn.close()
        return [d[0] for d in cur.description]

    def _get_all_player_entries(self, db_path):
        """ Helper function to retrieve all entries from the players table. """
        conn = sqlite3.connect(self._test_db_path)
        cur = conn.cursor()
        cur.execute("SELECT * FROM players")
        ret = cur.fetchall()
        conn.close()
        return ret

    def _write_csv(self, csv_path, headers, dict_list):
        """ Very simple helper function to write list of dictionaries to CSV.
            Uses CSV DictWriter implementation. """
        with open(csv_path, 'w') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=headers)
            writer.writeheader()
            for row in dict_list:
                writer.writerow(row)

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(TEST_DIR)