"""
Mappings for parsing about categories
"""

from model import CartographyCategory
from . import utils as config_utils

# CONFIG ======================================================================
# Type of cartography points
by_pattern = config_utils.pattern.config({
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
