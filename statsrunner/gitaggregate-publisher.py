import datetime
import decimal
import json
import os
import sys

from collections import defaultdict
from common import decimal_default

GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'gitout'

# Only aggregate certain json stats files at publisher level
# These should be small stats files that will not consume large amounts of
# memory/disk space if aggregated over time
whitelisted_stats_files = [
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

# Set bool if the 'dated' argument has been used in calling this script
dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'
if dated:
    gitdates = json.load(open('gitdate.json'))

def publisher_loop(publisher, commit, whitelisted, dated, gitdates, GITOUT_DIR):
    """Loop over publishers."""
    # Load the reference of commits to dates
    git_out_dir = os.path.join(GITOUT_DIR, 'gitaggregate-publisher-dated' if dated else 'gitaggregate-publisher', publisher)
    try:
        os.makedirs(git_out_dir)
    except OSError:
        pass

    total = total_loop(publisher, git_out_dir, whitelisted, commit, gitdates, GITOUT_DIR)

    for statname, stat_json in total.items():
        new_json_file = '{}.json.new'.format(statname)
        with open(os.path.join(git_out_dir, new_json_file), 'w') as filepath:
            json.dump(stat_json, filepath, sort_keys=True, indent=2, default=decimal_default)
        os.rename(os.path.join(git_out_dir, new_json_file), os.path.join(git_out_dir, new_json_file))


def total_loop(publisher, git_out_dir, whitelisted, commit, gitdates, GITOUT_DIR):
    """Loop over the existing files in the output directory for this publisher and load them into the 'total' dictionary."""
    total = defaultdict(dict)
    if os.path.isdir(git_out_dir):
        for fname in os.listdir(git_out_dir):
            if fname.endswith('.json'):
                with open(os.path.join(git_out_dir, fname)) as filepath:
                    total[fname[:-5]] = json.load(filepath, parse_float=decimal.Decimal)
    for statname in whitelisted:
        stat_json = whitelisted_stats(statname, publisher, commit, GITOUT_DIR)
        if dated:
            if commit in gitdates:
                total[statname][gitdates[commit]] = stat_json
            else:
                total[statname][commit] = stat_json
    return total


def whitelisted_stats(total, statname, commit, GITOUT_DIR):
    """Load specified stat json file for a publisher."""
    path = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated-publisher', publisher, '{}.json'.format(statname))
    if os.path.isfile(path):
        with open(path) as filepath:
            if commit not in total[statname]:
                return json.load(filepath, parse_float=decimal.Decimal)


# Loop over folders in the 'commits' directory
# Variable commit will be the commit hash
for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    print "gitaggregate-publisher for commit {}".format(commit)

    for publisher in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated-publisher')):
        print "{0} Currently looping over publisher {1}".format(str(datetime.datetime.now()), publisher)
        publisher_loop(publisher, commit, whitelisted_stats_files, dated, gitdates, GITOUT_DIR)
