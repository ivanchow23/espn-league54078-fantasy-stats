echo off

for %%x in (%*) do (
    %~dp0espn_league_roster_html_parser.py -i %%x
)

pause