"""
Mappings

History:
2020/08/21: v0.0.1
    + add utility methods for bmesh/mesh conversion
"""

from bca_types import CartographyCategory, CartographyInterestType, CartographyObjectType

# CONFIG ======================================================================
# Cartography: join word for name concatenation
cartography_point_name_join = ' - '

# Type of cartography points
cartography_point_category = {
    '(Outline|Contour)': CartographyCategory.OUTLINE,
    '(Gate|Porte|Entrée) ([0-9]+)': CartographyCategory.GATE,
    '(Escarpment|Escarpement) ([0-9]+)': CartographyCategory.ESCARPMENT,
    '(Column|Colonne) ([0-9]+)': CartographyCategory.COLUMN,
    '(Chasm|Gouffre) ([0-9]+)': CartographyCategory.CHASM,
    '(Climbing ?Point|Point( d[\'’ ]?)?escalade)': CartographyCategory.CLIMBING_POINT,
    '(Harvestables?|Consommables?)': CartographyCategory.HARVESTABLE,
    '((Anthropogenics? )?Objects?|Objets?( Anthropiques?))': CartographyCategory.ANTHROPOGENIC_OBJECT
}

# Cartography: pattern for determinate a junction
cartography_junction_pattern = '(Jonction|Junction) .+ (' + '|'.join(cartography_point_category.keys()) + ')'

# Type of cartography interest
cartography_interest_type = {
    '(Box(es)?|Caisses?)': CartographyInterestType.BOX,
    'Lichens?': CartographyInterestType.LICHEN,
    '(Ores?|Minerai?)': CartographyInterestType.ORE
}

# Type of cartography points
cartography_object_type = {
    # Point categories
    CartographyCategory.OUTLINE: 'contour',
    CartographyCategory.GATE: 'Gate',
    CartographyCategory.ESCARPMENT: 'elevation',
    CartographyCategory.COLUMN: 'colonne',
    CartographyCategory.CHASM: 'gouffre',
    CartographyCategory.CLIMBING_POINT: 'escalade',
    CartographyCategory.HARVESTABLE: 'ico_feces_Pilier',
    CartographyCategory.ANTHROPOGENIC_OBJECT: None,

    # Interest types
    CartographyInterestType.BOX: 'Caisse_1.001',
    CartographyInterestType.LICHEN: 'ico_lichen_Ico',
    CartographyInterestType.ORE: 'ico_handMining_Ico',

    # Object types
    CartographyObjectType.PLANE: 'Plane'
}
