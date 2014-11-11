#!/bin/bash

echo $GITOUT_DIR
if [ "$GITOUT_DIR" = "" ]; then
    GITOUT_DIR="gitout"
fi
if [ "$COMMIT_SKIP_FILE" = "" ]; then
    COMMIT_SKIP_FILE=$GITOUT_DIR/gitaggregate/activities.json
fi

cd helpers
python ckan.py
cd ..

# Clear output directory
rm -r out

cd data || exit $?
# Checkout automatic, and make sure it is clean and up to date
git checkout automatic
git reset --hard
git clean -df
git pull --ff-only

# Create gitdate file
echo '{' > gitdate.json
git log --format="format:%H|%ai" | awk -F '|' '{ print "\""$1"\": \""$2"\"," } ' >> gitdate.json
# Ensure the last line doesn't have a trailing comma
sed -i '$d' gitdate.json
git log --format="format:%H|%ai" | tail -n1 | awk -F '|' '{ print "\""$1"\": \""$2"\"" } ' >> gitdate.json
echo '}' >> gitdate.json
# Perform this dance because piping to ../ behaves differently with symlinks
cd .. || exit $?
mv data/gitdate.json .

cd data || exit $?
current_hash=`git rev-parse HEAD`
commits=`git log --format=format:%H`
cd .. || exit $?

for commit in $commits; do
    if grep -q $commit $COMMIT_SKIP_FILE; then
        echo Skipping $commit
    elif [ $GITOUT_SKIP_INCOMMITSDIR ] && [ -d $GITOUT_DIR/commits/$commit ]; then
        echo Skipping $commit
    else
        cd data || exit $?
        git checkout $commit
        git clean -df
        echo $commit;
        commit_date=`git log --format="format:%ai" | head -n 1`
        cd .. || exit $?
        # Disable this because it doesn't work for date dependent stuff.........
        #mkdir -p $GITOUT_DIR/hash
        #python statsrunner/hashlink.py || exit 1
        python calculate_stats.py $@ --today "$commit_date" loop || exit 1 #--new || exit 1
        python calculate_stats.py $@ --today "$commit_date" aggregate || exit 1
        python calculate_stats.py $@ --today "$commit_date" invert
        #python statsrunner/hashcopy.py || exit 1
        rm -r $GITOUT_DIR/commits/$commit
        mkdir -p $GITOUT_DIR/commits/$commit
        mv out/aggregated* out/inverted* $GITOUT_DIR/commits/$commit || exit $?
        rm -r out
    fi
done

cd $GITOUT_DIR || exit $?
if [ -d commits/$current_hash ]; then
    rm -r current
    cp -Lr commits/$current_hash current
    #find current | grep iati_identifiers | xargs rm
    tar -czf current.tar.gz current
fi
find commits | grep iati_identifiers | xargs rm
cd .. || exit $?

mkdir -p $GITOUT_DIR/gitaggregate
mkdir -p $GITOUT_DIR/gitaggregate-dated
python statsrunner/gitaggregate.py
python statsrunner/gitaggregate.py dated
python statsrunner/gitaggregate-publisher.py
python statsrunner/gitaggregate-publisher.py dated
mv gitdate.json $GITOUT_DIR
cp helpers/ckan.json $GITOUT_DIR

cd $GITOUT_DIR || exit $?
tar -czf gitaggregate.tar.gz gitaggregate
tar -czf gitaggregate-dated.tar.gz gitaggregate-dated
tar -czf gitaggregate-publisher.tar.gz gitaggregate-publisher
tar -czf gitaggregate-publisher-dated.tar.gz gitaggregate-publisher-dated

