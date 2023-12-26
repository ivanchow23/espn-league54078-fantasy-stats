#!/usr/bin/env python
""" Utility file to help with handling requests to an API.
    Supports JSON data loading, downloading, etc. """
import aiohttp
import asyncio
import certifi
import json
import requests
import ssl
import sys

class RequestsUtil():
    def __init__(self, base_url):
        self._base_url = base_url

    def load_json_from_endpoint(self, endpoint, headers=None, cookies=None):
        """ Loads JSON data from an endpoint into a dictionary. """
        return self._load_json(f"{self._base_url}{endpoint}", headers, cookies)

    def save_json_from_endpoint(self, endpoint, out_file_path, headers=None, cookies=None):
        """ Save data from the an endpoint into a JSON file output.
            Returns True if request and data saving is successful. """
        # Load data
        json_data = self._load_json(f"{self._base_url}{endpoint}", headers, cookies)
        if json_data is None:
            return False

        # Save to file
        with open(out_file_path, 'w') as out_file:
            json.dump(json_data, out_file)
        return True

    def load_jsons_from_endpoints_async(self, endpoint_list, headers=None, cookies=None):
        """ Loads JSON data from the given list of endpoints asynchronously.
            Returns a list of dictionaries. """
        # Set policy on Windows and Python 3.8+ to work around runtime exception:
        # https://github.com/encode/httpx/issues/914#issuecomment-622586610
        if (sys.version_info[0] == 3 and
            sys.version_info[1] >= 8 and
            sys.platform.startswith('win')):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        url_list = [f"{self._base_url}{endpoint}" for endpoint in endpoint_list]
        return asyncio.run(self._load_jsons_async(url_list, headers, cookies))

    def save_jsons_from_endpoints_async(self, endpoints_file_path_dict_list, headers=None, cookies=None):
        """ Saves JSON data from the given endpoints and corresponding file
            output path asynchronously. Input is a list of dictionaries in the
            form: {'endpoint': <endpoint>, 'out_file_path': <output file path>}

            Note: The requests are asynchronous but saving to JSON are not. """
        # Input is a dictionary to enforce that every URL link has a
        # corresponding file output path. Unpack into individual lists here
        # to take advantage of requesting JSON data asynchronously before
        # writing to file. Async operations preserve order.
        url_list = []
        file_path_list = []
        for d in endpoints_file_path_dict_list:
            url_list.append(f"{self._base_url}{d['endpoint']}")
            file_path_list.append(d['out_file_path'])

        # Set policy on Windows and Python 3.8+ to work around runtime exception:
        # https://github.com/encode/httpx/issues/914#issuecomment-622586610
        if (sys.version_info[0] == 3 and
            sys.version_info[1] >= 8 and
            sys.platform.startswith('win')):
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        # Run event loop and retrieve list of data after requests are finished
        json_data_list = asyncio.run(self._load_jsons_async(url_list, headers, cookies))
        for json_data, file_path in zip(json_data_list, file_path_list):
            with open(file_path, 'w') as out_file:
                json.dump(json_data, out_file)

        return len(json_data_list)

    def _load_json(self, url, headers=None, cookies=None):
        """ Loads data from the URL as a dictionary. """
        # Send request to URL
        response = requests.get(url, headers=headers, cookies=cookies)
        if response.status_code != 200:
            return None

        return response.json()

    async def _load_jsons_async(self, url_list, headers=None, cookies=None):
        """ Loads data from the given URL list asynchronously. Returns
            a list of dictionaries where each dictionary is expected to
            be in the same order as the input URL list. """
        json_data_list = []
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        connector = aiohttp.TCPConnector(ssl=ssl_context, limit=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = []
            for url in url_list:
                tasks.append(asyncio.create_task(self._load_json_from_session(session, url, headers, cookies)))

            json_data_list = await asyncio.gather(*tasks)
        return json_data_list

    async def _load_json_from_session(self, session, url, headers=None, cookies=None):
        """ Loads data from URL as dictionary from a session using the
            aiohttp library asynchronously. Intended to be used with
            asyncio event loop. """
        async with session.get(url, headers=headers, cookies=cookies) as resp:
            if resp.status != 200:
                return {}
            return await resp.json()