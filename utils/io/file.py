"""
Module for utility file methods
"""

import json


# METHODS =====================================================================
def format_line_for_logging(line: str) -> str:
    return line.replace('\n', '\\n').replace('\t', '\\t')


def read_json(path: str):
    with open(path) as json_data:
        return json.loads(json_data.read())
