# Requires:
#    - Make
#    -
# They should be able to run from anywhere using
# make -f <path/to/this/Makefile> [<target>]

# Tested on ubuntu 22.04 with python3.8.10
# Requires python3 and pip.

# Set desired python3 interpretter first on PATH or here..
GLOBALPYTHON ?= python3

# Path to this Makefile's parent directory. '.' is sufficient if caled from the same directory
MAKEPATH ?= $(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))

# Path to the location you wish the virtual environment to be created
VENV ?= ${MAKEPATH}/.venv

all: init test build

init: ${MAKEPATH}/requirements.txt
	${GLOBALPYTHON} -m venv ${VENV}
	cd ${MAKEPATH} && ${VENV}/bin/pip install -r ${MAKEPATH}/requirements.txt && cd -

test:
	${VENV}/bin/python3 -m unittest discover -s ${MAKEPATH}/tests || true

statsapi_downloader: START_YEAR=2023
statsapi_downloader: END_YEAR=2023
statsapi_downloader: DOWNLOAD_PATH="statsapi_downloads"
statsapi_downloader:
	@echo "This doesn't work. API? It gone.."
	${GLOBALPYTHON} statsapi_scripts/statsapi_downloader.py -s ${START_YEAR} -e ${END_YEAR} -o ${DOWNLOAD_PATH}

espn_html_parser_automation: ESPNHTML=html_raw
espn_html_parser_automation:
	${GLOBALPYTHON} espn_scripts/espn_html_parser_automation.py -d ${ESPNHTML}

espn_fantasy_api_download_and_data_generator:
	${GLOBALPYTHON} espn_scripts/espn_fantasy_api_download_and_data_generator.py

espn_statsapi_data_generator: ESPN=html_raw
espn_statsapi_data_generator: STATSAPI="statsapi_downloads"
espn_statsapi_data_generator: OUTDIR=statsapi_out
espn_statsapi_data_generator:
	${GLOBALPYTHON} espn_statsapi_scripts/espn_statsapi_data_generator.py --espn ${ESPN} --statsapi ${STATSAPI} --outdir ${OUTDIR}

espn_statsapi_validation: ESPN=html_raw
espn_statsapi_validation: STATSAPI="statsapi_downloads"
espn_statsapi_validation: OUTDIR=statsapi_out
espn_statsapi_validation:
	${GLOBALPYTHON} espn_statsapi_scripts/espn_statsapi_validation.py --espn ${ESPN} --statsapi ${STATSAPI} --outdir ${OUTDIR}

.PHONY: all init test
