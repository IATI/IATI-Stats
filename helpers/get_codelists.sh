#!/usr/bin/env bash

mkdir -p codelists/1
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/Version.json" -O codelists/1/Version.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/ActivityStatus.json" -O codelists/1/ActivityStatus.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/Currency.json" -O codelists/1/Currency.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/Sector.json" -O codelists/1/Sector.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/SectorCategory.json" -O codelists/1/SectorCategory.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/DocumentCategory.json" -O codelists/1/DocumentCategory.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/AidType.json" -O codelists/1/AidType.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/BudgetNotProvided.json" -O codelists/1/BudgetNotProvided.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/OrganisationRegistrationAgency.json" -O codelists/1/OrganisationRegistrationAgency.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/CRSChannelCode.json" -O codelists/1/CRSChannelCode.json

mkdir -p codelists/2
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/Version.json" -O codelists/2/Version.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/ActivityStatus.json" -O codelists/2/ActivityStatus.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/Currency.json" -O codelists/2/Currency.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/Sector.json" -O codelists/2/Sector.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/SectorCategory.json" -O codelists/2/SectorCategory.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/DocumentCategory.json" -O codelists/2/DocumentCategory.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/AidType.json" -O codelists/2/AidType.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/BudgetNotProvided.json" -O codelists/2/BudgetNotProvided.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/OrganisationRegistrationAgency.json" -O codelists/2/OrganisationRegistrationAgency.json
wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/CRSChannelCode.json" -O codelists/2/CRSChannelCode.json
