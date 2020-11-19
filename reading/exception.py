"""
Module for reading exceptions
"""

import utils


# CLASSES =====================================================================
class CartographyReaderException(Exception):
    # Constructor -------------------------------------------------------------
    def __init__(self, row: int, column: int, value: str, inv_type: str, pattern: str):
        Exception.__init__(self, 'Invalid {}: <{}> (l.{}, c.{}). Expected: <{}> (case insensitive)'.format(
            inv_type,
            utils.io.file.format_line_for_logging(value),
            row,
            column,
            pattern
        ))
