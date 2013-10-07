import os
from lxml import etree
import inspect
import json
import sys
import decimal
import argparse

from settings import *

parser = argparse.ArgumentParser()
parser.add_argument("--debug", help="Output extra debugging information",
                    action="store_true")
parser.add_argument("--strict", help="Follow the schema strictly",
                    action="store_true")
parser.add_argument("--stat", help="Name of stat to calculate")
parser.add_argument("--folder", help="Limit to a specific folder in the data")
args = parser.parse_args()

import stats

def decimal_default(obj):
    if isinstance(obj, decimal.Decimal):
        return float(obj)
    raise TypeError

def call_stats(this_stats):
    this_out = {}
    if args.stat:
        this_out[args.stat] = getattr(this_stats, args.stat)()
    else:
        for name, function in inspect.getmembers(this_stats, predicate=inspect.ismethod):
            if name.startswith('_'): continue
            this_out[name] = function()
    if args.debug:
        print this_out
    return this_out

def process_file(inputfile, outputfile):
    try:
        root = etree.parse(inputfile).getroot()
        if root.tag == 'iati-activities':
            activity_file_stats = stats.ActivityFileStats(root)
            activity_file_stats.strict = args.strict
            activity_file_stats.context = 'in '+inputfile
            file_out = call_stats(activity_file_stats)
            out = []
            for activity in root:
                activity_stats = stats.ActivityStats(activity)
                activity_stats.strict = args.strict
                activity_stats.context = 'in '+inputfile
                activity_out = call_stats(activity_stats)
                out.append(activity_out)
            with open(outputfile, 'w') as outfp:
                json.dump({'file':file_out, 'activities':out}, outfp, sort_keys=True, indent=2, default=decimal_default)
        else:
            print 'No support yet for {0} in {1}'.format(root.tag, inputfile)
    except etree.ParseError:
        print 'Could not parse file {0}'.format(inputfile)

def loop_folder(folder):
    if not os.path.isdir(os.path.join(DATA_DIR, folder)) or folder == '.git':
        return
    for xmlfile in os.listdir(os.path.join(DATA_DIR, folder)):
        try: os.makedirs(os.path.join(OUTPUT_DIR,folder))
        except OSError: pass
        process_file(os.path.join(DATA_DIR,folder,xmlfile),
                     os.path.join(OUTPUT_DIR,folder,xmlfile))

if __name__ == '__main__':
    if args.folder:
        loop_folder(args.folder)
    else:
        for folder in os.listdir(DATA_DIR):
            loop_folder(folder)

