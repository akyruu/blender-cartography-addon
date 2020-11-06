import os

import utils

words = utils.io.file.read_json(os.path.join(os.path.dirname(os.path.realpath(__file__)), 'mappings_words.json'))
