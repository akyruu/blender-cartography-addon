"""
Module for utility path methods
"""

import os
import sys


# METHODS =====================================================================
def workspace() -> os.path:
    # FIXME ok for debug only
    paths = [path for path in sys.path if os.path.basename(path) == 'blender-cartography-addon']
    return paths[0]


def get(path: str) -> os.path:
    return os.path.join(workspace(), path) if path.startswith('@') else os.path.realpath(path)
