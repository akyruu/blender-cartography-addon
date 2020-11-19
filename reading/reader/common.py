"""
Module for commons reader classes
"""

import os
from abc import abstractmethod

from ..model import CartographyFile


# CLASSES =====================================================================
class CartographyReader:
    """Interface for cartography readers"""

    # Methods -----------------------------------------------------------------
    @abstractmethod
    def read(self, filepath: os.path) -> CartographyFile:
        pass
