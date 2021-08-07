#!/usr/bin/env python
""" ESPN to statsapi utilities. """

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