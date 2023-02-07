from typing import Dict, List

from utils.common import T


# INTERNAL ====================================================================
def config(patterns_by_value: Dict[T, List[str]]) -> Dict[str, T]:
    return {f"({'|'.join(patterns)})": value for value, patterns in patterns_by_value.items()}
