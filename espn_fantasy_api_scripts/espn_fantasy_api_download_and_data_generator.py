#!/usr/bin/env python
""" Simple wrapper script that calls the ESPN fantasy API downloader
    and data generator together. Meant to be a one click solution to
    generate data easily for analysis. """
import argparse
from espn_fantasy_api_daily_rosters_data_generator import EspnFantasyApiDailyRostersDataGenerator
from espn_fantasy_api_all_players_info_data_generator import EspnFantasyApiAllPlayersInfoDataGenerator
from espn_fantasy_api_downloader import EspnFantasyApiDownloader
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Configurations
start_year = 2026
end_year = 2026
league_id = 54078

if __name__ == "__main__":
    # Parse args
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--espn_s2", required=False, default=None, type=str, help="espn_s2 string used for a cookie for ESPN fantasy API requests.")
    args = arg_parser.parse_args()

    # Download
    print("-------------------- Running ESPN fantasy API downloader --------------------")
    for season in range(start_year, end_year + 1):
        downloader = EspnFantasyApiDownloader(season, league_id, cookies={'espn_s2': args.espn_s2})
        downloader.download_league_info()
        downloader.download_scoring_periods()
        downloader.download_all_players_info()
    print("Done.")

    # Generate data into analysis folder
    print("------------ Running ESPN fantasy API daily roster data generator -----------")
    generator = EspnFantasyApiDailyRostersDataGenerator(SCRIPT_DIR.joinpath("espn_fantasy_api_downloads"), SCRIPT_DIR.parent.joinpath("espn_nhlapi_analysis", "espn_fantasy_api"))
    generator.generate()
    print("Done.")

    print("------------ Running ESPN fantasy API all player data generator -----------")
    all_players_generator = EspnFantasyApiAllPlayersInfoDataGenerator(SCRIPT_DIR.joinpath("espn_fantasy_api_downloads"), SCRIPT_DIR.parent.joinpath("espn_nhlapi_analysis", "espn_fantasy_api"))
    all_players_generator.generate()
    print("Done.")