import json, os, sys
from collections import defaultdict
import decimal
from common import decimal_default

GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'gitout'

# Only aggregate certain json stats files at publisher level 
# These should be small stats files that will not consume large amounts of 
# memory/disk space if aggregated over time
whitelisted_stats_files - [ 
    'activities',
    'activity_files',
    'bottom_hierarchy',
    'empty',
    'invalidxml',
    'file_size',
    'nonstandardroots',
    'organisation_files',
    'publisher_unique_identifiers',
    'toolarge',
    'validation',
    'versions',
    'activities_with_future_transactions',
    'latest_transaction_date',
    'transaction_dates_hash',
    'most_recent_transaction_date'
    ]

dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'
if dated:
    gitdates = json.load(open('gitdate.json'))


for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    for publisher in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated-publisher')):
        git_out_dir = os.path.join(GITOUT_DIR,'gitaggregate-publisher-dated' if dated else 'gitaggregate-publisher', publisher)
        try:
            os.makedirs(git_out_dir)
        except OSError:
            pass
        total = defaultdict(dict)
        if os.path.isdir(git_out_dir):
            for fname in os.listdir(git_out_dir):
                if fname.endswith('.json'):
                    with open(os.path.join(git_out_dir, fname)) as fp:
                        total[fname[:-5]] = json.load(fp, parse_float=decimal.Decimal)

        for statname in whitelisted_stats_files:
            path = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated-publisher', publisher, statname+'.json')
            if os.path.isfile(path):
                with open(path) as fp:
                    k = statname
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
