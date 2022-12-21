"""
Module for treat lines
"""

import re

import utils
from ..exception import CartographyReaderException
from ..model import ReadContext


# METHODS =====================================================================
def check(
        context: ReadContext, line: str, line_type: str, patterns: list,
        strict=True, ignore_reduced=False, log_warns=True
):
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
        elif log_warns:
            context.logger.warning('Insufficient data count for line #%d: %d < %d', context.row, data_count, count)
            context.logger.debug(
                'Insufficient data count for line #%d:'
                '\n\tpattern: [count: <%d>, data: <%s>]'
                '\n\tline: [count: <%d>, data: <%s>]',
                context.row,
                count, utils.io.file.format_line_for_logging(context.separator.join(patterns)),
                data_count, utils.io.file.format_line_for_logging(context.separator.join(data))
            )
        return None
    elif data_count > count and not ignore_reduced:
        context.logger.warning('Data ignored for line <%d>: <%d> column(s) ignored', context.row, data_count - count)
        context.logger.debug(
            'Data ignored for line <%d> (case insensitive):'
            '\n\tpattern: [count: <%d>, data: <%s>]'
            '\n\tline: [count: <%d>, data: <%s>]',
            context.row,
            count, utils.io.file.format_line_for_logging(context.separator.join(patterns)),
            data_count, utils.io.file.format_line_for_logging(context.separator.join(data))
        )

    # Check data
    for i in range(count):
        context.column = i + 1
        pattern = patterns[i] if patterns[i] else '^$'
        value = data[i]
        m = utils.string.match_ignore_case(pattern, value)
        if m is None:
            if strict:
                raise CartographyReaderException(context.row, context.column, value, line_type, pattern)
            elif log_warns:
                context.logger.warning(
                    'Data <%d> ignored for line <%d>: <%s> not match with <%s>',
                    context.column, context.row, value, pattern
                )
            return None
        matches.append(m)

    return matches


def ignore(context: ReadContext, line: str):
    context.logger.info('Ignore <%s> (l.%d)', utils.io.file.format_line_for_logging(line), context.row)
