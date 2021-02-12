echo off

for %%x in (%*) do (
    %~dp0espn_league_rosters_html_parser.py -i %%x
)

pause