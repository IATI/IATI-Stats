# Script to provide currency conversion functionality
# Current source of the exchange rate values is: https://docs.google.com/spreadsheets/d/1jpXHDNmJ1WPdrkidEle0Ig13zLlXw4eV6WkbSy6kWk4/edit#gid=13

# @todo Use IMF currency rates by date, using data here: http://www.imf.org/external/np/fin/ert/GUI/Pages/CountryDataBase.aspx

import csv
import datetime
import os
from decimal import Decimal

# Open exchange rate data and import into a dictionary
fname = os.path.join(os.path.dirname(__file__), 'exchange_rates.csv')
reader = csv.DictReader(open(fname, 'r'), delimiter=',')
columns = reader.fieldnames

# Set up default output structure
currency_values = {}
for currency in columns:
    currency_values[currency] = {}

# Loop over the exchange rate data to put it in a dictionary
for row in reader:
    year = int(row['year'])
    del row['year']

    for currency, value in row.iteritems():
    	if value == '':
    		value = 0
        currency_values[currency][year] = float(value)


def get_USD_value(input_currency, input_value, year):
    """ Returns a USD value based on an inputted ISO currency, an inputted value and a year """

    try:
        usd_value = (1 / currency_values[input_currency][int(year)]) * float(input_value)
    except KeyError:
        usd_value = 0

    return Decimal(usd_value)
