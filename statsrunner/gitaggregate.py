import json, os, sys
from collections import defaultdict
import decimal
from common import decimal_default

GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'gitout'

dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'
git_out_dir = os.path.join(GITOUT_DIR, 'gitaggregate-dated' if dated else 'gitaggregate')
if dated:
    gitdates = json.load(open('gitdate.json'))

try:
    os.makedirs(git_out_dir)
except OSError:
    pass

total = defaultdict(dict)
for fname in os.listdir(git_out_dir):
    if fname.endswith('.json'):
        print fname
        with open(os.path.join(git_out_dir, fname)) as fp:
            total[fname[:-5]] = json.load(fp, parse_float=decimal.Decimal)

for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    for fname in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated')):
        if fname.endswith('.json'):
            with open(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated', fname)) as fp:
                k = fname[:-5]
                if k in ['codelist_values','duplicate_identifiers','publisher_duplicate_identifiers', 'participating_orgs_text','transaction_dates']:
                   continue
                if not commit in total[k]:
                    v = json.load(fp, parse_float=decimal.Decimal)
                    if dated:
                        if commit in gitdates:
                            total[k][gitdates[commit]] = v
                    else:
                        total[k][commit] = v

for k,v in total.items():
    with open(os.path.join(git_out_dir, k+'.json.new'), 'w') as fp:
        json.dump(v, fp, sort_keys=True, indent=2, default=decimal_default)
    os.rename(os.path.join(git_out_dir, k+'.json.new'), os.path.join(git_out_dir, k+'.json'))
