#!/bin/bash

# Clear gitout
cd gitout || exit $?
git rm -r *
rm -rf *
cd .. || exit $?

# Clear other output directories
rm -r aggregated* inverted* out*

cd data || exit $?
# Checkout master, and make sure it is clean and up to date
git checkout master
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


for commit in `git log --format=format:%H`; do
    git checkout $commit
    git clean -df
    echo $commit;
    cd .. || exit $?
    mkdir aggregated
    python2 loop.py $@
    python2 aggregate.py
    python2 invert.py
    mkdir gitout/$commit
    mv aggregated* inverted* gitout/$commit || exit $?
    rm -r out
    cd data || exit $?
done

cd ..
python2 gitaggregate.py > gitout/gitaggregate.json
mv gitdate.json gitout
cp -r html gitout

cd gitout
git add .
git commit -a -m 'Auto'
