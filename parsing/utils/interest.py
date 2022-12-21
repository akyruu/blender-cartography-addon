"""
Module for common methods relative to parsing
"""

from typing import Optional

import mappings
import utils
from model import CartographyInterestType
from ..exception import CartographyParserException
from ..model import ParseContext


# METHODS =====================================================================
def parse_point_interest_v1p2(
        context: ParseContext,
        interest_label: str,
        dft_value: Optional[CartographyInterestType] = None,
        required: bool = False
) -> Optional[CartographyInterestType]:
    interests = [interest for pattern, interest in mappings.cartography_interest_type.items()
                 if utils.string.match_ignore_case(pattern, interest_label)]
    interests_len = len(interests)
    if interests_len == 0:
        interest = dft_value
    elif interests_len == 1:
        interest = interests[0]
    else:
        raise Exception(
            'Invalid mapping configuration: too much interests {} found for <{}>',
            interest_label, str(mappings.cartography_interest_type.keys())
        )

    if interest is None and required:
        raise CartographyParserException(
            context.row,
            interest_label,
            'point interest',
            '|'.join(mappings.cartography_interest_type.keys())
        )
    return interest
