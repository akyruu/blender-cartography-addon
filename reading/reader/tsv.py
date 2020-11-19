"""
Module for TSV reader
"""

import logging

from .csv import CartographyCsvReader
from ..model import ReadContext


# CLASSES =====================================================================
class CartographyTsvReader(CartographyCsvReader):
    """TSV cartography reader"""
    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyTsvReader')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        CartographyCsvReader.__init__(self, '\t', self.__logger)
