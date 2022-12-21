"""
Module for utility logging methods
"""

from typing import List


# METHODS =====================================================================
def build_table(header: List[str], data: List[List[any]]) -> str:
    # Determine max size of each column
    max_sizes = [max(len(h), 3) for h in header]
    for row in data:
        for i, column in enumerate(row):
            max_sizes[i] = max(len(column), max_sizes[i])
    # Build line templates
    col_sep = ' | '
    line_format = col_sep.join(['{:<' + str(ms) + '}' for ms in max_sizes])
    sep_line = '-' * (sum(max_sizes) + (len(col_sep) * len(max_sizes)))

    # Write lines
    lines = [
        sep_line,
        line_format.format(*header),
        sep_line
    ]
    for row in data:
        lines.append(line_format.format(*row))
    lines.append(sep_line)

    return '\n'.join(lines)
