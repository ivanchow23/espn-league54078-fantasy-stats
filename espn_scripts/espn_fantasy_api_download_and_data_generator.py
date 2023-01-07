#!/usr/bin/env python
""" Simple wrapper script that calls the ESPN fantasy API downloader
    and data generator together. Meant to be a one click solution to
    generate data easily for analysis. """
from espn_fantasy_api_daily_rosters_data_generator import EspnFantasyApiDailyRostersDataGenerator
from espn_fantasy_api_downloader import EspnFantasyApiDownloader
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Configurations
start_year = 2024
end_year = 2024
league_id = 54078

if __name__ == "__main__":
    # Download
    print("-------------------- Running ESPN fantasy API downloader --------------------")
    for season in range(start_year, end_year + 1):
        downloader = EspnFantasyApiDownloader(season, league_id)
        downloader.download_league_info()
        downloader.download_scoring_periods()

    # Generate data into analysis folder
    print("------------ Running ESPN fantasy API daily roster data generator -----------")
    generator = EspnFantasyApiDailyRostersDataGenerator(SCRIPT_DIR.joinpath("espn_fantasy_api_downloads"), SCRIPT_DIR.parent.joinpath("espn_statsapi_analysis", "espn_fantasy_api"))
    generator.generate()