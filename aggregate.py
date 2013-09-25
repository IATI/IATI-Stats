from settings import *
import inspect
import json
import os

def dict_sum_inplace(d1, d2):
    for k,v in d2.items():
        if type(v) == dict:
            dict_sum_inplace(d1[k], v)
        elif d1[k] is None:
            continue
        else:
            d1[k] += v

total = {}
import stats
activity_stats = stats.ActivityStats()
for name, function in inspect.getmembers(activity_stats, predicate=inspect.ismethod):
    if name.startswith('_'): continue
    total[name] = function()

for folder in os.listdir(OUTPUT_DIR):
    for jsonfile in os.listdir(os.path.join(OUTPUT_DIR, folder)):
        with open(os.path.join(OUTPUT_DIR, folder, jsonfile)) as jsonfp:
            for activity_json in json.load(jsonfp):
                dict_sum_inplace(total, activity_json)

print json.dumps(total, sort_keys=True, indent=2)

