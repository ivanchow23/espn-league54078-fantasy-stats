#!/usr/bin/env python
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
        if not os.path.exists(TEST_DIR):
            os.mkdir(TEST_DIR)

        self._test_db_path = os.path.join(TEST_DIR, "unittest.db")
        self._create_db(self._test_db_path)

    def test_create_db(self):
        """ Test functionality of creating a new local database. """
        # Test typical use-case
        # Check table columns match test case
        db_path = os.path.join(TEST_DIR, "test.db")
        self.assertTrue(statsapi_db.create_db(db_path))

        expected_table_cols = self._get_table_cols(self._test_db_path, "teams")
        actual_table_cols = self._get_table_cols(db_path, "teams")
        self.assertEqual(expected_table_cols, actual_table_cols)

        expected_table_cols = self._get_table_cols(self._test_db_path, "players")
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

    def _create_db(self, db_path):
        """ Very simple helper function to generate a database file for testing.
            Test database requires dual maintenance with implementation to be
            most updated with tests. """
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("CREATE TABLE teams (id integer PRIMARY KEY, name text, abbreviation text, link text)")
        conn.commit()
        cur.execute("CREATE TABLE players (id integer PRIMARY KEY, name text, link text)")
        conn.commit()
        conn.close()

    def _get_table_cols(self, db_path, table_name):
        """ Helper function to get list of table columns. """
        cur = self._connect_db(db_path)
        cur.execute(f"SELECT * from {table_name}")
        return [d[0] for d in cur.description]

    def _connect_db(self, db_path):
        """ Very simple helper function to connect to a database. Returns a cursor. """
        conn = sqlite3.connect(db_path)
        return conn.cursor()

    def _rm_file(self, file):
        """ Helper function to remove a file. Does nothing if it doesn't exist. """
        try:
            os.remove(file)
        except:
            pass

    def tearDown(self):
        """ Remove any items. """
        shutil.rmtree(TEST_DIR)