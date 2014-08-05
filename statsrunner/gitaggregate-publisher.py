import json, os, sys
from collections import defaultdict
import decimal

dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'
if dated:
    gitdates = json.load(open('gitdate.json'))


for commit in os.listdir(os.path.join('gitout', 'commits')):
    for publisher in ['dfid']:#FIXME os.listdir(os.path.join('gitout', 'commits', commit, 'aggregated-publisher')):
        git_out_dir = os.path.join('gitout','gitaggregate-publisher-dated' if dated else 'gitaggregate-publisher', publisher)
        total = defaultdict(dict)
        if os.path.isdir(git_out_dir):
            for fname in os.listdir(git_out_dir):
                if fname.endswith('.json'):
                    with open(os.path.join(git_out_dir, fname)) as fp:
                        total[fname[:-5]] = json.load(fp, parse_float=decimal.Decimal)

        for statname in [ 'activities', 'activity_files', 'annualreport', 'empty', 'invalidxml', 'file_size', 'nonstandardroots', 'organisation_files', 'publisher_unique_identifiers', 'toolarge', 'validation', 'versions', # Whitelist small stats to avoid using too much diskspace
                'latest_transaction_date', 'transaction_dates_hash', 'most_recent_transaction_date' ]: # Only run for stats/transaction_dates.py
            path = os.path.join('gitout', 'commits', commit, 'aggregated-publisher', publisher, statname+'.json')
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

        try:
            os.makedirs(git_out_dir)
        except OSError:
            pass

        for k,v in total.items():
            with open(os.path.join(git_out_dir, k+'.json'), 'w') as fp:
                json.dump(v, fp, sort_keys=True, indent=2)
