#!/usr/bin/env python
""" Various functions to retrieve hockey data from statsapi. """
import statsapi_utils
from statsapi_utils import URL_STRING

def save_teams_data():
    """ Saves data for each team. """
    statsapi_utils.save_json_from_url(_get_full_url("/api/v1/teams"), "teams.json")

def _get_full_url(url_suffix):
    """ Helper function to append a URL suffix to get the full stats API link. """
    return f"{URL_STRING}{url_suffix}"

if __name__ == "__main__":
    """ Main function. """
    save_teams_data()
