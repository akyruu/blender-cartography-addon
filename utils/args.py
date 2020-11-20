"""
Module for utility blender system methods
"""

import sys
from argparse import ArgumentParser
from typing import List

# VARIABLES ===================================================================
__arg_parser = ArgumentParser()


# METHODS =====================================================================
def add(name_or_flags: str, action: str, _type: any, _help: str):
    __arg_parser.add_argument(name_or_flags, action, type=_type, help=_help)


def get() -> List[str]:
    index = sys.argv.index('--')
    return sys.argv[index + 1:] if index > 0 else sys.argv


def parse() -> any:
    argv = get()
    args, unknown = __arg_parser.parse_known_args(argv)
    return args
