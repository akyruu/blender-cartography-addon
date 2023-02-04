"""
Module for reading exceptions
"""

import utils


# CLASSES =====================================================================
class CartographyReaderException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, column: int, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, CartographyReaderException.__get_message(value, pattern).format(
            inv_type,
            row,
            column,
            utils.io.file.format_line_for_logging(value),
            utils.io.file.format_line_for_logging(pattern)
        ))

    # Methods -----------------------------------------------------------------
    @staticmethod
    def __get_message(value: str, pattern: str) -> str:
        return 'Invalid {} (l.{}, c.{}):' \
               + ('\n\tCurrent: <{}>\n\tExpected: <{}> (case insensitive)'
                  if (value and len(value) > 80) or (pattern and len(pattern) > 80)
                  else 'Current: <{}>. Expected: <{}> (case insensitive)')
