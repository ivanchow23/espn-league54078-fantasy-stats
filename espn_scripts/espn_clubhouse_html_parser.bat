echo off

for %%x in (%*) do (
    %~dp0espn_clubhouse_html_parser.py -i %%x
)

pause