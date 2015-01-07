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

git_out_files = os.listdir(git_out_dir)

for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    print commit
    for fname in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated')):
        if not fname.endswith('.json'):
            continue
        k = fname[:-5]
        if k in ['codelist_values','iati_identifiers','duplicate_identifiers','publisher_duplicate_identifiers', 'participating_orgs_text','transaction_dates']:
           continue
        print fname
        commit_json_fname = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated', fname)
        if fname in git_out_files:
            with open(os.path.join(git_out_dir, fname)) as fp:
                v = json.load(fp, parse_float=decimal.Decimal)
        else:
            v = {}
        if not commit in v:
            with open(commit_json_fname) as fp2:
                v2 = json.load(fp2, parse_float=decimal.Decimal)
                if dated:
                    if commit in gitdates:
                        v[gitdates[commit]] = v2
                else:
                    v[commit] = v2

            with open(os.path.join(git_out_dir, k+'.json.new'), 'w') as fp:
                json.dump(v, fp, sort_keys=True, indent=2, default=decimal_default)
            os.rename(os.path.join(git_out_dir, k+'.json.new'), os.path.join(git_out_dir, k+'.json'))
