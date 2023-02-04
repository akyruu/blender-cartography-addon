"""
Module for utility file methods
"""

import json
import logging

from utils.common import T

# VARIABLES ===================================================================
__logger = logging.Logger("utils_io_file")


# METHODS =====================================================================
def format_line_for_logging(line: str) -> str:
    return line.replace('\n', '\\n').replace('\t', '\\t')


def read_json(path: str) -> T:
    __logger.info("Read json: %s", path)
    with open(path) as json_data:
        return json.loads(json_data.read())
