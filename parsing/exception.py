"""
Module for parsing exceptions
"""


# CLASSES =====================================================================
class CartographyParserException(Exception):
    # Constructor -------------------------------------------------------------

    def __init__(self, row: int, message: str):
        Exception.__init__(self, f'Row #{row} - {message}')
