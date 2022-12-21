"""
Module for category methods relative to parsing
"""

import re
from typing import List, Optional, Tuple

import config
import mappings
import utils
from model import CartographyCategory
from ..exception import CartographyParserException
from ..model import ParseContext


# METHODS =====================================================================
def parse_categories(values: List[str] or str, required=False) -> List[Tuple[CartographyCategory, re.Match]]:
    """
    Parse value(s) to extract categories for value(s).<br />
    NB: Only one category maximum must be found for each value item.

    :param values Text(s) to parse
    :param required If an exception must be thrown if not category found
    :return List of categories found
    """
    categories = []

    parts = (values if isinstance(values, list) else values.split(config.obs_separator))
    for pattern, category in mappings.cartography_point_category.items():
        for part in parts:
            m = __match_category_in_observation(pattern, part)
            if m:
                categories.append((category, m))

    if not categories and required:
        raise CartographyParserException('Category not found in values')

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


# FIXME deprecated ?
def parse_point_category(
        context: ParseContext,
        categories: List[CartographyCategory],
        dft_value: Optional[CartographyCategory] = None,
        categories_to_ignore: List[CartographyCategory] = []  # noqa
) -> CartographyCategory:
    """
    Get the first category that match with value.

    :param context Parse context
    :param values Value(s) to parse
    :param dft_value Default category to return if no category found (optional, None by default)
    :param categories_to_ignore List of category to ignore (optional, empty list by default).
    NB: must be bypass if filtered categories is empty)
    :return Tuple with category (required) and match result (optional)
    :raise CartographyParserException: No category found and default value is None
    """
    if categories:
        return utils.collection.list.inext((c for c in categories if c not in categories_to_ignore), categories[0])
    elif dft_value is None:
        raise CartographyParserException(f'Line #{context.row} - Category not found in {categories}'
                                         f' (accepted: {mappings.cartography_point_category.keys()}')
    return dft_value
