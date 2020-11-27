"""
Module for treat groups
"""

import re
from typing import List, Optional, Tuple

import config
import utils
from model import CartographyCategory, CartographyGroup, CartographyRoom
from parsing.model import ParseContext
from . import category as category_utils


# METHODS =====================================================================
def find(context: ParseContext, partial_name: str, category: CartographyCategory, room: CartographyRoom) \
        -> Optional[CartographyGroup]:
    groups = [
        g for g in room.groups.values()
        if g.category == category and utils.string.match_ignore_case(partial_name, g.name, False)
    ]
    count = len(groups)
    if count > 1:
        context.logger.warning('Too much group found for name <%s>: current=<%d> expected=<%d>', partial_name, count, 1)
        return None
    return groups[0] if count == 1 else None


def get_or_create(context: ParseContext, observations: List[str]) -> CartographyGroup:
    name, category = __determinate_group_name_category(context, observations)
    group = context.room.groups.get(name, None)
    if not group:
        if category.outline:
            group = context.room.outline_group
        if not group:
            context.logger.debug('Create new group <%s>', name)
            group = CartographyGroup(name, category)
            context.room.groups[name] = group

            if category.outline:
                context.room.outline_group = group
    else:
        context.logger.debug('Use existing group <%s>', name)
    return group


def __determinate_group_name_category(context, observations: List[str]) -> Tuple[str, CartographyCategory]:
    categories = category_utils.parse_categories(observations)
    if len(categories) == 0:
        category = CartographyCategory.UNKNOWN
        name = category.name
        context.logger.warning(
            'Category not found in <%s>. Use category: <%s>',
            config.obs_separator.join(observations), category.name
        )
    elif len(categories) > 1:
        category_types = [c for c, m in categories]
        if CartographyCategory.OUTLINE in category_types and CartographyCategory.GATE in category_types:
            category = CartographyCategory.OUTLINE
            name = category.name
        else:
            category, cat_match = categories[0]
            name = cat_match.group(0)
        context.logger.warning(
            'Group - Multiple category found: <%s>. Use category: <%s> (observations: <%s>)',
            ','.join([c.name for c, m in categories]),
            category.name,
            config.obs_separator.join(observations)
        )
    else:
        category, cat_match = categories[0]
        if category.outline:
            category = CartographyCategory.OUTLINE
            name = CartographyCategory.OUTLINE.name
        else:
            name = cat_match.group(0)

    return name.strip().capitalize(), category


def match_category_in_observation(pattern: str, value: str) -> re.Match:
    m = utils.string.match_ignore_case(pattern, value, True)
    if not m:
        pattern = '(?!(' + '|'.join(config.mappings.words['proximity']) + ').)* ' + pattern
        m = utils.string.match_ignore_case(pattern, value, True)
        if not m:
            pattern += '.*'
            m = utils.string.match_ignore_case(pattern, value, True)
    return m
