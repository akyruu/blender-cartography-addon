"""
Module for common methods relative to parsing
"""

from typing import Optional, Tuple

import utils
from model import CartographyInterestType
from parsing import config as parse_config


# METHODS =====================================================================
def check_interest(value: str, dft_value: Optional[Tuple[CartographyInterestType, int]] = None) \
        -> Tuple[Optional[CartographyInterestType], int]:
    for pattern, interest in parse_config.interest.by_pattern.items():
        # FIXME '(([0-9]+) )?' not working :(
        m = utils.string.match_ignore_case('([0-9]+) ' + pattern, value, False)
        if m:
            return interest, int(m.group(1))
        m = utils.string.match_ignore_case(pattern, value, False)
        if m:
            return interest, 1
    return dft_value
