import json, os
from collections import defaultdict

# FIXME should use decimal

total = defaultdict(dict)
for commit in os.listdir('gitout'):
    if len(commit) == 40: # all git commits should be this length
        for k,v in json.load(open(os.path.join('gitout', commit, 'aggregated.json'))).items():
            total[k][commit] = v
import sys
json.dump(total, sys.stdout, sort_keys=True, indent=2)
