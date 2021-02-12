#!/usr/bin/env python
""" Common utilities file used between various ESPN scripts. """
import re

# Expected file name patterns
FILE_NAME_RE_FORMAT_CLUBHOUSE      = r"[\W\w]+ Clubhouse - [\W\w]+ - ESPN Fantasy Hockey"
FILE_NAME_RE_FORMAT_DRAFT_RECAP    = r"Draft Recap - [\W\w]+ - ESPN Fantasy Hockey"
FILE_NAME_RE_FORMAT_LEAGUE_ROSTERS = r"League Rosters - [\W\w]+ - ESPN Fantasy Hockey"

# List of position designations
POSITIONS_LIST = ["D, F", "D", "F", "G"]

# List of detailed positions designations
DETAILED_POSITIONS_LIST = ["LW", "RW", "C", "D", "G"]

# List of NHL team abbreviations found in various ESPN HTML pages
NHL_TEAM_ABBREVIATIONS_LIST = ["Ana", "Ari", "Bos", "Buf", "Cgy", "Car", "Chi", "Col", "Cls", "Dal", "Det", "Edm",
                               "Fla", "LA",  "Min", "Mon", "Nsh", "NJ",  "NYI", "NYR", "Ott", "Phi", "Pit", "SJ",
                               "StL", "TB",  "Tor", "Van", "Vgs", "Wsh", "Wpg"]

# List of injury designations found in various ESPN HTML pages
INJURY_DESIGNATION_LIST = ["IR", "O", "DTD", "D", "Q", "P"]

def parse_draft_metadata_from_player_str(player_str):
    """ Helper function that parses metadata combined into the player name string.
        Input format: "<First Name> <Last Name> <Team>, <Position>".
        Returns a dictionary containing player metadata.

        Example: "Sidney Crosby Pit, C"
        {'Player': "Sidney Crosby", 'Team': "Pit", 'Positon': "C"}
    """
    re_pattern = r"[\W\w]+ [\W\w]+ [\w]+, [\w]+"
    player_dict = {'Player': "", 'Team': "", 'Position': ""}

    # Check if input is string
    if not isinstance(player_str, str):
        return player_dict

    # Check if string matches pattern
    if not re.match(re_pattern, player_str):
        return player_dict

    # Parse for position
    for pos in DETAILED_POSITIONS_LIST:
        if player_str.endswith(", " + pos):
            player_dict['Position'] = pos
            player_str = player_str[:len(player_str) - len(", ") - len(pos)]
            break

    # Parse for team abbreviation
    for team in NHL_TEAM_ABBREVIATIONS_LIST:
        if player_str.endswith(team):
            player_dict['Team'] = team
            player_str = player_str[:len(player_str) - len(" ") - len(team)]
            break

    # We should just be left with player name here
    player_dict['Player'] = player_str
    return player_dict

def parse_metadata_from_player_str(player_str):
    """ Helper function that parses metadata cobined into the player name string.
        Input format: "<First Name> <Last Name>"<Injury Designation><Team><Position>".
        Returns a dictionary containing player metadata.

        Example: "Steven StamkosOTBF"
        {'Player': "Steven Stamkos", 'Injury Designation': "O", 'Team': "TB", 'Positon': "F"}
    """
    player_dict = {'Player': "", 'Injury Designation': "", 'Team': "", 'Position': ""}

    # Check if input is string
    if not isinstance(player_str, str):
        return player_dict

    # Handle special case where the player name is literally empty
    if player_str == "Empty":
        return player_dict

    # First, parse last letter that indicates player's position
    # Handle special case where a player is eligible for multiple positions
    for pos in POSITIONS_LIST:
        if player_str.endswith(pos):
            # Handle special case where a player is eligible for multiple positions
            if pos == "D, F":
                player_dict['Position'] = "D/F"
            # Otherwise, simple case where position matches
            else:
                player_dict['Position'] = pos

            player_str = player_str[:len(player_str) - len(pos)]
            break

    # Parse for team abbreviation
    for team in NHL_TEAM_ABBREVIATIONS_LIST:
        if player_str.endswith(team):
            player_dict['Team'] = team
            player_str = player_str[:len(player_str) - len(team)]
            break

    # Parse for injury designation
    for status in INJURY_DESIGNATION_LIST:
        if player_str.endswith(status):
            player_dict['Injury Designation'] = status
            player_str = player_str[:len(player_str) - len(status)]
            break

    # We should just be left with player name here
    player_dict['Player'] = player_str
    return player_dict