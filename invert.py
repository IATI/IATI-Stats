import json
import os, sys
from collections import defaultdict

def invert():
    """
    This 'inverts' the aggregated json files produced by aggregate.py
    ie. it creates a json file of the stats grouped by value, and then by
    publisher.

    """
    out = defaultdict(lambda: defaultdict(list))

    for f in os.listdir('aggregated'):
        with open(os.path.join('aggregated',f)) as fp:
            for stats_name,stats_values in json.load(fp).items():
                if type(stats_values) == dict:
                    for k,v in stats_values.items():
                        out[stats_name][k].append(f[:-5])

    with open('inverted.json', 'w') as fp:
        json.dump(out, fp, sort_keys=True, indent=2)


if __name__ == '__main__':
    invert()
