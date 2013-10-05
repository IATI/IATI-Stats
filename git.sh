#!/bin/bash

rm -r out
cd gitout || exit $?
git rm -r *
rm -rf *
cd ..
cd data || exit $?
git checkout master
git reset --hard
git clean -df
# git log --format="format:%H %ai"
for commit in `git log --format=format:%H`; do
    git checkout $commit
    git clean -df
    echo $commit;
    cd .. || exit $?
    mkdir aggregated
    python2 loop.py $@
    python2 aggregate.py
    python2 invert.py
    #python2
    mkdir gitout/$commit
    mv out aggregated* inverted* gitout/$commit || exit $?
    cd data || exit $?
done

cd ..
python2 gitaggregate.py > gitout/gitaggregate.json

cd gitout
git add .
git commit -a -m 'Auto'
