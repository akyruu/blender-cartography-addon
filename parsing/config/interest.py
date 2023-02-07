"""
Mappings for parsing about interests
"""

from model import CartographyInterestType
from . import utils as config_utils

# CONFIG ======================================================================
# Type of cartography interest
by_pattern = config_utils.pattern.config({
    # Objects
    CartographyInterestType.LITTLE_BOX: ["Littles? box(es)?", "Petites? caisses?"],
    CartographyInterestType.BOX: ["Big box(es)?", "Grosses? caisses?"],
    # Harvestable
    CartographyInterestType.LICHEN: ["Lichens?"],
    CartographyInterestType.ORE: ["Ores?", "Minerai?"],
    CartographyInterestType.FECES: ["Feces?", "(Mati[ère]s? )?f[ée]cale?s?|Extr[ée]ments"]
})
