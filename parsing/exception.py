"""
Module for parsing exceptions
"""

import utils


# CLASSES =====================================================================
class CartographyParserException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, 'Invalid {}: <{}> (l.{}). Expected: <{}> (case insensitive)'.format(
            inv_type,
            utils.io.file.format_line_for_logging(value),
            row,
            pattern
        ))
