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
commits=`git log --format=format:%H`
cd .. || exit $?

for commit in $commits; do
    if [ ! -e ../gitout/commits/$commit ]; then
        cd data || exit $?
        git checkout $commit
        git clean -df
        echo $commit;
        cd .. || exit $?
        python calculate_stats.py $@ loop
        python calculate_stats.py $@ aggregate
        python calculate_stats.py $@ invert
        mkdir -p gitout/commits/$commit
        mv out/aggregated* out/inverted* gitout/commits/$commit || exit $?
        rm -r out
    fi
done

python statsrunner/gitaggregate.py
python statsrunner/gitaggregate.py dated
mv gitdate.json gitout
cp helpers/ckan.json gitout

cd gitout || exit $?
rm -r current
cp -r commits/$current_hash current
tar -czf current.tar.gz current

