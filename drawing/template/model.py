"""
Module for template model
"""

import os


# Classes =====================================================================
class CartographyTemplate:
    """Template for cartography"""

    # Constructor -------------------------------------------------------------
    def __init__(self, filepath: os.path):
        self.filepath = filepath
        self.objects = {}
