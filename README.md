# ESPN Fantasy Hockey Stats

## Introduction
This repository contains various tools to download, parse, and analyze ESPN fantasy hockey data for league: https://fantasy.espn.com/hockey/league?leagueId=54078

Some tools/functionality include methods to:
* Download raw ESPN fantasy hockey data
* Parse historically saved ESPN fantasy hockey HTML pages
* Generate "raw data" files for data analysis
* Analyze data and generate stats, plots, tables, etc.

See high_level_design_diagram.drawio for a design overview.

## Set-Up Instructions
Run setup_environment.bat.

This will download uv, install Python, create a virtual environment, and download packages in the repository.

## Basic Usage
Various commonly used .bat scripts for downloading and data generation are placed in the root of the repository for convenience. For example, ESPN fantasy API data downloading and generation are wrapped together in one .bat file. These .bat scripts can be ran by double clicking on them, or dragging and dropping input files onto them depending on the .bat script.

There is also an analysis folder where generated data will be put into. These folders contain various notebooks used to analyze data, generate stats and plots, etc.

Use "uv run" before running any script on command line.

## Development
### Running Unit Tests
Run on command line in the root project folder:
```
uv run -m unittest discover -s tests -v -b
```
### Project Management
Tasks and TODOs are backlogged in JIRA (access required): https://ivanchow-jira.atlassian.net/jira/software/projects/EFHS/boards/1/backlog

### Pull Requests
* Create a branch with the same name as the JIRA ticket
* Push to the branch for code review
* Approved changes will be merged directly onto master (using squash as a single commit) and the branch will be deleted.