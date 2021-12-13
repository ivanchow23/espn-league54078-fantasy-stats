#!/usr/bin/env python
""" Common utilities file used for retrieving data from statsapi. """
import aiohttp
import asyncio
import os
import json
import requests
import statsapi_logger
import sys

URL_STRING = "https://statsapi.web.nhl.com"
API_ENDPOINT_PREFIX = "/api/v1"
URL_STRING_API_PREFIX = f"https://statsapi.web.nhl.com{API_ENDPOINT_PREFIX}"

logger = statsapi_logger.logger()

def load_json_from_url(url):
    """ Loads JSON data from the given URL into a dictionary. """
    return _load_json(url)

def save_json_from_url(url, out_file_path):
    """ Save data from the given URL into a JSON file output.
        Returns True if request and data saving is successful. """
    # Check JSON output
    if not _is_json(out_file_path):
        logger.error(f"Output {out_file_path} is not a .json file.")
        return False

    # Load data
    json_data = _load_json(url)
    if json_data is None:
        return False

    # Save to file
    with open(out_file_path, 'w') as out_file:
        json.dump(json_data, out_file)

    return True

def load_jsons_from_urls_async(url_list):
    """ Loads JSON data from the given list of URLs asynchronously.
        Returns a list of dictionaries. """
    # Set policy on Windows and Python 3.8+ to work around runtime exception:
    # https://github.com/encode/httpx/issues/914#issuecomment-622586610
    if (sys.version_info[0] == 3 and
        sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    return asyncio.run(_load_jsons_async(url_list))

def save_jsons_from_urls_async(url_file_path_dict_list):
    """ Saves JSON data from the given URLs and corresponding file output
        path asynchronously. Input is a list of dictionaries in the form:
        {'url': <url>, 'out_file_path': <output file path>}

        Note: The requests each URL links is ran asynchronously. Saving
        to JSON files are not. """
    # Input is a dictionary to enforce that every URL link has a
    # corresponding file output path. Unpack into individual lists here
    # to take advantage of requesting JSON data asynchronously before
    # writing to file.
    url_list = []
    file_path_list = []
    for d in url_file_path_dict_list:
        url_list.append(d['url'])
        file_path_list.append(d['out_file_path'])

    # Set policy on Windows and Python 3.8+ to work around runtime exception:
    # https://github.com/encode/httpx/issues/914#issuecomment-622586610
    if (sys.version_info[0] == 3 and
        sys.version_info[1] >= 8 and
        sys.platform.startswith('win')):
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    json_data_list = asyncio.run(_load_jsons_async(url_list))
    for json_data, file_path in zip(json_data_list, file_path_list):
        with open(file_path, 'w') as out_file:
            json.dump(json_data, out_file)

    return len(json_data_list)

def get_full_url(endpoint):
    """ Helper function that retrieves the full statsapi URL given the endpoint. """
    return f"{URL_STRING}{endpoint}"

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
        logger.error(f"{url} is invalid for Stats API access.")
        return None

    # Send request to URL
    response = requests.get(url)
    if response.status_code != 200:
        logger.error(f"Request to {url} failed.")
        return None

    return response.json()

async def _load_json_from_session(session, url):
    """ Loads data from URL as dictionary from a session using the
        aiohttp library asynchronously. Intended to be used with
        asyncio event loop. """
    # Check input URL before sending request
    if not _check_url(url):
        logger.error(f"{url} is invalid for Stats API access.")
        return {}

    async with session.get(url) as resp:
        return await resp.json()

async def _load_jsons_async(url_list):
    """ Loads data from the given URL list asynchronously. Returns
        a list of dictionaries where each dictionary is expected to
        be in the same order as the input URL list. """
    json_data_list = []
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in url_list:
            tasks.append(asyncio.create_task(_load_json_from_session(session, url)))

        json_data_list = await asyncio.gather(*tasks)
    return json_data_list