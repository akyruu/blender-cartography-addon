"""
Configuration for template
"""

from model import CartographyCategory, CartographyInterestType, CartographyObjectType
from . import utils as config_utils
from .model import CartographyTemplateConfigItem

# CONFIG ======================================================================
# Material for specific items
material_wall = 'rock_cliff'
material_climbing = 'escalade'

# Name of object in blender utils for categories
by_category = config_utils.template.config('category', {
    # Structure
    CartographyCategory.OUTLINE: 'contour',
    CartographyCategory.GATE: 'Gate',
    CartographyCategory.ESCARPMENT: 'elevation',
    CartographyCategory.BASEMENT: 'elevation',
    CartographyCategory.COLUMN: 'colonne',
    # Obstacle
    CartographyCategory.CHASM: 'gouffre',
    # Interests
    CartographyCategory.CLIMBING_POINT: CartographyTemplateConfigItem('escalade', -1.5),
    CartographyCategory.HARVESTABLE: 'ico_feces_Pilier',
    CartographyCategory.ANTHROPOGENIC_OBJECT: None,
    CartographyCategory.UNKNOWN: 'ico_unknown_Pilier'
})

# Name of object in blender utils for interests
by_interest_type = config_utils.template.config('interest type', {
    # Object
    CartographyInterestType.BOX: 'Caisse_1',
    CartographyInterestType.LITTLE_BOX: 'Caisse_1.001',
    # Harvestable
    CartographyInterestType.LICHEN: 'ico_lichen_Ico',
    CartographyInterestType.FECES: 'ico_feces_Ico',
    CartographyInterestType.ORE: 'ico_handMining_Ico',
    CartographyInterestType.UNKNOWN: 'ico_unknown_Ico'
})

# Name of object in blender utils for object types
by_object_type = config_utils.template.config('object type', {
    CartographyObjectType.PLANE: 'Plane'
})
