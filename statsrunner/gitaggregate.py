from collections import defaultdict
from common import decimal_default
import decimal
import json
import os 
import sys

# Set value for the gitout directory
GITOUT_DIR = os.environ.get('GITOUT_DIR') or 'gitout'

# Set bool if the 'dated' argument has been used in calling this script
dated = len(sys.argv) > 1 and sys.argv[1] == 'dated'

git_out_dir = os.path.join(GITOUT_DIR, 'gitaggregate-dated' if dated else 'gitaggregate')

# Exclude some json stats files from being aggregated
# These are typically the largest stats files that would consume large amounts of 
# memory/disk space if aggregated over time
whitelisted_stats_files = [
    'activities',
    'activity_files',
    'file_size_bins',
    'file_size',
    'invalidxml',
    'nonstandardroots',
    'organisation_files',
    'publisher_has_org_file',
    'publishers_per_version',
    'publishers',
    'publishers_validation',
    'unique_identifiers',
    'validation',
    'versions'
    ]

# Load the reference of commits to dates 
if dated:
    gitdates = json.load(open('gitdate.json'))

# Make the gitout directory
try:
    os.makedirs(git_out_dir)
except OSError:
    pass

# Get a list containing the names of the entries in the directory
git_out_files = os.listdir(git_out_dir)

# Loop over each commit in gitout/commits
for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    print 'Aggregating for commit: {}'.format(commit)

    for fname in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated')):
        if not fname.endswith('.json'):
            continue
        
        k = fname[:-5] # remove '.json' from the filename
        # Ignore certain files
        if k not in whitelisted_stats_files:
           continue

        print 'Adding to {} for file: {}'.format('gitaggregate-dated' if dated else 'gitaggregate', fname)
        
        commit_json_fname = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated', fname)
        
        # Load the current file conents to memory, or set as an empty dictionary
        if fname in git_out_files:
            # FIXME: This is a possible cause of a memory issue in future, as the size of the aggregate file 
            #        increases each time there is a new commit
            with open(os.path.join(git_out_dir, fname)) as fp:
                v = json.load(fp, parse_float=decimal.Decimal)
        else:
            v = {}
        
        # If the commit that we are looping over is not already in the data for this file, then add it to the output
        if not commit in v:
            with open(commit_json_fname) as fp2:
                v2 = json.load(fp2, parse_float=decimal.Decimal)
                if dated:
                    if commit in gitdates:
                        v[gitdates[commit]] = v2
                else:
                    v[commit] = v2

            # Write output to a temporary file, then rename
            with open(os.path.join(git_out_dir, k+'.json.new'), 'w') as fp:
                print 'Writing data to {}'.format(k)
                json.dump(v, fp, sort_keys=True, indent=2, default=decimal_default)
            print 'Renaming file {} to {}'.format(k+'.json.new', k+'.json')
            os.rename(os.path.join(git_out_dir, k+'.json.new'), os.path.join(git_out_dir, k+'.json'))
