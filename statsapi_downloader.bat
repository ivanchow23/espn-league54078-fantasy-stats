:: Double click to run statsapi download
echo off

:: Year specified corresponds to year + 1
:: Example: 2023 will download for 20232024
set START_YEAR=2023
set END_YEAR=2023
set DOWNLOAD_PATH="%~dp0statsapi_downloads"

%~dp0statsapi_scripts\statsapi_downloader.py -s %START_YEAR% -e %END_YEAR% -o %DOWNLOAD_PATH%
pause
