from typing import Dict, List

from utils.common import T


# INTERNAL ====================================================================
def __join_patterns(patterns: List[str]) -> str:
    return f"({'|'.join(patterns)})"


def __to_value_by_patterns(patterns_by_value: Dict[T, List[str]]) -> Dict[str, T]:
    return {__join_patterns(patterns): value for value, patterns in patterns_by_value.items()}


# CONFIG ======================================================================
# Cartography: join word for name concatenation
cartography_point_name_join = ' - '

proximity = __join_patterns(["proximity", "near", "proximité", "proche"])
