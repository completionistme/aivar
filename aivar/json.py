import codecs
import json

import numpy as np

from aivar.logger import success


def store_json(payload, file):
    # store the whole result to json to be worked with somewhere else
    def default(o):
        if isinstance(o, np.int64): return int(o)
        raise TypeError

    json.dump(payload, codecs.open(file, 'w', encoding='utf-8'), separators=(',', ':'),
              sort_keys=True, indent=4, default=default)
    success('stored to ' + file)