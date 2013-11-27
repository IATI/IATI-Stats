import json, os, sys
from collections import defaultdict

dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'
if dated:
    gitdates = json.load(open('gitdate.json'))

# FIXME should use decimal
total = defaultdict(dict)
for commit in os.listdir('gitout'):
    if len(commit) == 40: # all git commits should be this length
        try:
            for k,v in json.load(open(os.path.join('gitout', commit, 'aggregated.json'))).items():
                if dated:
                    if commit in gitdates:
                        total[k][gitdates[commit]] = v
                else:
                    total[k][commit] = v
        except IOError:
            pass
json.dump(total, sys.stdout, sort_keys=True, indent=2)
