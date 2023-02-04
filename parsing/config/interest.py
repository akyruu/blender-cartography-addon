"""
Mappings for parsing about interests
"""

from model import CartographyInterestType
from .common import __to_value_by_patterns

# CONFIG ======================================================================
# Type of cartography interest
by_pattern = __to_value_by_patterns({
    # Objects
    CartographyInterestType.LITTLE_BOX: ["Littles? box(es)?", "Petites? caisses?"],
    CartographyInterestType.BOX: ["Big box(es)?", "Grosses? caisses?"],
    # Harvestable
    CartographyInterestType.LICHEN: ["Lichens?"],
    CartographyInterestType.ORE: ["Ores?", "Minerai?"],
    CartographyInterestType.FECES: ["Ores?", "Minerai?"]
})
