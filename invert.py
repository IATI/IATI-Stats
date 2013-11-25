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
                        if type(v) == dict:
                            if not k in out[stats_name]:
                                out[stats_name][k] = defaultdict(list)
                            for k2,v2 in v.items():
                                out[stats_name][k][k2].append(f[:-5])
                        else:
                            out[stats_name][k].append(f[:-5])

    with open('inverted.json', 'w') as fp:
        json.dump(out, fp, sort_keys=True, indent=2)

def invert_file():
    out = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for d in os.listdir('out'):
        for f in os.listdir(os.path.join('out',d)):
            with open(os.path.join('out',d,f)) as fp:
                for stats_name,stats_values in json.load(fp)['file'].items():
                    if type(stats_values) == dict:
                        for k,v in stats_values.items():
                            out[stats_name][k][d].append(f[:-5])

    with open('inverted-file.json', 'w') as fp:
        json.dump(out, fp, sort_keys=True, indent=2)


if __name__ == '__main__':
    invert()
    invert_file()
