"""
Module for category methods relative to parsing
"""

import re
from typing import List, Optional, Tuple

import config
import mappings
import utils
from model import CartographyCategory
from ..__model import ParseContext
from ..exception import CartographyParserException


# METHODS =====================================================================
def parse_point_categories(value: str) -> List[Tuple[CartographyCategory, re.Match]]:
    """
    Parse value to extract point categories.

    :param value Text to parse
    :return List of categories found
    """
    categories = []
    for pattern, category in mappings.cartography_point_category.items():
        for part in value.split(config.obs_separator):
            m = __match_category_in_observation(pattern, part)
            if m:
                categories.append((category, m))
    return categories


def __match_category_in_observation(pattern: str, value: str) -> re.Match:
    m = utils.string.match_ignore_case(pattern, value, True)
    if not m:
        pattern = '(?!(' + '|'.join(config.mappings.words['proximity']) + ').)* ' + pattern
        m = utils.string.match_ignore_case(pattern, value, True)
        if not m:
            pattern += '.*'
            m = utils.string.match_ignore_case(pattern, value, True)
    return m


def parse_point_category(
        context: ParseContext,
        value: str,
        dft_value: Optional[CartographyCategory] = None,
        categories_to_ignore: List[CartographyCategory] = ()
) -> Tuple[CartographyCategory, Optional[re.Match]]:
    """
    Get the first category that match with value.

    :param context Parse context
    :param value Value to parse
    :param dft_value Default category to return if no category found (optional, None by default)
    :param categories_to_ignore List of category to ignore (optional, empty list by default).
    NB: must be bypass if filtered categories is empty)
    :return Tuple with category (required) and match result (optional)
    :raise CartographyParserException: No category found and default value is None
    """
    categories = parse_point_categories(value)
    if categories:
        return utils.collection.list.inext(
            ((c, m) for c, m in categories if c not in categories_to_ignore),
            categories[0]
        )
    elif dft_value is None:
        raise CartographyParserException(
            context.row,
            value,
            'point category',
            '|'.join(mappings.cartography_point_category.keys())
        )
    return dft_value, None
