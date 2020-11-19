"""
Module for TSV writer
"""

import logging

from .csv import CartographyCsvWriter


# CLASSES =====================================================================
class CartographyTsvWriter(CartographyCsvWriter):
    """TSV cartography writer"""
    # Fields ------------------------------------------------------------------
    __logger: logging.Logger = logging.getLogger('CartographyTsvWriter')

    # Constructor -------------------------------------------------------------
    def __init__(self):
        CartographyCsvWriter.__init__(self, '\t', self.__logger)
