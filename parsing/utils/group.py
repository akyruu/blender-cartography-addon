"""
Module for treat groups
"""

import re
from typing import List, Optional, Tuple

import config
import utils
from model import CartographyCategory, CartographyGroup, CartographyRoom
from parsing.model import ParseContext


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


def get_or_create(context: ParseContext, category: CartographyCategory, category_number: int = 0) -> CartographyGroup:
    name = category.name + (f' {category_number}' if category_number else '')
    group = context.room.groups.get(name, None)
    if not group:
        if category.options.outline:
            group = context.room.outline_group
        if not group:
            context.logger.debug('Create new group <%s>', name)
            group = CartographyGroup(name, category, category_number)
            context.room.groups[name] = group

            if category.options.outline:
                context.room.outline_group = group
    else:
        context.logger.debug('Use existing group <%s>', name)
    return group


def __determinate_group_name_category(
        context,
        categories: List[CartographyCategory],
        category_number: int
) -> Tuple[str, CartographyCategory]:
    if len(categories) == 0:
        category = CartographyCategory.UNKNOWN
        name = category.name
        context.logger.warning('Category not found. Use category: <%s>', category.name)
    elif len(categories) > 1:
        category_types = [c for c in categories]
        if CartographyCategory.OUTLINE in category_types and CartographyCategory.GATE in category_types:
            category = CartographyCategory.OUTLINE
            name = category.name
        else:
            category = categories[0]
            name = category.name + (f' {category_number}' if category_number else '')
        context.logger.warning(
            'Group - Multiple category found: <%s>. Use category: <%s>',
            ','.join([c.name for c in categories]), category.name
        )
    else:
        category = categories[0]
        if category.options.outline:
            category = CartographyCategory.OUTLINE
            name = CartographyCategory.OUTLINE.name
        else:
            name = category.name + (f' {category_number}' if category_number else '')

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
