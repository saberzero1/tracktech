import json
import random
import os
import sys


def load_data(datatype, nr=None):
    """Load a JSON test data file of chosen type.

    Args:
        - A string, which is one of these options: {'boundingBoxes', 'start', 'stop', 'featureMap', 'invalid'}
        - A number which defaults to None. If it is not None, it will load 'nr' random json objects

    Returns:
        A dictionary of test data of the chosen JSON message type
    """
    switcher = {
        'boundingBoxes': 'boxes',
        'start': 'start',
        'stop': 'stop',
        'featureMap': 'featuremaps',
        'invalid': 'invalid'
    }
    filename = switcher.get(datatype)
    if filename is None:
        raise NameError('The JSON object requested is not in scope.')
    else:
        cd = os.path.join(sys.path[0], f'tests/integrationtests/testdata/{filename}.json')
        f = open(cd, encoding="utf-8")
        jfile = json.load(f)
        if nr == 'all':
            return json.dumps(jfile)
        if nr is not None:
            d = []
            for i in range(nr):
                d.append(json.dumps(random.choice(jfile)))
            return d
        else:
            return jfile