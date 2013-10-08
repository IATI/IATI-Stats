#!/bin/bash

rm -r out
cd gitout || exit $?
git rm -r *
rm -rf *
cd .. || exit $?
rm -r aggregated* inverted* out*
cd data || exit $?
git checkout master
git reset --hard
git clean -df
git pull --ff-only
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
./gitdate.sh
cp -r html gitout
rm gitout/html/gitout
ln -s .. gitout/html/gitout

cd gitout
git add .
git commit -a -m 'Auto'
