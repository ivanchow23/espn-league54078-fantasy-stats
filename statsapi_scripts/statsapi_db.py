#!/usr/bin/env python
""" Module for building database used for easier access of data from statsapi. """
import os
import sqlite3
import statsapi_utils
import statsapi_logger

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DATABASE_PATH = os.path.join(SCRIPT_DIR, "statsapi.db")
logger = statsapi_logger.logger()

def create_db(db_path=None):
    """ Creates a database file. """
    # Connect to database
    conn = _connect_db(db_path, create_new=True)
    if not conn:
        logger.warning(f"Could not connect to database: {db_path}")
        return False

    # Get cursor for database
    cur = conn.cursor()

    # Create team information table
    _create_table_if_not_exist(cur, "teams", { 'name': "text",
                                               'abbreviation': "text",
                                               'link': "text" })
    # Create player information table
    _create_table_if_not_exist(cur, "players", { 'name': "text",
                                                 'link': "text" })
    # Close connection
    conn.close()
    return True

def _connect_db(db_path, create_new=False):
    """ Helper function for connecting to the given database. Handles exceptions.
        Use create_new=True to create a new database if it doesn't exist. Otherwise,
        set default False to ensure database must already exist before connecting.
        Returns connection handle if successful. None otherwise. """
    # Default database object path if not supplied
    if db_path is None:
        db_path = DEFAULT_DATABASE_PATH

    # Path check
    if not _check_db_path(db_path, create_new):
        return None

    # Attempt to connect
    conn = None
    try:
        conn = sqlite3.connect(db_path)
    except sqlite3.OperationalError:
        # Intentional pass
        pass

    return conn

def _check_db_path(db_path, create_new=False):
    """ Helper function to check validity of supplied database path. """
    # Check string input
    if not isinstance(db_path, str):
        return False

    # Check URL starts with stats API string
    if not db_path.endswith(".db"):
        return False

    # Skip check if function is looking to create a new if database doesn't exist
    # Otherwise, check database file exists
    if not create_new:
        if not os.path.exists(db_path):
            return False

    return True

def _create_table_if_not_exist(cur, table_name, col_dict):
    """ Helper function for creating a table in the database if it doesn't already exist.
        Compares columns in the table if it exists, and handles adding or removing columns
        as supplied by col_dict. TODO: Removing columns functionality unsupported for now.
        Does not change data types of columns.

        col_dict is a dictionary corresponding to column name and data type.
        Example: col_dict = { 'col1': "text",
                              'col2': "integer",
                              'col3': "real" }
    """
    # First check if table exists
    cur.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table_name}'")
    cur_ret = cur.fetchone()

    # If table doesn't exist, simply create it with the supplied columns
    if cur_ret is None:
        execute_str = f"CREATE TABLE {table_name} ("
        for col_name, data_type in col_dict.items():
            execute_str += f"{col_name} {data_type},"

        # Remove trailing comma from string after columns are built
        execute_str = execute_str[:-1]
        execute_str += ")"
        logger.info(f"Executing: {execute_str}")
        cur.execute(execute_str)

    # If table exists, update column names by:
    # - Dropping columns from the table that don't exist in col_dict
    # - Adding columns into the table if there are new ones in col_dict
    else:
        # Get columns in table that already exist
        cur.execute(f"SELECT * from {table_name}")
        table_cols = [d[0] for d in cur.description]

        # Find columns to add/remove
        cols_to_add = {col: dtype for col, dtype in col_dict.items() if col not in table_cols}
        cols_to_drop = [col for col in table_cols if col not in col_dict]

        logger.debug(f"Adding new columns to table {table_name}: {cols_to_add}")
        logger.debug(f"Dropping columns from table {table_name}: {cols_to_drop}")

        # Add columns to table if needed
        if len(cols_to_add) != 0:
            for col_name, data_type in cols_to_add.items():
                execute_string = f"ALTER TABLE {table_name} ADD COLUMN '{col_name}' '{data_type}'"
                logger.info(f"Executing: {execute_string}")
                cur.execute(execute_string)

        # Remove columns from table if needed
        # TODO: Intentionally not supported right now -
        # ALTER TABLE DROP COLUMN command is only available for sqlite3 versions >= 3.35
        # See: https://stackoverflow.com/a/5987838
        #
        # At the time of writing, was using Python 3.7.5 where sqlite3.version was:
        # import sqlite3
        # >>> sqlite3.sqlite_version
        # '3.28.0'

        # if len(cols_to_drop) != 0:
        #     for col_name in cols_to_drop:
        #         cur.execute(f"ALTER TABLE {table_name} DROP COLUMN '{col_name}'")

if __name__ == "__main__":
    create_db()