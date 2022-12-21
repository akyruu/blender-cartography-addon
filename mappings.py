"""
Mappings for parsing
"""

from typing import List

import config
from model import CartographyCategory, CartographyInterestType, CartographyObjectType


# INTERNAL ====================================================================
def __build_regex(words: List[str], has_number: bool) -> str:
    return '(' + '|'.join(words) + ')' + (' ([0-9]+)' if has_number else '')


# CONFIG ======================================================================
# Cartography: join word for name concatenation
cartography_point_name_join = ' - '

# Type of cartography points
__category_words = config.mappings.words.category
cartography_point_category = {
    # TODO move to "mapping"
    # Structure
    __build_regex(__category_words['OUTLINE'], False): CartographyCategory.OUTLINE,
    __build_regex(__category_words['GATE'], True): CartographyCategory.GATE,
    __build_regex(__category_words['ESCARPMENT'], True): CartographyCategory.ESCARPMENT,
    __build_regex(__category_words['BASEMENT'], True): CartographyCategory.BASEMENT,
    __build_regex(__category_words['LANDING'], True): CartographyCategory.LANDING,
    __build_regex(__category_words['COLUMN'], True): CartographyCategory.COLUMN,
    __build_regex(__category_words['COLUMN_BASE'], True): CartographyCategory.COLUMN_BASE,
    __build_regex(__category_words['CHASM'], True): CartographyCategory.CHASM,
    # Obstacle
    __build_regex(__category_words['BANK'], False): CartographyCategory.BANK,
    # Interest
    __build_regex(__category_words['CLIMBING_POINT'], False): CartographyCategory.CLIMBING_POINT,
    __build_regex(__category_words['HARVESTABLE'], False): CartographyCategory.HARVESTABLE,
    __build_regex(__category_words['ANTHROPOGENIC_OBJECT'], False): CartographyCategory.ANTHROPOGENIC_OBJECT,
    __build_regex(__category_words['STRUCTURE'], False): CartographyCategory.STRUCTURE
}

# Cartography: pattern for determinate a junction
cartography_junction_pattern = '(Jonction|Junction) .+ (' + '|'.join(cartography_point_category.keys()) + ')'

# Type of cartography interest
__category_words = config.mappings.words.interest_type
cartography_interest_type = {
    # TODO move to "mapping"
    __build_regex(__category_words['LITTLE_BOX'], False): CartographyInterestType.LITTLE_BOX,
    __build_regex(__category_words['LICHEN'], False): CartographyInterestType.LICHEN,
    __build_regex(__category_words['ORE'], False): CartographyInterestType.ORE
}

# Type of cartography points
cartography_object_type = {
    # TODO move to "config" ?
    # Point categories
    CartographyCategory.OUTLINE: 'contour',
    CartographyCategory.GATE: 'Gate',
    CartographyCategory.ESCARPMENT: 'elevation',
    CartographyCategory.BASEMENT: 'elevation',
    CartographyCategory.COLUMN: 'colonne',
    CartographyCategory.CHASM: 'gouffre',
    CartographyCategory.CLIMBING_POINT: 'escalade',
    CartographyCategory.HARVESTABLE: 'ico_feces_Pilier',
    CartographyCategory.ANTHROPOGENIC_OBJECT: None,
    CartographyCategory.UNKNOWN: 'ico_unknown_Pilier',

    # Interest types
    CartographyInterestType.BOX: 'Caisse_1',
    CartographyInterestType.LITTLE_BOX: 'Caisse_1.001',
    CartographyInterestType.LICHEN: 'ico_lichen_Ico',
    CartographyInterestType.ORE: 'ico_handMining_Ico',
    CartographyInterestType.UNKNOWN: 'ico_unknown_Ico',

    # Object types
    CartographyObjectType.PLANE: 'Plane'
}

# Material for specific items
cartography_mat_wall = 'rock_cliff'
cartography_mat_climbing = 'escalade'
