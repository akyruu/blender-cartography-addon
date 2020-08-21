"""
Mappings

History:
2020/08/21: v0.0.1
    + add utility methods for bmesh/mesh conversion
"""

from bca_types import CartographyPointCategory, CartographyInterestType, CartographyObjectType

# CONFIG ======================================================================
# Type of cartography points
cartography_point_category = {
    '(Outline|Contour)': CartographyPointCategory.OUTLINE,
    '(Gate|Porte|Entrée) ([0-9]+)': CartographyPointCategory.GATE,
    '(Escarpment|Escarpement) ([0-9]+)': CartographyPointCategory.ESCARPMENT,
    '(Column|Colonne) ([0-9]+)': CartographyPointCategory.COLUMN,
    '(Chasm|Gouffre) ([0-9]+)': CartographyPointCategory.CHASM,
    '(Climbing ?Point|Point( d[\'’ ]?)?escalade)': CartographyPointCategory.CLIMBING_POINT,
    '(Harvestables?|Consommables?)': CartographyPointCategory.HARVESTABLE,
    '((Anthropogenics? )?Objects?|Objets?( Anthropiques?))': CartographyPointCategory.ANTHROPOGENIC_OBJECT
}

# Type of cartography interest
cartography_interest_type = {
    '(Box(es)?|Caisses?)': CartographyInterestType.BOX,
    'Lichens?': CartographyInterestType.LICHEN,
    '(Ores?|Minerai?)': CartographyInterestType.ORE
}

# Type of cartography points
cartography_object_type = {
    # Point categories
    CartographyPointCategory.OUTLINE: 'contour',
    CartographyPointCategory.GATE: 'Gate',
    CartographyPointCategory.ESCARPMENT: 'elevation',
    CartographyPointCategory.COLUMN: 'colonne',
    CartographyPointCategory.CHASM: 'gouffre',
    CartographyPointCategory.CLIMBING_POINT: 'escalade',
    CartographyPointCategory.HARVESTABLE: 'ico_feces_Pilier',
    CartographyPointCategory.ANTHROPOGENIC_OBJECT: None,

    # Interest types
    CartographyInterestType.BOX: 'Caisse_1.001',
    CartographyInterestType.LICHEN: 'ico_lichen_Ico',
    CartographyInterestType.ORE: 'ico_handMining_Ico',

    # Object types
    CartographyObjectType.PLANE: 'Plane'
}
