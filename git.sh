#!/bin/bash
set -eux
# ^ https://explainshell.com/explain?cmd=set+-eux

GIT_DATA_DIR="iati-data"

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Starting Stats generation"
if [ ! -v GITOUT_DIR ]; then
    GITOUT_DIR="gitout"
fi
if [ ! -v COMMIT_SKIP_FILE ]; then
    COMMIT_SKIP_FILE=$GITOUT_DIR/commits_run.txt
fi

# Make the all the gitout directories
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Making gitout directories"
mkdir -p $GITOUT_DIR/logs
mkdir -p $GITOUT_DIR/commits
mkdir -p $GITOUT_DIR/gitaggregate-dated



cd helpers
# Update codelist mapping, codelists and schemas
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelist mapping"
./get_codelist_mapping.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelists"
./get_codelists.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update schemas"
./get_schemas.sh

wget -q https://raw.githubusercontent.com/IATI/IATI-Dashboard/live/registry_id_relationships.csv -O registry_id_relationships.csv
wget -q https://codeforiati.org/imf-exchangerates/imf_exchangerates_A_ENDA_USD.csv -O currency_conversion/exchange_rates.csv

cd ..


# Clear output directory
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Clearing output directory"
rm -r out || true

if [ ! -d $GIT_DATA_DIR/.git ]; then
    set +x
    echo "'$GIT_DATA_DIR' is not a git repository, exiting."
    exit
fi

# Bring the IATI raw data up-to-date
# This is now done outside this script/repo - the data directory should be made up to date by the server
cd $GIT_DATA_DIR
# However we leave the cd in so the rest of the script is in the directory it expects to be

# Create a gitdate file in JSON format. This contains the git hash and date for each data commit
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating gitdate file"
echo '{' > gitdate.json
git log --format="format:%H|%ai" | awk -F '|' '{ print "\""$1"\": \""$2"\"," } ' >> gitdate.json
# Ensure the last line doesn't have a trailing comma
#
sed -i '$d' gitdate.json
git log --format="format:%H|%ai" | tail -n1 | awk -F '|' '{ print "\""$1"\": \""$2"\"" } ' >> gitdate.json
echo '}' >> gitdate.json
# Perform this dance because piping to ../ behaves differently with symlinks
cd ..
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Move and copy gitdate file"
mv $GIT_DATA_DIR/gitdate.json .
cp gitdate.json $GITOUT_DIR


# Store current and all commit hashes as variables
cd $GIT_DATA_DIR
# Get the latest commit hash
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Storing git info as bash variables"
current_hash=`git rev-parse HEAD`
# Get all commit hashes
commits=`git log --format=format:%H`
cd ..


# Loop over commits and run stats code
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Looping over commits"
for commit in $commits; do
    if grep -q $commit $COMMIT_SKIP_FILE; then
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Skipping $commit (due to grep conditional)"
    elif [ -v GITOUT_SKIP_INCOMMITSDIR ] && [ -d $GITOUT_DIR/commits/$commit ]; then
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Skipping $commit (due to git skip conditionals)"
    else
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running stats code for commit: $commit"

        # Get the data to the specified commit
        cd $GIT_DATA_DIR
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Checking out commit $commit"
        git checkout $commit
        git clean -df

        commit_date=`git log --format="format:%ai" | head -n 1`
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Set commit date as $commit_date"
        cd ..

        if [ -d "$GIT_DATA_DIR/datasets" ]; then
            # If the data in this commit has come from the bulk data service (mid 2025 and later)
            git_dataset_dir="$GIT_DATA_DIR/datasets"
            reporting_orgs_metadata="$GIT_DATA_DIR/reporting-orgs.json"
        else
            # If the data in this commit has come from IATI-Registry-Refresher (mid 2025 and earlier)
            git_dataset_dir="$GIT_DATA_DIR"
            reporting_orgs_metadata=""
        fi

        # Run the stats commands and save output to log files
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (loop) for commit $commit"
        python calculate_stats.py $@ --today "$commit_date" loop --data "$git_dataset_dir" > $GITOUT_DIR/logs/${commit}_loop.log
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (aggregate) for commit $commit"
        python calculate_stats.py $@ --today "$commit_date" aggregate --reporting-orgs-metadata "$reporting_orgs_metadata" > $GITOUT_DIR/logs/${commit}_aggregate.log
        if [ $commit = $current_hash ]; then
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Calculating stats (invert) for commit $commit"
            python calculate_stats.py $@ --today "$commit_date" invert > $GITOUT_DIR/logs/${commit}_invert.log
        fi

        mkdir out/bulk-data-service-metadata/
        cp -r iati-data/*.json out/bulk-data-service-metadata/

        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing output for commit dir: $commit"
        rm -r $GITOUT_DIR/commits/$commit || true
        mv out $GITOUT_DIR/commits/$commit

        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate.py dated for commit: $commit"
        python statsrunner/gitaggregate.py dated
        echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Running gitaggregate-publisher.py dated for commit: $commit"
        python statsrunner/gitaggregate-publisher.py dated
        echo "$commit" >> $COMMIT_SKIP_FILE
        # If the commit is the latest commit then, move the resulting stats to the 'current' directory
        if [ ! $commit = $current_hash ]; then
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing commit dir (based on latest commit logic) for commit: $commit"
            rm -r $GITOUT_DIR/commits/$commit
        else
            cd $GITOUT_DIR
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Removing current dir for commit: $commit"
            rm -r current || true
            # Since we're not currently creating symlinks, we can just do a plain move here
            mv commits/$current_hash current
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating current.tar.gz for commit: $commit"
            tar -czf current.tar.gz current
            cd ..
        fi
        if [ ! -v ALL_COMMITS ]; then
            echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Breaking out of commit logic for commit: $commit"
            break
        fi
    fi
done

cd $GITOUT_DIR
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate-dated"
tar -czf gitaggregate-dated.tar.gz gitaggregate-dated
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Creating compressed file: gitaggregate-publisher-dated"
tar -czf gitaggregate-publisher-dated.tar.gz gitaggregate-publisher-dated
