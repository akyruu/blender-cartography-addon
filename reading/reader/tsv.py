"""
Module for TSV reader
"""

from .csv import CartographyCsvReader
from ..config.table import ModelVersion


# CLASSES =====================================================================
class CartographyTsvReader(CartographyCsvReader):
    """TSV cartography reader"""

    # Constructor -------------------------------------------------------------
    def __init__(self, version: ModelVersion, read_coordinates=True):
        CartographyCsvReader.__init__(self, '\t', version, read_coordinates)
