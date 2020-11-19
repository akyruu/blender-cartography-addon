"""
Module for commons writer classes
"""
from abc import abstractmethod
from pathlib import Path
from typing import Optional

from reading import CartographyFile


# CLASSES =====================================================================
class CartographyWriter:
    """Interface for cartography writers"""

    # Methods -----------------------------------------------------------------
    @abstractmethod
    def write(self, file: CartographyFile, filepath: Optional[Path] = None) -> CartographyFile:
        pass
