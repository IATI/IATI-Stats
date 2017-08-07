#!/usr/bin/env bash

for x in 105 202; do
    i=$(echo $x | head -c 1)
    mkdir -p codelists/$i
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Version.json" -O codelists/$i/Version.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/ActivityStatus.json" -O codelists/$i/ActivityStatus.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Currency.json" -O codelists/$i/Currency.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/Sector.json" -O codelists/$i/Sector.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/SectorCategory.json" -O codelists/$i/SectorCategory.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/DocumentCategory.json" -O codelists/$i/DocumentCategory.json
    wget "http://iatistandard.org/$x/codelists/downloads/clv2/json/en/AidType.json" -O codelists/$i/AidType.json
done
