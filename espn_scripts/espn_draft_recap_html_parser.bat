echo off

for %%x in (%*) do (
    %~dp0espn_draft_recap_html_parser.py -i %%x
)

pause