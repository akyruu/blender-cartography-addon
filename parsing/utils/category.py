"""
Module for category methods relative to parsing
"""

from typing import Optional

import utils
from model import CartographyCategory, CartographyCategoryType
from parsing import config as parse_config
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
    categories = [category for pattern, category in parse_config.category.by_pattern.items()
                  if utils.string.match_ignore_case(pattern, category_label)]
    categories_len = len(categories)
    if categories_len == 0:
        category = dft_value
    elif categories_len == 1:
        category = categories[0]
    else:
        raise Exception('Invalid mapping configuration: too much categories {} found for <{}>'
                        .format(category_label, str(parse_config.category.by_pattern.keys())))

    if category is None and required:
        raise CartographyParserException(
            context.row,
            category_label,
            'point category',
            '|'.join(parse_config.category.by_pattern.keys())
        )
    return category
