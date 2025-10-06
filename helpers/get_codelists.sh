#!/usr/bin/env bash

mkdir -p codelists/1
mkdir -p codelists/2

for codelist in \
    ActivityDateType \
    ActivityScope \
    ActivityStatus \
    AidType \
    AidTypeFlag \
    AidTypeVocabulary \
    BudgetIdentifier \
    BudgetIdentifierVocabulary \
    BudgetNotProvided \
    BudgetStatus \
    BudgetType \
    CRSAddOtherFlags \
    CRSChannelCode \
    CashandVoucherModalities \
    CollaborationType \
    ConditionType \
    ContactType \
    Country \
    Currency \
    DescriptionType \
    DisbursementChannel \
    DocumentCategory \
    EarmarkingCategory \
    FileFormat \
    FinanceType \
    FlowType \
    GazetteerAgency \
    GeographicExactness \
    GeographicLocationClass \
    GeographicLocationReach \
    GeographicVocabulary \
    GeographicalPrecision \
    HumanitarianScopeType \
    HumanitarianScopeVocabulary \
    IndicatorMeasure \
    IndicatorVocabulary \
    Language \
    LoanRepaymentPeriod \
    LoanRepaymentType \
    LocationType \
    OrganisationRegistrationAgency \
    OrganisationRole \
    OrganisationType \
    OtherIdentifierType \
    PolicyMarker \
    PolicyMarkerVocabulary \
    PolicySignificance \
    Region \
    RegionVocabulary \
    RelatedActivityType \
    ResultType \
    ResultVocabulary \
    Sector \
    SectorCategory \
    SectorVocabulary \
    TagVocabulary \
    TiedStatus \
    TransactionType \
    UNSDG-Goals \
    UNSDG-Targets \
    Version \
    Vocabulary
do
    wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/105/codelists/downloads/clv3/json/en/$codelist.json" -O codelists/1/$codelist.json
    wget --tries=20 --waitretry=10 --retry-connrefused "https://iatistandard.org/reference_downloads/203/codelists/downloads/clv3/json/en/$codelist.json" -O codelists/2/$codelist.json
done

# Remove codelists we couldn't download (usually because they only exist for 1 standard version)
find codelists -type f -empty -print -delete
