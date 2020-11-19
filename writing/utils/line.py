"""
Module for treat lines
"""

from typing import List, TextIO

from reading import CartographyFileLine


# METHODS =====================================================================
def write_obj(line: CartographyFileLine, output: TextIO):
    output.write(line.text + '\n')


def write(sep: str, args: List[str], output: TextIO):
    output.write(sep.join(args) + '\n')
