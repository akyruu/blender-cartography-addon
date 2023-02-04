"""
Module for utility string (str) methods
"""

import re


# METHODS =====================================================================
def match_ignore_case(pattern: str, value: str, exact: bool = True) -> re.Match:
    flags = re.IGNORECASE

    m = re.match(pattern, value, flags)
    if m is None and not exact:
        m = re.match(pattern + '.*', value, flags)
        if m is None:
            m = re.match('.*' + pattern + '.*', value, flags)
    return m


def to_string(value: any) -> str:
    return '' if value is None else str(value)
