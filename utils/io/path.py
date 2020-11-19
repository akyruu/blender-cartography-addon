"""
Module for utility path methods
"""

import os


# METHODS =====================================================================
def workspace() -> os.path:
    return os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../..'))


def get(path: str) -> os.path:
    return os.path.join(workspace(), path) if path.startswith('@') else os.path.realpath(path)
