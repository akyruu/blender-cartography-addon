"""
Module for treat lines
"""
import logging
import re
from typing import Optional, List, Dict

import utils
from ..exception import CartographyReaderException
from ..model import ReadContext


# TYPES =======================================================================
class DataMapField:
    """Data map field after extraction"""

    def __init__(self, name: str, value: str):
        self.name = name
        self.value = value

    def value_to_int(self, default_value: int = 0) -> int:
        return int(self.value) if self.value else default_value


# METHODS =====================================================================
def check(
        context: ReadContext,
        line: str, line_type: str,
        patterns: List[str], names: List[str] = None,
        strict=True, ignore_extra_data=False, log_error=True
) -> Optional[List[re.Match]]:
    matches = []

    # Split line
    data = line.split(context.separator)
    data_count = len(data)

    # Check number of columns
    patterns_count = len(patterns)
    if data_count < patterns_count:
        if strict:
            context.column = 1
            raise CartographyReaderException(
                context.row,
                context.column,
                line,
                line_type,
                context.separator.join(patterns)
            )
        if log_error:
            __debug_log_pattern_current_diff(
                f'Missing data for line <{context.row}>: {data_count}/{patterns_count}',
                context, patterns, data, names
            )
        return None
    elif data_count > patterns_count and not ignore_extra_data:
        context.logger.warning(
            'Data ignored for line <%d>: <%d> last column(s) ignored',
            context.row, data_count - patterns_count
        )
        if log_error:
            __debug_log_pattern_current_diff(
                f'Details of previous WARNING message',
                context, patterns, data, names
            )

    # Check data
    count = min(data_count, patterns_count)
    for i in range(count):
        context.column = i + 1
        pattern = patterns[i] or '^.*$'
        value = data[i]
        m = utils.string.match_ignore_case(pattern, value)
        if m is None:
            if strict:
                raise CartographyReaderException(context.row, context.column, value, line_type, pattern)
            if log_error:
                __debug_log_pattern_current_diff(
                    f'Column {context.column} of line {context.row} not match!',
                    context, patterns, data, names
                )
            return None
        matches.append(m)

    return matches


def extract_data_map(context: ReadContext, line: str, names: List[str]) -> Dict[str, DataMapField]:
    data_map = {}

    data = line.split(context.separator)
    for index, name in enumerate(names):
        if name:
            data_map[name] = DataMapField(name, data[index])

    return data_map


def __debug_log_pattern_current_diff(
        message: str, context: ReadContext,
        patterns: List[str], data: List[str], names: List[str]
):
    if context.logger.isEnabledFor(logging.DEBUG):
        patterns_count = len(patterns)
        data_count = len(data)
        names_count = len(names)
        max_count = max(patterns_count, data_count, names_count)
        context.logger.debug(
            f'{message}:\n%s',
            utils.logging.build_table([
                f'Line #{context.row}',
                *[f'{n} (c{(i + 1):02})' for i, n in enumerate(names)],
                *[f'c{(i + 1):02}' for i in range(names_count, max_count)]
            ], [
                ['Pattern', *patterns, *([''] * (max_count - patterns_count))],
                ['Line', *data, *([''] * (max_count - data_count))]
            ])
        )


def ignore(context: ReadContext, line: str):
    context.logger.info('Ignore <%s> (l.%d)', utils.io.file.format_line_for_logging(line), context.row)
