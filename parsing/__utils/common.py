"""
Module for common methods relative to parsing
"""

from copy import copy
from typing import Optional, Tuple

import mappings
import utils
from model import CartographyInterestType, CartographyPoint
from ..__model import ParseContext


# METHODS =====================================================================
def check_interest(
        context: ParseContext,
        value: str,
        dft_value: Optional[Tuple[CartographyInterestType, int]] = None
) -> Tuple[Optional[CartographyInterestType], int]:
    for pattern, interest in mappings.cartography_interest_type.items():
        # FIXME '(([0-9]+) )?' not working :(
        m = utils.string.match_ignore_case('([0-9]+) ' + pattern, value, False)
        if m:
            return interest, int(m.group(1))
        m = utils.string.match_ignore_case(pattern, value, False)
        if m:
            return interest, 1
    return dft_value


def format_value(line: str) -> str:
    return line.replace('\n', '\\n') \
        .replace('\t', '\\t')


def normalize_z_axis(point: CartographyPoint, z: int) -> CartographyPoint:
    norm_point = copy(point)
    norm_point.location = copy(point.location)
    norm_point.location.z = z
    norm_point.copy = True
    return norm_point
