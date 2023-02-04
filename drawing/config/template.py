"""
Mappings for drawing
"""

from typing import Dict, List

import utils
from model import CartographyCategory, CartographyInterestType, CartographyObjectType
from utils.common import T


# INTERNAL ====================================================================
def __join_maps(maps: List[Dict[any, T]]) -> Dict[any, T]:
    items = utils.collection.list.flat_map(lambda m: m.items(), maps)
    return {k: v for k, v in items}


# CONFIG ======================================================================
# Name of object in blender template for categories
__by_category = {
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
}

# Name of object in blender template for interests
__by_interest = {
    CartographyInterestType.BOX: 'Caisse_1',
    CartographyInterestType.LITTLE_BOX: 'Caisse_1.001',
    CartographyInterestType.LICHEN: 'ico_lichen_Ico',
    CartographyInterestType.ORE: 'ico_handMining_Ico',
    CartographyInterestType.UNKNOWN: 'ico_unknown_Ico',
}

# Name of object in blender template for object types
__by_object_type = {
    CartographyObjectType.PLANE: 'Plane'
}

by_object = __join_maps([__by_category, __by_interest, __by_object_type])

# Material for specific items
material_wall = 'rock_cliff'
material_climbing = 'escalade'
