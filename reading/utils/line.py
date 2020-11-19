"""
Module for treat lines
"""

import re

import utils
from ..exception import CartographyReaderException
from ..model import ReadContext


# METHODS =====================================================================
def check(context: ReadContext, line: str, line_type: str, patterns: list, strict=True, ignore_reduced=False):
    matches = []

    # Split line
    data = line.split(context.separator)
    data_count = len(data)

    # Determine columns count
    patterns_count = len(patterns)
    columns = patterns_count
    while columns > 0 and (not patterns[columns - 1] or re.match('\\(.+\\)\\?', patterns[columns - 1])):
        columns -= 1
    count = min(max(data_count, columns), patterns_count)

    # Check number of columns
    if data_count < count:
        if strict:
            context.column = 1
            raise CartographyReaderException(
                context.row,
                context.column,
                line,
                line_type,
                context.separator.join(patterns)
            )
        return None
    elif data_count > count and not ignore_reduced:
        context.logger.warning('Data ignored for line "<%d>": ' + str(data_count - count) + ' column(s) ignored')
        context.logger.debug(
            'Data ignored for line "<%d>":\n\tcurrent: [count: <%d>, data: <%s>]\n\texpected: [count: <%d>, data: <%s>]',
            context.row, data_count, ', '.join(data), count, ', '.join(patterns)
        )

    # Check data
    print('########')
    for i in range(count):
        context.column = i + 1
        pattern = patterns[i] if patterns[i] else '^$'
        value = data[i]
        m = utils.string.match_ignore_case(pattern, value)
        print(pattern, '/', value, '->', m)
        if m is None:
            if strict:
                raise CartographyReaderException(context.row, context.column, value, line_type, pattern)
            return None
        matches.append(m)

    print('---------')
    return matches


def ignore(context: ReadContext, line: str):
    context.logger.info('Ignore <%s> (l.%d)', utils.io.file.format_line_for_logging(line), context.row)
