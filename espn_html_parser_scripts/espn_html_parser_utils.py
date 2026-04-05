#!/usr/bin/env python
""" Common utilities file used between various ESPN scripts. """
import os
import re

def parse_draft_metadata_from_player_str(player_str):
    """ Helper function that parses metadata combined into the player name string.
        Input format: "<First Name> <Last Name> <Team>, <Position>".
        Returns a dictionary containing player metadata.

        Example: "Sidney Crosby Pit, C"
        {'Player': "Sidney Crosby", 'Team': "Pit", 'Positon': "C"}
    """
    re_pattern = r"[\W\w]+ [\W\w]+ ([\w]+|), [\w]+"
    player_dict = {'Player': "", 'Team': "", 'Position': ""}

    # Check if input is string
    if not isinstance(player_str, str):
        return player_dict

    # Check if string matches pattern
    if not re.match(re_pattern, player_str):
        return player_dict

    # Split string based on comma first
    # Example: "Sidney Crosby Pit, C" becomes "Sidney Crosby Pit" and " C"
    string_parts = player_str.split(",")

    # Parse player name and team part
    # Assumes last part is the team abbreviation and the parts in front is the name
    player_name_team_parts = string_parts[0].split(" ")
    player_dict['Player'] = " ".join(player_name_team_parts[i] for i in range(len(player_name_team_parts) -1))
    player_dict['Team'] = player_name_team_parts[len(player_name_team_parts) -1]

    # Player position is just the part after the comma without spaces
    player_dict['Position'] = string_parts[1].strip()

    return player_dict

def check_html(html_path):
    """ Helper function to check if input is a valid HTML file. """
    if (not isinstance(html_path, str) or
        not html_path.lower().endswith(".html") or
        not os.path.exists(html_path)):
        return False

    return True

def sub_special_chars(input_str):
    """ Helper function to strip special characters and replace them with an underscore. """
    # Add special character regex as needed - regex pattern contain characters to replace.
    # Returns original input if no characters are found to need replacing.
    if not isinstance(input_str, str):
        return input_str

    # Note: \\ delimits \
    # Note: \" delimits "
    # Set contains special characters that can't be used in file names
    return re.sub(r"[\\/:*?\"<>|]", "_", input_str)