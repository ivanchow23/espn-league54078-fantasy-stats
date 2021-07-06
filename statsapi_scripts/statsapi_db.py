#!/usr/bin/env python
""" Module for building database used for easier access of data from statsapi. """
import argparse
import csv
import os
import sqlite3
import statsapi_utils
import statsapi_logger

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DEFAULT_DATABASE_PATH = os.path.join(SCRIPT_DIR, "statsapi.db")
logger = statsapi_logger.logger()

def create_db(db_path):
    """ Creates a database file. """
    # Connect to database
    conn = _connect_db(db_path, create_new=True)
    if not conn:
        logger.error(f"Could not connect to database: {db_path}")
        return False
    logger.info(f"Creating database file...")
    logger.info(f"Connected to: {db_path}")

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

def update_teams_table(db_path):
    """ Updates a table within a database of team information from statsapi.
        Directly fetches teams data from statsapi website. Overwrites data if
        team information already exists in table. """
    # Connect to database
    conn = _connect_db(db_path)
    if not conn:
        logger.warning(f"Could not connect to database: {db_path}")
        return False
    logger.info("Updating teams table...")
    logger.info(f"Connected to: {db_path}")

    # Get cursor for database
    cur = conn.cursor()

    # Load teams data from server
    teams_dict = statsapi_utils.load_json_from_url(statsapi_utils.URL_STRING_API_PREFIX + "/teams")
    if not teams_dict:
        logger.error(f"Could not load data to update teams table.")
        return False

    # Get list of dictionaries of teams
    teams_dicts_list = teams_dict['teams']
    for team_dict in teams_dicts_list:
        id = team_dict['id']
        name = team_dict['name']
        abbrev = team_dict['abbreviation']
        link = team_dict['link']

        logger.info(f"Updating team entry: {name} (ID: {id})")
        execute_str = "INSERT or REPLACE INTO teams VALUES (:id, :name, :abbreviation, :link)"
        conn.execute(execute_str, {'id': id, 'name': name, 'abbreviation': abbrev, 'link': link})
        conn.commit()

    conn.close()
    return True

def update_players_table(db_path, input_file):
    """ Updates a table within a database of player information from statsapi.
        Requires the teams table to be populated in the database so it can
        access roster data, which is then used to retrieve player links.
        Overwrites data if player information already exists in table.

        This function performs the general steps to retrieve player links:
            1. Get team the player played for in a given season.
            2. Get team roster for the given season.
            3. Find player on that roster, which should contain a player link.
            4. Use player link to access player info. In our case, we want to
               store the link and other information if needed in our database.

        Input file is a CSV formatted file with the following info:

        Player Name,        Team,     Year
        Sidney Crosby,      PIT,      20182019
        Connor McDavid,     EDM,      20202021
        Auston Matthews,    TOR,      20160217
    """
    # Input file check
    if not _check_csv_path(input_file):
        logger.error(f"Cannot open {input_file}")
        return False

    # Read input file as CSV
    with open(input_file, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        if not reader:
            logger.error(f"Input CSV {input_file} is empty.")
            return False

        # Check required headers exist
        headers = reader.fieldnames
        required_headers = ['Player Name', 'Team', 'Year']
        if not headers or not set(required_headers).issubset(set(headers)):
            logger.error(f"Input CSV require headers: {required_headers}")
            return False

        # Connect to database
        conn = _connect_db(db_path)
        if not conn:
            logger.error(f"Could not connect to database: {db_path}")
            return False
        logger.info("Updating players table...")
        logger.info(f"Connected to: {db_path}")

        # Get cursor for database
        cur = conn.cursor()

        # Iterate through each row in file
        for row in reader:
            player_name = row['Player Name']
            team_abbrev = row['Team']
            year_string = row['Year']

            # Look up link from teams table
            execute_str = f"SELECT link from teams WHERE abbreviation='{team_abbrev}'"
            logger.debug(f"Executing: {execute_str}")
            cur.execute(execute_str)

            # Attempt to find team link from database
            link_ret = cur.fetchone()
            if not link_ret:
                logger.warning(f"Could not find team link for: {player_name} {team_abbrev} {year_string}")
                continue

            # Load team roster data given the link and year
            # This link should have the form: https://statsapi.web.nhl.com/api/v1/teams/20?expand=team.roster&season=20122013
            # TODO: Optimization - Look for players on the same team and season to load team roster season information just once
            # TODO: Logic currently requires access to server every time. Ideally, figure out if an entry already exists in the
            #       database to skip this step. But would also need to handle if two players share the same name.
            team_link = link_ret[0]
            team_roster_season_link = f"{statsapi_utils.URL_STRING}{team_link}?expand=team.roster&season={year_string}"
            team_roster_season_json = statsapi_utils.load_json_from_url(team_roster_season_link)
            if not team_roster_season_json:
                logger.warning(f"Could not access team roster season data for: {player_name} {team_abbrev} {year_string}")
                continue

            # Attempt to find player in list of roster dictionaries
            try:
                roster_dicts = team_roster_season_json['teams'][0]['roster']['roster']
                player_dict = next((p_dict['person'] for p_dict in roster_dicts if p_dict['person']['fullName'] == player_name), None)
                if not player_dict:
                    logger.warning(f"Could not find player data for: {player_name} {team_abbrev} {year_string}")
                    continue
            except KeyError:
                logger.warning(f"Could not access team roster or player data for: {player_name} {team_abbrev} {year_string}")
                continue

            # Insert into table
            id = player_dict['id']
            name = player_dict['fullName']
            link = player_dict['link']

            logger.info(f"Updating player entry: {player_dict['fullName']} (ID: {player_dict['id']})")
            execute_str = "INSERT or REPLACE INTO players VALUES (:id, :name, :link)"
            conn.execute(execute_str, {'id': id, 'name': name, 'link': link})
            conn.commit()

        return True

def _connect_db(db_path, create_new=False):
    """ Helper function for connecting to the given database. Handles exceptions.
        Use create_new=True to create a new database if it doesn't exist. Otherwise,
        set default False to ensure database must already exist before connecting.
        Returns connection handle if successful. None otherwise. """
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

def _check_csv_path(file_path):
    """ Helper function to check validity of supplied CSV file path. """
    # Check string input
    if not isinstance(file_path, str):
        return False

    # Input file check
    if not os.path.exists(file_path):
        return False

    # File extension check
    if not file_path.endswith(".csv"):
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
        execute_str = f"CREATE TABLE {table_name} (id integer PRIMARY KEY,"
        for col_name, data_type in col_dict.items():
            execute_str += f"{col_name} {data_type},"

        # Remove trailing comma from string after columns are built
        execute_str = execute_str[:-1]
        execute_str += ")"
        logger.debug(f"Executing: {execute_str}")
        cur.execute(execute_str)
        logger.info(f"Created table {table_name}")

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
                execute_str = f"ALTER TABLE {table_name} ADD COLUMN '{col_name}' '{data_type}'"
                logger.debug(f"Executing: {execute_str}")
                cur.execute(execute_str)
                logger.info(f"Added column {col_name} to table {table_name}")

        # Remove columns from table if needed
        # TODO: Intentionally not supported right now
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
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument('-i', required=False, help="Input players CSV file to update statsapi players table in database.")
    args = arg_parser.parse_args()
    input_players_csv = args.i

    if not os.path.exists(DEFAULT_DATABASE_PATH):
        create_db(DEFAULT_DATABASE_PATH)
        update_teams_table(DEFAULT_DATABASE_PATH)

    update_players_table(DEFAULT_DATABASE_PATH, input_players_csv)