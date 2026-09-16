set -eux

cd helpers

echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelist mapping"
./get_codelist_mapping.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update codelists"
./get_codelists.sh
echo "LOG: `date '+%Y-%m-%d %H:%M:%S'` - Update schemas"
./get_schemas.sh

wget -q https://raw.githubusercontent.com/IATI/IATI-Dashboard/live/registry_id_relationships.csv -O registry_id_relationships.csv
wget -q https://codeforiati.org/imf-exchangerates/imf_exchangerates_A_ENDA_USD.csv -O currency_conversion/exchange_rates.csv
