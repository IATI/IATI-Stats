import os
from lxml import etree
import inspect
import json
import sys

from settings import *

if len(sys.argv) > 1:
    debug = sys.argv[1] == '--debug'
else:
    debug = False

import stats

def process_file(inputfile, outputfile):
    try:
        root = etree.parse(inputfile).getroot()
        if root.tag == 'iati-activities':
            out = []
            for activity in root:
                activity_out = {}
                activity_stats = stats.ActivityStats(activity)
                activity_stats.context = 'in '+inputfile
                for name, function in inspect.getmembers(activity_stats, predicate=inspect.ismethod):
                    if name.startswith('_'): continue
                    activity_out[name] = function()
                if debug:
                    print activity_out
                out.append(activity_out)
            with open(outputfile, 'w') as outfp:
                json.dump(out, outfp, sort_keys=True, indent=2)
        else:
            print 'No support yet for {0} in {1}'.format(root.tag, inputfile)
    except etree.ParseError:
        print 'Could not parse file {0}'.format(inputfile)

for folder in os.listdir(DATA_DIR):
    if not os.path.isdir(os.path.join(DATA_DIR, folder)) or folder == '.git':
        continue
    for xmlfile in os.listdir(os.path.join(DATA_DIR, folder)):
        try: os.makedirs(os.path.join(OUTPUT_DIR,folder))
        except OSError: pass
        process_file(os.path.join(DATA_DIR,folder,xmlfile),
                     os.path.join(OUTPUT_DIR,folder,xmlfile))

