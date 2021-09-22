#!/usr/bin/env python
""" This script is meant to help auto-generate files across folders easier.
    Given a root folder:
      1. Recursively searches for other folders within.
      2. Looks for file names in a certain format.
      3. Calls the appropriate ESPN HTML parsing script to generate files.
    File names must be in a certain format to be parsed.

    Folder structure is expected to have the form:
    <root_folder>
    - 20192020
      -> <clubhouse1>.html
      -> <clubhouse2>.html
      -> <draft_recap>.html
      -> <espn_statsapi_correction>.csv (if needed)
      ...
    - 20202021
      -> <clubhouse1>.html
      -> <clubhouse2>.html
      -> <draft_recap>.html
      -> <espn_statsapi_correction>.csv (if needed)
      ...
"""
import argparse
from espn_html_parser_clubhouse import EspnHtmlParserClubhouse
from espn_html_parser_league_rosters import EspnHtmlParserLeagueRosters
from espn_html_parser_league_standings import EspnHtmlParserLeagueStandings
from espn_html_parser_draft_recap import EspnHtmlParserDraftRecap
import espn_utils
from espn_writer import EspnWriter
import os
import pandas as pd
import pickle
import re
import sys
import timeit

import espn_logger
logger = espn_logger.logger()

sys.path.insert(1, os.path.join(sys.path[0], "..", "espn_statsapi_scripts"))
import espn_statsapi_utils

