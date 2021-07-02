#!/usr/bin/env python
""" Common utilities file used for retrieving data from statsapi. """
import os
import json
import requests
import statsapi_logger

URL_STRING = "https://statsapi.web.nhl.com"
URL_STRING_API_PREFIX = "https://statsapi.web.nhl.com/api/v1"
logger = statsapi_logger.logger()

def load_json_from_url(url):
    """ Loads JSON data from the given URL into a dictionary. """
    return _load_json(url)

def save_json_from_url(url, out_file_path):
    """ Save data from the given URL into a JSON file output.
        Returns True if request and data saving is successful. """
    # Check JSON output
    if not _is_json(out_file_path):
        logger.warning(f"Output {out_file_path} is not a .json file.")
        return False

    # Load data
    json_data = _load_json(url)
    if json_data is None:
        return False

    # Save to file
    with open(out_file_path, 'w') as out_file:
        json.dump(json_data, out_file)

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

def _load_json(url):
    """ Loads data from the URL as a dictionary.
        Assumes data to be in JSON format. """
    # Check input URL before sending request
    if not _check_url(url):
        logger.warning(f"{url} is invalid for Stats API access.")
        return None

    # Send request to URL
    response = requests.get(url)
    if response.status_code != 200:
        logger.warning(f"Request to {url} failed.")
        return None

    return response.json()