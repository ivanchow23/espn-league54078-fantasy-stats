#!/usr/bin/env python
""" ESPN to statsapi utilities. """
import csv
import os

# ESPN to statsapi teams abbreviation mapping
# Key = ESPN abbreivation, Value = statsapi abbreviation
ESPN_STATSAPI_TEAM_ABBREV_MAP = { "Ana": "ANA", "Ari": "ARI", "Bos": "BOS", "Buf": "BUF", "Cgy": "CGY", "Car": "CAR",
                                  "Chi": "CHI", "Col": "COL", "Cls": "CBJ", "Dal": "DAL", "Det": "DET", "Edm": "EDM",
                                  "Fla": "FLA", "LA":  "LAK", "Min": "MIN", "Mon": "MTL", "Nsh": "NSH", "NJ":  "NJD",
                                  "NYI": "NYI", "NYR": "NYR", "Ott": "OTT", "Phi": "PHI", "Pit": "PIT", "Sea": "SEA",
                                  "SJ":  "SJS", "StL": "STL", "TB":  "TBL", "Tor": "TOR", "Van": "VAN", "Vgs": "VGK",
                                  "Wsh": "WSH", "Wpg": "WPG" }

# statsapi to ESPN teams abbreviaion mapping (Inverse of ESPN to statsapi teams mapping)
# Key = statsapi abbreviation, Value = ESPN abbreviation
STATSAPI_ESPN_TEAM_ABBREV_MAP = {val: key for key, val in ESPN_STATSAPI_TEAM_ABBREV_MAP.items()}

def statsapi_team_abbrev(espn_abbrev):
    """ Returns the statsapi team abbreviation string given an ESPN team abbreivation string.
        Returns an empty string if mapping cannot be found. """
    if not _is_string(espn_abbrev):
        return ""

    try:
        return ESPN_STATSAPI_TEAM_ABBREV_MAP[espn_abbrev]
    except KeyError:
        return ""

def espn_team_abbrev(statsapi_abbrev):
    """ Returns the ESPN team abbreviation string given a statsapi team abbreivation string.
        Returns an empty string if mapping cannot be found. """
    if not _is_string(statsapi_abbrev):
        return ""

    try:
        return STATSAPI_ESPN_TEAM_ABBREV_MAP[statsapi_abbrev]
    except KeyError:
        return ""

def _is_string(string):
    """ Helper function to check if input is a string type. """
    if not string:
        return False

    if not isinstance(string, str):
        return False

    return True

class CorrectionUtil():
    """ Generic class for reading in a file which is used to apply naming corrections. """
    def __init__(self, correction_file_path):
        """ Reads in a correction file and stores it internally.
            File is a CSV file with original and corrected information.
            Must contain headers described in class. """
        # Valid flag used publicly and internally to check if instance is valid
        self.valid = True

        # Required headers in file
        self._required_headers = ["Player", "Team", "Corrected Player", "Corrected Team"]

        # Load data and store
        self._data_dict = self._read_file(correction_file_path)

        # If data is not valid, something went wrong
        # Set flag to indicate instance is not valid for whatever reason
        if not self._data_dict:
            self.valid = False

    def get_corrected_dict(self, player_name, team):
        """ Returns a dictionary of corrected names and information given the input.
            Returns None if no correction entries are found. """
        if self.valid:
            for data_dict in self._data_dict:
                if data_dict['Player'] == player_name and data_dict['Team'] == team:
                    return {k: data_dict[k] for k in ['Corrected Player', 'Corrected Team'] if k in data_dict}
        return None

    def _read_file(self, file_path):
        """ Reads in CSV file with error checking. Returns list of dictionaries
            if successful. None otherwise. """
        # Error check
        if (not _is_string(file_path) or
            not file_path.endswith(".csv") or
            not os.path.exists(file_path)):
            return None

        # Read file
        with open(file_path, 'r') as csv_file:
            # File headers must contain the required headers
            dict_reader = csv.DictReader(csv_file)
            headers = dict_reader.fieldnames
            if not set(self._required_headers).issubset(set(headers)):
                return None

            # Return loaded data
            return list(dict_reader)

        return None