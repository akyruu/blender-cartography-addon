"""
Module for TSV reader
"""

from config.patterns import TablePattern
from .csv import CartographyCsvReader


# CLASSES =====================================================================
class CartographyTsvReader(CartographyCsvReader):
    """TSV cartography reader"""

    # Constructor -------------------------------------------------------------
    def __init__(self, model: TablePattern):
        CartographyCsvReader.__init__(self, '\t', model)
