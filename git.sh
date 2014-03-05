#!/bin/bash

# Clear gitout
##cd gitout || exit $?
##git rm -r *
##rm -rf *
##cd .. || exit $?

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

for commit in `git log --format=format:%H`; do
    if [ ! -e ../gitout/$commit ]; then
        git checkout $commit
        git clean -df
        echo $commit;
        cd .. || exit $?
        python calculate_stats.py loop $@
        python calculate_stats.py aggregate $@
        python calculate_stats.py invert $@
        mkdir gitout/$commit
        mv out/aggregated* out/inverted* gitout/$commit || exit $?
        rm -r out
        cd data || exit $?
    fi
done

cd ..
python statsrunner/gitaggregate.py > gitout/gitaggregate.json
python statsrunner/gitaggregate.py dated > gitout/gitaggregate-dated.json
mv gitdate.json gitout
cp helpers/ckan.json gitout

cd gitout || exit $?
rm -r current
cp -r $current_hash current
tar -czf current.tar.gz current

