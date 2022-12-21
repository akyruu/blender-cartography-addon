"""
Module for category methods relative to parsing
"""

import re
from typing import List, Optional, Tuple

import config
import mappings
import utils
from model import CartographyCategory, CartographyCategoryType
from ..exception import CartographyParserException
from ..model import ParseContext


# METHODS =====================================================================
def is_outline(category: CartographyCategory):
    return category.type == CartographyCategoryType.STRUCTURAL and category.options.outline


def require_interest(category: CartographyCategory):
    return category.type == CartographyCategoryType.INTEREST and category.options.detailed_required


def parse_point_category_v1p2(
        context: ParseContext,
        category_label: str,
        dft_value: Optional[CartographyCategory] = None,
        required: bool = True
) -> Optional[CartographyCategory]:
    """
    Get the category corresponding to label (use the configuration mapping).

    :param context Parse context
    :param category_label Value(s) to parse
    :param dft_value Default category to return if no category found (optional, None by default)
    :param required If category is required (raise an exception if None)
    :return Category if found or dft_value otherwise
    """
    categories = [category for pattern, category in mappings.cartography_point_category.items()
                  if utils.string.match_ignore_case(pattern, category_label)]
    categories_len = len(categories)
    if categories_len == 0:
        category = dft_value
    elif categories_len == 1:
        category = categories[0]
    else:
        raise Exception('Invalid mapping configuration: too much categories {} found for <{}>'
                        .format(category_label, str(mappings.cartography_point_category.keys())))

    if category is None and required:
        raise CartographyParserException(
            context.row,
            category_label,
            'point category',
            '|'.join(mappings.cartography_point_category.keys())
        )
    return category


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
        raise CartographyParserException(
            -1,
            (config.obs_separator.join(values) if isinstance(values, list) else values),
            'point categories',
            '|'.join(mappings.cartography_point_category.keys())
        )

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
        values: List[str] or str,
        dft_value: Optional[CartographyCategory] = None,
        categories_to_ignore: List[CartographyCategory] = []  # noqa
) -> Tuple[CartographyCategory, Optional[re.Match]]:
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
    categories = parse_categories(values)
    if categories:
        return utils.collection.list.inext(
            ((c, m) for c, m in categories if c not in categories_to_ignore),
            categories[0]
        )
    elif dft_value is None:
        raise CartographyParserException(
            context.row,
            config.obs_separator.join(values) if isinstance(values, list) else values,
            'point category',
            '|'.join(mappings.cartography_point_category.keys())
        )
    return dft_value, None
