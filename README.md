# ESPN League 54078 Fantasy Stats

## Introduction
This repository contains tools to download, parse, and generate data for: https://fantasy.espn.com/hockey/league?leagueId=54078

## Set-Up Instructions
Run setup_environment.bat or setup_environment.sh.

## Basic Usage
See the following for basic overview and usage of commonly used scripts.

### espn_fantasy_api_downloader.py
* Purpose: Downloads raw JSON files from various ESPN endpoints
* Reason: Downloaded data is stored on the machine for faster development
* Example: Downloads day to day roster data, player information, etc.
```
Example: Downloads data from 20152016 to 20252026 season
uv run espn_fantasy_api_downloader.py -s 2016 -e 2026
```

### data_generator_*.py
* Purpose: Parses through downloaded data from espn_fantasy_api_downloader.py and generates new data files for easier consumption
* Reason: This is so downstream tools don't need to handle processing raw JSON files themselves
* Example: Generated data can be in CSV format so downstream tools can consume them for easier analysis
```
Example: Generates draft data
uv run data_generator_draft.py
```

### espn_html_parser.py
* Purpose: Parses manually archived HTML files (which are usually checked into the repository)
* Reason: We took snapshots of historical league data because not everything was easily accessible or available through the APIs. We use data from the archived HTML files with fantasy API data to generate new data.
* Example: League standings data was archived because we currently cannot get fantasy API access to daily rosters data for older seasons (which could be used to derive league standings)
* Note: Script is mainly used for debugging and is not usually ran standalone
```
Example:
uv run espn_html_parser.py -i "..\espn_html_files"
```

## Development

### Running Unit Tests
Run on command line in the root project folder:
```
uv run -m unittest discover -s tests -v -b
```
### Project Management
Tasks and TODOs are backlogged in JIRA (access required): https://ivanchow-jira.atlassian.net/jira/software/projects/EFHS/boards/1/backlog

Note: This could change in the future since the repository has migrated to GitHub.

### Pull Requests
* Create a branch with the same name as the ticket or issue
* Push to the branch for code review
* Approved changes will be merged directly using squash as a single commit and the branch will be deleted

## System Architecture
See high_level_design_diagram.drawio for a design overview.