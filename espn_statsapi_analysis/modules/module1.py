#!/usr/bin/env python
import os
import sys

SCRIPT_DIR = os.path.join(os.path.abspath(__file__))
sys.path.insert(1, os.path.join(SCRIPT_DIR, ".."))
import esa_logger

logger = esa_logger.logger()

class Module1():
    def __init__(self, espn_loader, statsapi_loader, out_path):
        logger.info("Module 1 __init__")
        logger.info(f"Module 1 out_path: {out_path}")

    def process(self):
        logger.info("Module 1 Process.")