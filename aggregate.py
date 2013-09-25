from settings import *
from collections import defaultdict
import inspect
import json
import os
import copy

def dict_sum_inplace(d1, d2):
    for k,v in d2.items():
        if type(v) == dict or type(v) == defaultdict:
            dict_sum_inplace(d1[k], v)
        elif d1[k] is None:
            continue
        else:
            d1[k] += v

blank = {}
import stats
for stats_object in [ stats.ActivityStats(blank=True), stats.PublisherStats(blank=True) ]:
    for name, function in inspect.getmembers(stats_object, predicate=inspect.ismethod):
        if name.startswith('_'): continue
        blank[name] = function()

total = copy.deepcopy(blank)

for folder in os.listdir(OUTPUT_DIR):
    subtotal = copy.deepcopy(blank)

    for jsonfile in os.listdir(os.path.join(OUTPUT_DIR, folder)):
        with open(os.path.join(OUTPUT_DIR, folder, jsonfile)) as jsonfp:
            for activity_json in json.load(jsonfp):
                dict_sum_inplace(subtotal, activity_json)

    publisher_stats = stats.PublisherStats(subtotal)
    for name, function in inspect.getmembers(publisher_stats, predicate=inspect.ismethod):
        if name.startswith('_'): continue
        subtotal[name] = function()

    dict_sum_inplace(total, subtotal)
    with open(os.path.join('aggregated', folder+'.json'), 'w') as fp:
        json.dump(subtotal, fp, sort_keys=True, indent=2)

with open('aggregated.json', 'w') as fp:
    json.dump(total, fp, sort_keys=True, indent=2)

