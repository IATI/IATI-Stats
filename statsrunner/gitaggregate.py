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
# These are typically the largest stats files that would consume large amounts
# of memory/disk space if aggregated over time
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
    'versions',
    'teststat'  # Extra 'stat' added as the test_gitaggregate.py assumes a file with this name is present
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


def get_json_commit_for_file(commit, fname):
    """Get json file for the commit."""
    commit_json_fname = os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated', fname)
    return commit_json_fname


def write_output(trimmed_fname, gitaggregate_file, git_out_dir):
    """Write output to a temporary file, then rename."""
    new_json = '{}.json.new'.format(trimmed_fname)
    with open(os.path.join(git_out_dir, new_json), 'w') as filepath:
        print 'Writing data to {}'.format(trimmed_fname)
        json.dump(gitaggregate_file, filepath, sort_keys=True, indent=2, default=decimal_default)
    print 'Renaming file {} to {}'.format(new_json, trimmed_fname + '.json')
    os.rename(os.path.join(git_out_dir, new_json), os.path.join(git_out_dir, trimmed_fname + '.json'))


def file_loop(commit, fname, whitelisted, dated, git_out_dir):
    """Write through each file in the commit."""
    if fname.endswith('.json'):
        trimmed_fname = fname[:-5]  # remove '.json' from the filename
    if trimmed_fname not in whitelisted:
        commit_json_fname = get_json_commit_for_file(commit, fname, gitoutdir)
    # Load the current file contents to memory, or set as an empty dictionary
    if fname in git_out_files:
        # FIXME: This is a possible cause of a memory issue in future, as the size of the aggregate file
        #        increases each time there is a new commit
        with open(os.path.join(git_out_dir, fname)) as filepath:
            gitaggregate_file = json.load(filepath, parse_float=decimal.Decimal)
    else:
        gitaggregate_file = {}
    # If the commit that we are looping over is not already in the data for this file, then add it to the output
    if commit not in gitaggregate_file:
        with open(commit_json_fname) as filepath:
            commit_file = json.load(filepath, parse_float=decimal.Decimal)
            if dated:
                if commit in gitdates:
                    gitaggregate_file[gitdates[commit]] = commit_file
            else:
                gitaggregate_file[commit] = commit_file
        write_output(trimmed_fname, gitaggregate_file, git_out_dir)
    return


# Loop over each commit in gitout/commits
for commit in os.listdir(os.path.join(GITOUT_DIR, 'commits')):
    print 'Aggregating for commit: {}'.format(commit)
    for fname in os.listdir(os.path.join(GITOUT_DIR, 'commits', commit, 'aggregated')):
        print 'Adding to {} for file: {}'.format('gitaggregate-dated' if dated else 'gitaggregate', fname)
        file_loop(commit, fname, whitelisted_stats_files, dated, git_out_dir)