def main(root_folder_path):
    """ Main automation function. Recursively looks for season folders with HTML pages to parse.
        Outputs parsed data into the same directory as input HTMLs. """
    # Timing
    start_time = timeit.default_timer()

    # Find folders to parse
    folder_paths_to_parse = _find_folders_with_html(root_folder_path)
    for folder_path in folder_paths_to_parse:
        logger.info(f"--------------------------- Processing folder: {folder_path} ---------------------------")

        # Assumes folder path is in the form of a season string: "XXXXYYYY" (e.g.: "20192020")
        season_string = os.path.basename(folder_path)

        # Find files to parse
        clubhouse_file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_CLUBHOUSE)
        league_roster_file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_LEAGUE_ROSTERS)
        league_standing_file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_LEAGUE_STANDINGS)
        draft_recap_file_paths = _find_files_recursive(folder_path, espn_utils.FILE_NAME_RE_FORMAT_DRAFT_RECAP)
        correction_files = _find_files_recursive(folder_path, "[0-9]+_corrections")

        # Set-up output
        espn_writer = EspnWriter(folder_path)

        # Parse clubhouse files
        team_owners_dicts = []
        team_owners_df = pd.DataFrame()
        clubhouse_dicts = []
        for file_path in clubhouse_file_paths:
            espn_parser = EspnHtmlParserClubhouse(file_path)

            if espn_parser.valid:
                logger.info(f"Parsing: {os.path.basename(file_path)}")
                clubhouse_rosters_dict = espn_parser.get_rosters_dict()
                team_owners_dict = espn_parser.get_team_owners_dict()

                clubhouse_dict = {}
                clubhouse_dict.update(team_owners_dict)
                clubhouse_dict.update(clubhouse_rosters_dict)
                clubhouse_dicts.append(clubhouse_dict)
                team_owners_dicts.append(team_owners_dict)

        team_owners_df = pd.DataFrame(team_owners_dicts)

        # Parse league roster files
        rosters_list = []
        for file_path in league_roster_file_paths:
            espn_parser = EspnHtmlParserLeagueRosters(file_path)

            if espn_parser.valid:
                logger.info(f"Parsing: {os.path.basename(file_path)}")
                rosters_list = espn_parser.get_rosters_list()

            # Intentional break after one loop - assumes at most one file in directory
            break

        # Parse league standings files
        league_standings_dict = {}
        for file_path in league_standing_file_paths:
            espn_parser = EspnHtmlParserLeagueStandings(file_path)

            if espn_parser.valid:
                logger.info(f"Parsing: {os.path.basename(file_path)}")
                league_standings_dict = espn_parser.get_standings_dict()

            # Intentional break after one loop - assumes at most one file in directory
            break

        # Parse draft recap files
        draft_recap_df = pd.DataFrame()
        for file_path in draft_recap_file_paths:
            espn_parser = EspnHtmlParserDraftRecap(file_path)

            if espn_parser.valid:
                logger.info(f"Parsing: {os.path.basename(file_path)}")
                draft_recap_df = espn_parser.get_df()

            # Get owner information into the draft dataframe
            if not draft_recap_df.empty:
                draft_recap_df = draft_recap_df.merge(team_owners_df, on='Team Name', how='left')

            # Intentional break after one loop - assumes at most one file in directory
            break

        # Apply team name corrections
        logger.info(f"Applying statsapi corrections for team abbreviations.")
        for clubhouse_dict in clubhouse_dicts:
            clubhouse_dict['skaters_df']['Skaters', 'Team'] = clubhouse_dict['skaters_df']['Skaters', 'Team'].apply(espn_statsapi_utils.statsapi_team_abbrev)
            clubhouse_dict['goalies_df']['Goalies', 'Team'] = clubhouse_dict['goalies_df']['Goalies', 'Team'].apply(espn_statsapi_utils.statsapi_team_abbrev)
        for roster in rosters_list:
            roster['roster_df']['Team'] = roster['roster_df']['Team'].apply(espn_statsapi_utils.statsapi_team_abbrev)
        if not draft_recap_df.empty:
            draft_recap_df['Team'] = draft_recap_df['Team'].apply(espn_statsapi_utils.statsapi_team_abbrev)

        # Apply corrections if file is found in directory - assumes up to one file exists
        correction_file_path = ""
        if len(correction_files) > 0:
            correction_file_path = correction_files[0]
            espn_corr = espn_statsapi_utils.CorrectionUtil(correction_file_path)
            if espn_corr.valid:
                logger.info(f"Applying statsapi corrections for players from: {os.path.basename(correction_file_path)}")

                # Apply to clubhouse rosters
                for clubhouse_dict in clubhouse_dicts:
                    # Iterating through dataframes is not intended, but it's currently the simplest way
                    for index, row in clubhouse_dict['skaters_df']['Skaters'].iterrows():
                        corrected_dict = espn_corr.get_corrected_dict(row['Player'], row['Team'])
                        if corrected_dict:
                            # Note: Use "at" to change df values: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html
                            clubhouse_dict['skaters_df'].at[index, ('Skaters', 'Player')] = corrected_dict['Corrected Player']
                            clubhouse_dict['skaters_df'].at[index, ('Skaters', 'Team')] = corrected_dict['Corrected Team']
                    # Iterating through dataframes is not intended, but it's currently the simplest way
                    for index, row in clubhouse_dict['goalies_df']['Goalies'].iterrows():
                        corrected_dict = espn_corr.get_corrected_dict(row['Player'], row['Team'])
                        if corrected_dict:
                            # Note: Use "at" to change df values: https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.at.html
                            clubhouse_dict['goalies_df'].at[index, ('Goalies', 'Player')] = corrected_dict['Corrected Player']
                            clubhouse_dict['goalies_df'].at[index, ('Goalies', 'Team')] = corrected_dict['Corrected Team']

                # Apply to league rosters
                for roster in rosters_list:
                    # Iterating through dataframes is not intended, but it's currently the simplest way
                    for index, row in roster['roster_df'].iterrows():
                        corrected_dict = espn_corr.get_corrected_dict(row['Player'], row['Team'])
                        if corrected_dict:
                            roster['roster_df'].at[index, 'Player'] = corrected_dict['Corrected Player']
                            roster['roster_df'].at[index, 'Team'] = corrected_dict['Corrected Team']

                # Apply to draft recap
                # Iterating through dataframes is not intended, but it's currently the simplest way
                for index, row in draft_recap_df.iterrows():
                    corrected_dict = espn_corr.get_corrected_dict(row['Player'], row['Team'])
                    if corrected_dict:
                        draft_recap_df.at[index, 'Player'] = corrected_dict['Corrected Player']
                        draft_recap_df.at[index, 'Team'] = corrected_dict['Corrected Team']

        # CSV outputs
        logger.info("Outputting CSV files.")
        for clubhouse_dict in clubhouse_dicts:
            file_basename = espn_utils.sub_special_chars((f"{season_string} Clubhouse - {clubhouse_dict['Team Name']} ({clubhouse_dict['Owner Name']})"))
            espn_writer.df_to_csv(clubhouse_dict['skaters_df'], f"{file_basename} - Skaters.csv")
            espn_writer.df_to_csv(clubhouse_dict['goalies_df'], f"{file_basename} - Goalies.csv")

        for roster in rosters_list:
            file_basename = espn_utils.sub_special_chars(f"{season_string} League Roster - {roster['team_name']}")
            espn_writer.df_to_csv(roster['roster_df'], f"{file_basename}.csv")

        espn_writer.df_to_csv(draft_recap_df, f"{season_string} Draft Recap.csv")
        espn_writer.df_to_csv(league_standings_dict['season_points'], f"{season_string} League Standings - Season Points.csv")
        espn_writer.df_to_csv(league_standings_dict['season_stats'], f"{season_string} League Standings - Season Stats.csv")
        espn_writer.df_to_csv(team_owners_df, f"{season_string} Team Owners.csv")

        # Excel outputs
        logger.info("Outputting Excel files.")
        for clubhouse_dict in clubhouse_dicts:
            skaters_sheet_name = espn_utils.sub_special_chars((f"{clubhouse_dict['Team Name']} ({clubhouse_dict['Owner Name']}) - Skaters"))
            goalies_sheet_name = espn_utils.sub_special_chars((f"{clubhouse_dict['Team Name']} ({clubhouse_dict['Owner Name']}) - Goalies"))
            espn_writer.df_to_excel(clubhouse_dict['skaters_df'], f"{season_string} Clubhouses.xlsx", sheet_name=skaters_sheet_name)
            espn_writer.df_to_excel(clubhouse_dict['goalies_df'], f"{season_string} Clubhouses.xlsx", sheet_name=goalies_sheet_name)

        for roster in rosters_list:
            espn_writer.df_to_excel(roster['roster_df'], f"{season_string} League Rosters.xlsx", sheet_name=roster['team_name'])

        espn_writer.df_to_excel(draft_recap_df, f"{season_string} Draft Recap.xlsx")
        espn_writer.df_to_excel(league_standings_dict['season_points'], f"{season_string} League Standings.xlsx", sheet_name="Season Points")
        espn_writer.df_to_excel(league_standings_dict['season_stats'], f"{season_string} League Standings.xlsx", sheet_name="Season Stats")

        # Pickle outputs
        logger.info("Outputting Pickle files.")
        espn_writer.to_pickle(clubhouse_dicts, f"{season_string} Clubhouses.pickle")
        espn_writer.to_pickle(rosters_list, f"{season_string} League Rosters.pickle")
        espn_writer.to_pickle(draft_recap_df, f"{season_string} Draft Recap.pickle")
        espn_writer.to_pickle(league_standings_dict, f"{season_string} League Standings.pickle")

    print(f"Finished in {round(timeit.default_timer() - start_time, 1)}s.")

def _find_folders_with_html(root_folder):
    """ Recursively finds all folders that contain at least one HTML file. """
    folder_paths_list = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if f.endswith(".html"):
                folder_paths_list.append(root)
                break
    return folder_paths_list

def _find_files_recursive(root_folder, file_pattern_re):
    """ Recursively finds files with given pattern in a root folder. """
    file_paths_list = []
    for root, _, files in os.walk(root_folder):
        for f in files:
            if re.match(file_pattern_re, f):
                file_paths_list.append(os.path.join(root, f))
    return file_paths_list

if __name__ == "__main__":
    arg_parse = argparse.ArgumentParser()
    arg_parse.add_argument("--root_folder", "-d", required=True, help="Path to the root folder containing ESPN HTML pages to parse.")
    args = arg_parse.parse_args()
    main(args.root_folder)