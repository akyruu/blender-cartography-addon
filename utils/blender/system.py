"""
Module for utility blender system methods
"""

import sys
from typing import List


# METHODS =====================================================================
def get_script_args() -> List[str]:
    index = sys.argv.index('--')
    return [arg for i, arg in enumerate(sys.argv) if i > index] \
        if index > 0 \
        else sys.argv
