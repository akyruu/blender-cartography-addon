import os
from typing import Dict, List

import utils


# TYPES =======================================================================
class Words:
    """Word to use for mapping text to type"""
    category: Dict[str, List[str]] = {}
    interest_type: Dict[str, List[str]] = {}
    proximity: List[str] = []

    def __repr__(self):
        return self.__dict__.__repr__()


# CONFIG ======================================================================
words = utils.object.to_class(utils.io.file.read_json(
    os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mappings_words.json'),
), Words)
print('[Config] Mappings - Words: {}', words)
