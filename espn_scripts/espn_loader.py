#!/usr/bin/env python
""" Utility to load data generated from ESPN parser scripts. """
import os
import pickle
import re

class EspnLoader():
    """ Holds a reference to the root ESPN data folder and provides APIs to load data from it.
        Assumes the following general structure in data folder:

        root_folder
          20192020
            - pickles
              -> <clubhouse_data>.pickle
              -> <draft_data>.pickle
              -> etc.
          20202021
            - pickles
              -> <clubhouse_data>.pickle
              -> <draft_data>.pickle
              -> etc.
    """
    def __init__(self, root_folder_path):
        """ Constructor. Takes in path to root data folder. """
        self._root_folder_path = root_folder_path

    def load_clubhouses_data(self, season_string):
        """ Loads data from clubhouses file given season string. Returns None on failure. """
        return self._load_pickle(season_string, "Clubhouses")

    def load_draft_recap_data(self, season_string):
        """ Loads data from draft recap file given season string. Returns None on failure. """
        return self._load_pickle(season_string, "Draft Recap")

    def load_league_standings_data(self, season_string):
        """ Loads data from league standings file given season string. Returns None on failure. """
        return self._load_pickle(season_string, "League Standings")

    def get_seasons(self):
        """ Returns a list of season folders from the root.
            Folder must be in the form XXXXYYYY. """
        # Regex pattern to find a season string
        #   - ^ used to denote start of string searching
        #   - $ used to denote end of string searching
        #   - + used to denote any repeating numbers between [0-9]
        # Examples:
        #  - "20192020" (ok)
        #  - "aaa20192020" (no)
        #  - "20192020aaa" (no)
        season_string_re_pattern = "^[0-9]+$"

        if not self._check_path(self._root_folder_path):
            return []

        ret_list = []
        for item in os.listdir(self._root_folder_path):
            item_path = os.path.join(self._root_folder_path, item)
            if os.path.isdir(item_path) and re.match(season_string_re_pattern, item):
                ret_list.append(item)

        return ret_list

    def _load_pickle(self, season_string, file_search_string):
        """ Helper function to load pickle file. """
        file_path = self._find_file_path_recursive(season_string, file_search_string, ".pickle")
        if not self._check_path(file_path):
            return None
        return pickle.load(open(file_path, 'rb'))

    def _find_file_path_recursive(self, season_string, file_search_string, file_ext):
        """ Helper function to retrieve the file path of the given file, given the search
            string to find a name contained in the file and the extension to look for.
            Looks in the season folder for a file containing the string, then searches
            folders within recursively. Returns first instance if found. None otherwise. """
        if (not isinstance(season_string, str) or
            not isinstance(file_search_string, str) or
            not isinstance(file_ext, str)):
            return None

        season_folder_path = os.path.join(self._root_folder_path, season_string)
        if not self._check_path(season_folder_path):
            return None

        for root, _, files in os.walk(season_folder_path):
            for f in files:
                if file_search_string in f and file_ext in f:
                    return os.path.join(root, f)

        return None

    def _check_path(self, path):
        """ Helper function to test if a path is valid and/or whether it exists. """
        if not isinstance(path, str) or not os.path.exists(path):
            return False
        return True

