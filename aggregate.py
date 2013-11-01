from settings import *
from collections import defaultdict
import inspect
import json
import os
import copy
import decimal
import argparse
import statsfunctions

parser = argparse.ArgumentParser()
parser.add_argument("--stats-module", help="Name of module to import stats from", default='stats')
args = parser.parse_args()

import importlib
stats = importlib.import_module(args.stats_module)


def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def dict_sum_inplace(d1, d2):
    for k,v in d2.items():
        if type(v) == dict or type(v) == defaultdict:
            dict_sum_inplace(d1[k], v)
        elif d1[k] is None:
            continue
        else:
            d1[k] += v

def make_blank():
    blank = {}
    for stats_object in [ stats.ActivityStats(), stats.ActivityFileStats(), stats.PublisherStats() ]:
        stats_object.blank = True
        for name, function in inspect.getmembers(stats_object, predicate=inspect.ismethod):
            if not statsfunctions.use_stat(stats_object, name): continue
            blank[name] = function()
    return blank

if __name__ == '__main__':
    blank = make_blank()
    total = copy.deepcopy(blank)
    for folder in os.listdir(OUTPUT_DIR):
        subtotal = copy.deepcopy(blank)

        for jsonfile in os.listdir(os.path.join(OUTPUT_DIR, folder)):
            with open(os.path.join(OUTPUT_DIR, folder, jsonfile)) as jsonfp:
                stats_json = json.load(jsonfp, parse_float=decimal.Decimal)
                for activity_json in stats_json['activities']:
                    dict_sum_inplace(subtotal, activity_json)
                dict_sum_inplace(subtotal, stats_json['file'])

        publisher_stats = stats.PublisherStats()
        publisher_stats.aggregated = subtotal
        for name, function in inspect.getmembers(publisher_stats, predicate=inspect.ismethod):
            if statsfunctions.use_stat(publisher_stats, name): continue
            subtotal[name] = function()

        dict_sum_inplace(total, subtotal)
        with open(os.path.join('aggregated', folder+'.json'), 'w') as fp:
            json.dump(subtotal, fp, sort_keys=True, indent=2, default=decimal_default)

    with open('aggregated.json', 'w') as fp:
        json.dump(total, fp, sort_keys=True, indent=2, default=decimal_default)

