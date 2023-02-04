"""
Mappings for parsing about categories
"""

from model import CartographyCategory
from .common import __to_value_by_patterns

# CONFIG ======================================================================
# Type of cartography points
by_pattern = __to_value_by_patterns({
    CartographyCategory.OUTLINE: ["Outline", "Contour"],
    CartographyCategory.GATE: ["Gate", "Porte", "Entr[ée]e"],
    CartographyCategory.ESCARPMENT: ["Escarpment", "Escarpement"],
    CartographyCategory.BASEMENT: ["Basement", "Sou(s-)?bassement"],
    CartographyCategory.LANDING: ["Landing", "Plateau"],
    CartographyCategory.COLUMN: ["Column", "Colonn?e", "Pilier"],
    CartographyCategory.COLUMN_BASE: ["Column base", "Base colonn?e", "Base pilier"],
    CartographyCategory.CHASM: ["Chasm", "Gouffre"],
    CartographyCategory.BANK: ["Bank", "Talus( de pierr?e)?", "[Eé]bouli"],
    CartographyCategory.RECESS: ["Recess", "Renfoncement"],
    CartographyCategory.CLIMBING_POINT: ["Climbing ?Point", "Point( d['’ ]?)?escalade"],
    CartographyCategory.HARVESTABLE: ["Harvestables?", "Consommables?"],
    CartographyCategory.ANTHROPOGENIC_OBJECT: ["(Anthropogenics? )?Objects?", "Objets?( Anthropiques?)?"],
    CartographyCategory.STRUCTURE: ["Structure"]
})

# Cartography: pattern for determinate a junction
cartography_junction_pattern = '(Jonction|Junction) .+ (' + '|'.join(by_pattern.keys()) + ')'
