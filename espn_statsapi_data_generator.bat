:: Drag and drop ESPN HTML root data and statsapi downloaded root folder to run data generator.
:: Note: Must drag and drop ESPN folder on as the first folder.
%~dp0\espn_statsapi_scripts\espn_statsapi_data_generator.py --espn %1 --statsapi %2 --outdir %~dp1
pause