#!/usr/bin/env python
""" Common utilities file used for retrieving data from statsapi. """
import json
import requests

URL_STRING =  "https://statsapi.web.nhl.com"
URL_STRING_API_PREFIX = "https://statsapi.web.nhl.com/api/v1"

def url_to_json(url, out_file_path):
    """ Save data from the given URL into a JSON file output.
        Returns True if request and data saving is successful. """

    # Check JSON output
    if not _is_json(out_file_path):
        print(f"Output {out_file_path} is not a .json file.")
        return False

    # Check input URL before sending request
    if not _check_url(url):
        print(f"{url} is invalid for Stats API access.")
        return False

    # Send request to URL
    response = requests.get(url)
    if response.status_code != 200:
        print(f"Request to {url} failed.")
        return False

    # Read as JSON and save to file
    with open(out_file_path, 'w') as out_file:
        json.dump(response.json(), out_file)

    return True

def _check_url(url):
    """ Basic checks for URL input string. """
    # Check string input
    if not isinstance(url, str):
        return False

    # Check URL starts with stats API string
    if not url.startswith(URL_STRING_API_PREFIX):
        return False

    return True

def _is_json(file_path):
    """ Basic checks if file path is a JSON file. """
    # Check string input
    if not isinstance(file_path, str):
        return False

    # Check extension
    if not file_path.endswith(".json"):
        return False

    return True