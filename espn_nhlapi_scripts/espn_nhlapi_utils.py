""" Utilities for ESPN and nhlapi functionality. """
from unidecode import unidecode

# ESPN to statsapi teams abbreviation mapping
# Key = ESPN abbreivation, Value = nhlapi abbreviation
ESPN_NHLAPI_TEAM_ABBREV_MAP = { "Ana": "ANA", "Ari": "ARI", "Bos": "BOS", "Buf": "BUF", "Cgy": "CGY", "Car": "CAR",
                                "Chi": "CHI", "Col": "COL", "Cls": "CBJ", "Dal": "DAL", "Det": "DET", "Edm": "EDM",
                                "Fla": "FLA", "LA":  "LAK", "Min": "MIN", "Mon": "MTL", "Nsh": "NSH", "NJ":  "NJD",
                                "NYI": "NYI", "NYR": "NYR", "Ott": "OTT", "Phi": "PHI", "Pit": "PIT", "Sea": "SEA",
                                "SJ":  "SJS", "StL": "STL", "TB":  "TBL", "Tor": "TOR", "Utah": "UTA", "Van": "VAN",
                                "Vgk": "VGK", "Vgs": "VGK", "Wsh": "WSH", "Wpg": "WPG" }

def espn_to_nhlapi_team_abbrev(espn_abbrev):
    """ Returns the nhlapi team abbreviation string given an ESPN team abbreivation string.
        Returns an empty string if mapping cannot be found. """
    return ESPN_NHLAPI_TEAM_ABBREV_MAP.get(espn_abbrev, "")

def player_name_is_close_match(player_name1, player_name2):
    """ Checks if two given player names are a close enough match. Function is meant
        to be used to combine datasets where player names are represented differntly.
        Ex: "T.J. Brodie" vs. "TJ Brodie" or "Mike Cammalleri" vs. "Michael Cammalleri" """
    # Normalize ascii characters first to remove any accented characters
    player_firstname1 = unidecode(player_name1.split(" ", 1)[0])
    player_lastname1 = unidecode(player_name1.split(" ", 1)[1])
    player_firstname2 = unidecode(player_name2.split(" ", 1)[0])
    player_lastname2 = unidecode(player_name2.split(" ", 1)[1])

    # Check 1: Last names
    # Instant fail if they do not match
    if player_lastname1 != player_lastname2:
        return False

    # Check 2: Different first letter of first name
    # Instant fail if they do not match
    if player_firstname1[0] != player_firstname2[0]:
        return False

    # Check 3: Abbreviated first names (ex: "T.J." vs. "TJ")
    # Instant pass if they do match (because last name check also passed)
    if player_firstname1.replace(".", "") == player_firstname2.replace(".", ""):
        return True

    # Check 4: Shortened names (ex: "Mitchell" vs. "Mitch")
    if player_firstname1 in player_firstname2 or player_firstname2 in player_firstname1:
        return True

    # Check 5: Hardcoded list of names that I don't know how else to handle
    if _check_list_of_equivalent_names(player_firstname1, player_firstname2):
        return True

    # No match up to this point
    return False

def _check_list_of_equivalent_names(player_name1, player_name2):
    """ Checks if names are "equivalent" against a hardcoded list of names. """
    equivalent_names_list = {'Mike': "Michael",
                             'Matt': "Mathew"}

    for name1, name2 in equivalent_names_list.items():
        if (player_name1 == name1 and player_name2 == name2) or (player_name2 == name1 and player_name1 == name2):
            return True

    return False