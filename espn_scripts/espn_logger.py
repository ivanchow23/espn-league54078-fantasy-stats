#!/usr/bin/env python
""" Wrapper module for declaring a logger in other ESPN modules. Assumes script directory
    contains logging configuration file. Also assumes script directory is in the same directory
    as all other ESPN modules.

    Usage:
        import espn_logger
        logger = espn_logger.logger()
"""
import logging
import logging.config
import os

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

def logger():
    """ Helper function to return a logger instance. """
    logging.config.fileConfig(os.path.join(SCRIPT_DIR, "logging.ini"), disable_existing_loggers=False)
    return logging.getLogger()

if __name__ == "__main__":
    pass