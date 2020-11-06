"""
Module for treat groups
"""

import re
from typing import Optional, Tuple

import config
import utils
from model import CartographyCategory, CartographyGroup, CartographyRoom
from parsing.__model import ParseContext
from reading import CartographyFilePoint
from . import category as category_utils
from ..exception import CartographyParserException


# METHODS =====================================================================
def find_group(
        context: ParseContext,
        partial_name: str,
        category: CartographyCategory,
        room: CartographyRoom
) -> Optional[CartographyGroup]:
    groups = [
        g for g in room.groups.values()
        if g.category == category and utils.string.match_ignore_case(partial_name, g.name, False)
    ]
    count = len(groups)
    if count > 1:
        context.logger.warning('Too much group found for name <%s>: current=<%d> expected=<%d>', partial_name, count, 1)
        return None
    return groups[0] if count == 1 else None


def get_or_create_group(context: ParseContext, point: CartographyFilePoint) -> CartographyGroup:
    name, category = determinate_group_name_category(context, point)
    group = context.room.groups.get(name, None)
    if group is None:
        context.logger.debug('Create new group <%s>', name)
        group = CartographyGroup(name, category)
        context.room.groups[name] = group

        if group.category.outline:
            if context.room.outline_group is not None and context.room.outline_group != group:
                raise CartographyParserException(
                    context.row,
                    group.name,
                    'group category',
                    'Only one outline for each room'
                )
            context.room.outline_group = group
    else:
        context.logger.debug('Use existing group <%s>', name)
    return group


def determinate_group_name_category(context, point: CartographyFilePoint) -> Tuple[str, CartographyCategory]:
    categories = category_utils.parse_point_categories(', '.join(point.observations))
    if len(categories) == 0:
        raise ValueError('Category not found in <' + ', '.join(point.observations) + '>')
    elif len(categories) > 1:
        category_types = [c for c, m in categories]
        if CartographyCategory.OUTLINE in category_types and CartographyCategory.GATE in category_types:
            category, cat_match = next((c, m) for c, m in categories if c == CartographyCategory.OUTLINE)
        else:
            category, cat_match = categories[0]
        context.logger.warning(
            'Group - Multiple category found: <%s>. Use category: <%s> (observations: <%s>)',
            ','.join([c.name for c, m in categories]),
            category.name,
            ', '.join(point.observations)
        )
    else:
        category, cat_match = categories[0]

    return cat_match.group(0), category


def match_category_in_observation(pattern: str, value: str) -> re.Match:
    m = utils.string.match_ignore_case(pattern, value, True)
    if not m:
        pattern = '(?!(' + '|'.join(config.mappings.words['proximity']) + ').)* ' + pattern
        m = utils.string.match_ignore_case(pattern, value, True)
        if not m:
            pattern += '.*'
            m = utils.string.match_ignore_case(pattern, value, True)
    return m
