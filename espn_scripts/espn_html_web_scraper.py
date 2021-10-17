#!/usr/bin/env python
from datetime import datetime
from espn_utils import sub_special_chars
from espn_html_parser_clubhouse import EspnHtmlParserClubhouse
from espn_html_parser_league_standings import EspnHtmlParserLeagueStandings
import os
import pickle
from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.edge.options import Options
from selenium.webdriver.edge.service import Service
import time

import espn_logger
logger = espn_logger.logger()

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

class EspnHtmlWebScraper():
    """ Class for providing functionality to scrape data from ESPN
        fantasy hockey sites. Intended use is to save day-by-day data
        to files for later usage. League website must be viewable by
        public. """

    def __init__(self, league_id, season_id, num_teams, out_dir):
        """ Constructor. Takes in league ID and season ID to
            use for getting league standings and clubhouse data.
            Number of teams is used as the ID for each team. Also
            takes an output directory where scraped data is output
            and archived. """
        # Used for loading or retrying webpages
        self.GET_WAIT_TIME_SEC = 5
        self.GET_RETRY_TIME_SEC = 10
        self.GET_RETRY_NUM_TIMES = 20

        # Used internally throughout class
        self._league_id = league_id
        self._season_id = season_id
        self._num_teams = num_teams
        self._out_dir = out_dir
        self._league_standings_pickle_path = os.path.join(self._out_dir, "League Standings.pickle")
        self._clubhouses_pickle_path = os.path.join(self._out_dir, "Clubhouses.pickle")

        self._driver = None
        self._dt_str = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        self._log(logger.info, f"------------------ Instantiated class at {self._dt_str} ------------------")

    def __del__(self):
        """ Destructor. """
        self.close_driver()

    def run(self):
        """ Main runner function. Goes through all the different links
            to scrape. Saves the HTML and parses the data. Stores the
            data to files to keep track of all the relevant data after
            scraping. Call after init_driver and before close_driver. """
        self._log(logger.info, "Running main method.")

        # Web driver must be initialized first
        if self._driver is None:
            self._log(logger.error, "Driver is not initialized.")
            return

        # Create archive directory
        archive_folder_path = os.path.join(self._out_dir, "archive")
        os.makedirs(archive_folder_path, exist_ok=True)

        # Scrape, parse, and save league standings data
        url = f"https://fantasy.espn.com/hockey/league/standings?leagueId={self._league_id}"
        html_path = self._save_html(url, archive_folder_path)
        espn = EspnHtmlParserLeagueStandings(html_path)
        data_dict = {self._dt_str: espn.get_standings_dict()}

        self._log(logger.info, f"Appending to: {self._league_standings_pickle_path}")
        if not self._append_dict_to_pickle(data_dict, self._league_standings_pickle_path):
            self._log(logger.error, f"Error appending to: {self._league_standings_pickle_path}")

        # Scrape, parse, and save all individual clubhouse data
        clubhouse_dict = {self._dt_str: []}
        for index in range(0, self._num_teams):
            team_id = index + 1
            url = f"https://fantasy.espn.com/hockey/team?leagueId={self._league_id}&seasonId={self._season_id}&teamId={team_id}"
            html_path = self._save_html(url, archive_folder_path)
            espn = EspnHtmlParserClubhouse(html_path)

            d = {}
            d.update(espn.get_team_owners_dict())
            d.update(espn.get_rosters_dict())
            clubhouse_dict[self._dt_str].append(d)

        self._log(logger.info, f"Appending to: {self._clubhouses_pickle_path}")
        if not self._append_dict_to_pickle(clubhouse_dict, self._clubhouses_pickle_path):
            self._log(logger.error, f"Error appending to: {self._clubhouses_pickle_path}")

    def init_driver(self):
        """ Instantiates a webdriver object. Must be called before
            using other methods in the class. Note: Currently supports
            Microsoft Edge because most machines (assuming Windows)
            will have this browser installed by default. """
        if self._driver is None:
            # Headless option opens the web browser in the background
            options = Options()
            options.headless = True
            options.add_experimental_option('excludeSwitches', ['enable-logging'])

            # Location of the webdriver binary
            service = Service(os.path.join(SCRIPT_DIR, "webdrivers", "msedgedriver.exe"))

            # Return an instance of the web driver
            self._driver = webdriver.Edge(options=options, service=service)
            self._log(logger.info, "Initialized web driver.")

    def close_driver(self):
        """ Closes the webdriver instance. Recommended to call this
            method before exiting scripts so web browser instances
            aren't left running on the system. """
        if self._driver is not None:
            self._driver.quit()
            self._log(logger.info, "Closed web driver.")
        self._driver = None

    def _save_html(self, url, output_path):
        """ Scrapes HTML of the given URL and outputs to an HTML file
            in the given output folder path. Folder path must already
            exist. Has a retry mechanism in case of a connection failure.
            Retries up to the specified number of times before giving up.
            Returns path to the saved file on success. False otherwise. """
        get_success = False
        retry_counter = 0

        self._log(logger.info, f"Opening webpage: {url}")
        while not get_success and retry_counter < self.GET_RETRY_NUM_TIMES:
            try:
                self._driver.get(url)
                time.sleep(self.GET_WAIT_TIME_SEC)
                get_success = True
            except WebDriverException:
                retry_counter += 1
                self._log(logger.warning, f"Failed. Retrying ({retry_counter}/{self.GET_RETRY_NUM_TIMES}) in {self.GET_RETRY_TIME_SEC}s.")
                time.sleep(self.GET_RETRY_TIME_SEC)

        # Return early on fail
        if not get_success:
            self._log(logger.warning, "Maximum retries reached.")
            return None
        # Save HTML to file on success
        else:
            html_path = os.path.join(output_path, f"{sub_special_chars(self._driver.title)} ({self._dt_str}).html")
            self._log(logger.info, f"Saving: {html_path}")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self._driver.page_source)
            return html_path

    def _append_dict_to_pickle(self, data_dict, pickle_path):
        """ Helper function that appends a dictionary to an existing
            dictionary in a pickle file. If pickle path doesn't already
            exist, creates a new pickle and writes the dictionary.
            Otherwise, loads the pickle, reads the dictionary and
            appends the new one to it. """
        if not isinstance(data_dict, dict):
            self._log(logger.warning, "Input data must be a dictionary.")
            return False

        # Read and append to dictionary if pickle already exists
        if os.path.exists(pickle_path):
            pickle_dict = pickle.load(open(pickle_path, 'rb'))
            if not isinstance(pickle_dict, dict):
                self._log(logger.warning, "Pickle data is not a dictionary.")
                return False

            pickle_dict.update(data_dict)
            pickle.dump(pickle_dict, open(pickle_path, 'wb'))
        # Otherwise, create a new pickle and output data
        else:
            pickle.dump(data_dict, open(pickle_path, 'wb'))

        return True

    def _log(self, logger_func, msg):
        """ Wrapper for logging messages with a timestamp. Required
            because logging.ini file in this directory does not
            currently have timestamps in message since they aren't
            required in other scripts. """
        dt = datetime.now().isoformat(sep=' ', timespec='milliseconds')
        logger_func(f"{dt} {msg}")

if __name__ == "__main__":
    web_scraper = EspnHtmlWebScraper(league_id=54078,
                                     season_id=2022,
                                     num_teams=7,
                                     out_dir="E:\\espn_html_web_scraper_data")
    web_scraper.init_driver()
    web_scraper.run()
    web_scraper.close_driver()