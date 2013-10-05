#!/bin/bash
cd data or exit
echo '{' > gitdate.json
git log --format="format:%H|%ai" | awk -F '|' '{ print "\""$1"\": \""$2"\"," } ' >> gitdate.json
echo '}' >> gitdate.json
# Perform this dance because piping to ../ behaves differently with symlinks
cd ..
mv data/gitdate.json gitout
