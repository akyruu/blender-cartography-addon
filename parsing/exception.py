"""
Module for parsing exceptions
"""

import utils


# CLASSES =====================================================================
class CartographyParserException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, f'Invalid {inv_type}: <{utils.io.file.format_line_for_logging(value)}> (l.{row}).'
                                 f' Expected: <{pattern}> (case insensitive)')
